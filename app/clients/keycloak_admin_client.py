import httpx
from fastapi import HTTPException, status

from app.common.exceptions.bad_request_exception import BadRequestException
from app.settings.app import settings
import logging

logger = logging.getLogger(__name__)


class KeycloakAdminClient:
    def __init__(self):
        self.settings = settings
        self.base_url = f"{self.settings.KEYCLOAK_URL}/admin/realms/{self.settings.KEYCLOAK_REALM_NAME}"
        self.token_url = (
            f"{self.settings.KEYCLOAK_URL}/realms/{self.settings.KEYCLOAK_REALM_NAME}/protocol/openid-connect/token"
        )

    async def _get_admin_token(self) -> str:
        """
        Obtém um token de acesso com permissões de administrador.
        """
        logger.info("Obtendo token de administrador do Keycloak para operação interna.")
        token_data = {
            "grant_type": "password",
            "client_id": self.settings.KEYCLOAK_ADMIN_CLIENT_ID,
            "username": self.settings.KEYCLOAK_ADMIN_USER,
            "password": self.settings.KEYCLOAK_ADMIN_PASSWORD,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=token_data)
            response.raise_for_status()
            return response.json()["access_token"]

    async def create_user(self, username: str, email: str, password: str, seller_id: str) -> str:
        """
        Cria um novo usuário no Keycloak.
        """
        logger.info(f"Iniciando criação de usuário no Keycloak para o seller: {seller_id}")
        try:
            admin_token = await self._get_admin_token()
            headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}

            user_payload = {
                "username": username,
                "email": email,
                "firstName": username,
                "lastName": username,
                "enabled": True,
                "emailVerified": True,
                "credentials": [{"type": "password", "value": password, "temporary": False}],
                "attributes": {"sellers": [seller_id]},
                "realmRoles": ["offline_access", "uma_authorization"],
                "requiredActions": [],
            }

            users_url = f"{self.base_url}/users"
            async with httpx.AsyncClient() as client:
                response = await client.post(users_url, headers=headers, json=user_payload)

                if response.status_code == 409:
                    raise BadRequestException(message=f"Usuário '{username}' já existe no Keycloak.")

                response.raise_for_status()

                if response.status_code == 201:
                    location_header = response.headers.get("Location")
                    if not location_header:
                        raise Exception("Keycloak não retornou a localização do novo usuário.")

                    # Extrai o ID do usuário (sub) da URL
                    new_user_id = location_header.split("/")[-1]

                    # Constrói o identificador (iss+sub)
                    issuer = f"{self.settings.KEYCLOAK_URL}/realms/{self.settings.KEYCLOAK_REALM_NAME}"
                    return f"{issuer}:{new_user_id}"

                logger.error(f"Falha ao criar usuário '{username}' no Keycloak.", exc_info=True)
                raise Exception("Resposta inesperada do Keycloak ao criar usuário.")

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar usuário no Keycloak: {e.response.text}",
            )
