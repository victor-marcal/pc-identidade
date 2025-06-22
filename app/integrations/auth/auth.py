from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
import httpx
from jose import jwt, jwk
from jose.exceptions import JWTError
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# --- Configuração ---
KEYCLOAK_URL = "http://pc-identidade-keycloak:8080"
REALM_NAME = "marketplace"
CLIENT_ID = "varejo"

JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/certs"

_jwks_cache: Optional[Dict] = None

# Extracao do token do cabeçalho Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token")


class TokenData(BaseModel):
    """
    Modelo Pydantic para os dados extraídos do token.
    """
    preferred_username: str = Field(alias="preferred_username")
    sellers: List[str] = []
    sub: str  # Subject (ID do usuário no Keycloak)
    exp: int  # Expiration time


async def get_jwks() -> Dict:
    """
    Busca as chaves públicas (JWKS) do Keycloak.
    Implementa um cache simples para evitar requisições repetidas.
    """
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(JWKS_URL)
            response.raise_for_status()
            _jwks_cache = response.json()
            return _jwks_cache
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Não foi possível conectar ao serviço de autenticação."
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Dependência FastAPI para validar o token JWT e retornar os dados do usuário.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Obter a chave pública correta
        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break

        if not rsa_key:
            raise credentials_exception

        # 2. Decodificar e validar o token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=CLIENT_ID,  # Valida a audiência
            issuer=f"{KEYCLOAK_URL}/realms/{REALM_NAME}"  # Valida o emissor
        )

        # 3. Mapear o payload para o nosso modelo Pydantic
        # O claim 'sellers' pode ser uma string separada por vírgulas ou já uma lista
        # Por enquanto 'sellers' vai conter apenas uma informação, nã teremos usuários com mais de um 'seller'
        sellers_claim = payload.get("sellers", "")
        if isinstance(sellers_claim, str):
            sellers_list = [s.strip() for s in sellers_claim.split(',') if s.strip()]
        else:
            sellers_list = sellers_claim or []

        token_data = TokenData(
            preferred_username=payload.get("preferred_username", ""),
            sellers=sellers_list,
            sub=payload.get("sub"),
            exp=payload.get("exp")
        )

    except JWTError as e:
        raise credentials_exception

    return token_data


async def check_seller_permission(
    seller_id: str,
    current_user: TokenData = Depends(get_current_user)
) -> None:
    """
    Verifica se o seller_id está na lista de sellers permitidos para o usuário.
    Levanta uma exceção HTTP 403 (Forbidden) se não tiver permissão.
    """
    if seller_id not in current_user.sellers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Você não tem permissão para acessar o seller '{seller_id}'"
        )

