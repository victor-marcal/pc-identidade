import httpx
from fastapi import HTTPException, status

from app.common.exceptions.bad_request_exception import BadRequestException
from app.settings.app import settings


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

    async def create_user(self, username: str, email: str, password: str, seller_id: str):
        """
        Cria um novo usuário no Keycloak.
        """
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

                # Erro caso o usuário já exista
                if response.status_code == 409:
                    raise BadRequestException(message=f"Usuário '{username}' já existe no Keycloak.")

                response.raise_for_status()

        except httpx.HTTPStatusError as e:
            # Captura erros da API do Keycloak e os relança como exceções da aplicação
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar usuário no Keycloak: {e.response.text}",
            )
