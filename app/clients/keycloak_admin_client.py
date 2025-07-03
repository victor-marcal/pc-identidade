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
            try:
                response = await client.post(self.token_url, data=token_data)
                response.raise_for_status()
                return response.json()["access_token"]
            except httpx.HTTPStatusError as e:
                logger.error(f"Erro ao obter token de admin: {e.response.text}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Falha ao autenticar com o Keycloak.")

    async def create_user(
            self, username: str, email: str, password: str, first_name: str | None, last_name: str | None,
            sellers: list[str]
    ) -> str:
        logger.info(f"Iniciando criação de usuário no Keycloak: {username}")
        admin_token = await self._get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}

        user_payload = {
            "username": username,
            "email": email,
            "firstName": first_name or '',
            "lastName": last_name or '',
            "enabled": True,
            "emailVerified": True,
            "credentials": [{"type": "password", "value": password, "temporary": False}],
            "attributes": {"sellers": sellers},
            "realmRoles": ["offline_access", "uma_authorization"],
            "requiredActions": [],
        }

        users_url = f"{self.base_url}/users"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(users_url, headers=headers, json=user_payload)
                if response.status_code == 409:
                    raise BadRequestException(message=f"Usuário '{username}' já existe.")
                response.raise_for_status()
                location_header = response.headers.get("Location")
                if not location_header:
                    raise Exception("Keycloak não retornou a localização do novo usuário.")
                return location_header.split("/")[-1]
            except httpx.HTTPStatusError as e:
                logger.error(f"Erro ao criar usuário no Keycloak: {e.response.text}")
                raise HTTPException(status_code=e.response.status_code, detail=f"Erro no Keycloak: {e.response.text}")

    async def get_user(self, user_id: str) -> dict | None:
        logger.debug(f"Buscando usuário por ID: {user_id}")
        admin_token = await self._get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_url = f"{self.base_url}/users/{user_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(user_url, headers=headers)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()

    async def get_users(self) -> list[dict]:
        logger.debug("Listando todos os usuários.")
        admin_token = await self._get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        users_url = f"{self.base_url}/users"
        async with httpx.AsyncClient() as client:
            response = await client.get(users_url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def update_user_attributes(self, user_id: str, attributes: dict):
        logger.info(f"Atualizando atributos para o usuário ID: {user_id}")
        admin_token = await self._get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        user_url = f"{self.base_url}/users/{user_id}"
        async with httpx.AsyncClient() as client:
            current_user_response = await client.get(user_url, headers=headers)
            current_user_response.raise_for_status()
            user_data = current_user_response.json()

            user_data['attributes'] = attributes

            response = await client.put(user_url, headers=headers, json=user_data)
            response.raise_for_status()
            logger.info(f"Atributos do usuário {user_id} atualizados com sucesso.")

    async def delete_user(self, user_id: str) -> bool:
        logger.info(f"Deletando usuário ID: {user_id}")
        admin_token = await self._get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_url = f"{self.base_url}/users/{user_id}"
        async with httpx.AsyncClient() as client:
            response = await client.delete(user_url, headers=headers)
            if response.status_code == 404:
                return False
            response.raise_for_status()
            return True

