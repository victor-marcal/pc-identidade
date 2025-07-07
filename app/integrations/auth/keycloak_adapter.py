import httpx
import jwt
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.integrations.kv_db.redis_asyncio_adapter import RedisAsyncioAdapter

logger = logging.getLogger(__name__)

# ----- Exceções -----


class OAuthException(Exception):
    """Exceção geral de autenticação"""


class TokenExpiredException(OAuthException):
    """Token expirou"""


class InvalidTokenException(OAuthException):
    """Token inválido"""


class KeycloakAdapter:
    def __init__(self, well_known_url: str, inmemory_adapter: "RedisAsyncioAdapter"):
        self.well_known_url = str(well_known_url)
        self.jwks_client = jwt.PyJWKClient(self._get_jwks_uri())
        self.inmemory_adapter = inmemory_adapter
        self.public_keys_cache_key = f"keycloak:public_keys:{self.well_known_url}"

    def _get_jwks_uri(self) -> str:
        """Busca o .well-known de forma síncrona no construtor."""
        with httpx.Client() as http_client:
            response = http_client.get(self.well_known_url)
            response.raise_for_status()
            return response.json()["jwks_uri"]

    async def validate_token(self, token: str) -> dict:
        try:
            try:
                signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            except jwt.exceptions.PyJWKClientError:
                logger.info("Chave não encontrada no cache local, buscando no Redis/HTTP...")
                await self._fetch_and_cache_keys()
                signing_key = self.jwks_client.get_signing_key_from_jwt(token)

            unverified_header = jwt.get_unverified_header(token)
            info_token = jwt.decode(
                token,
                signing_key.key,
                algorithms=[unverified_header.get("alg")],
                options={"verify_aud": False},
            )
            logger.info(f"Token validado com sucesso para o usuário sub: {info_token.get('sub')}")
            return info_token
        except jwt.ExpiredSignatureError as e:
            raise TokenExpiredException("Token expirou") from e
        except (jwt.InvalidTokenError, jwt.exceptions.DecodeError) as e:
            raise InvalidTokenException("Token inválido") from e
        except Exception as e:
            logger.error("Falha inesperada ao validar o token", exc_info=True)
            raise OAuthException("Falha inesperada ao validar o token") from e

    async def _fetch_and_cache_keys(self):
        """Busca chaves no Redis ou, em último caso, no Keycloak e as salva no cache."""
        cached_keys = await self.inmemory_adapter.get_json(self.public_keys_cache_key)
        if cached_keys:
            logger.debug("Chaves públicas carregadas do cache Redis.")
            self.jwks_client.jwk_set = cached_keys
            return

        # Se não estiver no Redis, busca no Keycloak
        logger.warning("Cache Redis vazio. Buscando chaves públicas diretamente do Keycloak.")
        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwks_client.uri)
            response.raise_for_status()
            jwk_set = response.json()
            # Salva no cache Redis com uma expiração (1 hora por enquanto, definir regra de negocio)
            await self.inmemory_adapter.set_json(self.public_keys_cache_key, jwk_set, expires_in_seconds=3600)
            self.jwks_client.jwk_set = jwk_set
