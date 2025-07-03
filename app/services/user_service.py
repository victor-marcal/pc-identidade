import logging
from app.clients.keycloak_admin_client import KeycloakAdminClient
from app.api.v1.schemas.user_schema import UserCreate, UserResponse
from app.common.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, keycloak_client: KeycloakAdminClient):
        self.keycloak_client = keycloak_client

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Cria um novo usuário no Keycloak.
        """
        user_id = await self.keycloak_client.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            sellers=[]
        )
        logger.info(f"Usuário '{user_data.username}' criado com sucesso com o ID: {user_id}")
        return await self.get_user_by_id(user_id)


    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """
        Busca um usuário no Keycloak pelo seu ID.
        """
        logger.debug(f"Buscando usuário com ID: {user_id}")
        user_info = await self.keycloak_client.get_user(user_id)
        if not user_info:
            logger.warning(f"Usuário com ID '{user_id}' não encontrado.")
            raise NotFoundException(message=f"Usuário com ID '{user_id}' não encontrado.")

        return UserResponse(
            id=user_info.get("id"),
            username=user_info.get("username"),
            email=user_info.get("email"),
            first_name=user_info.get("firstName"),
            last_name=user_info.get("lastName"),
            enabled=user_info.get("enabled"),
            attributes=user_info.get("attributes"),
        )

    async def get_all_users(self) -> list[UserResponse]:
        """
        Lista todos os usuários do realm no Keycloak.
        """
        logger.debug("Listando todos os usuários do Keycloak.")
        users_info = await self.keycloak_client.get_users()
        return [
            UserResponse(
                id=user.get("id"),
                username=user.get("username"),
                email=user.get("email"),
                first_name=user.get("firstName"),
                last_name=user.get("lastName"),
                enabled=user.get("enabled"),
                attributes=user.get("attributes"),
            ) for user in users_info
        ]

    async def delete_user(self, user_id: str) -> None:
        """
        Deleta um usuário do Keycloak.
        """
        logger.info(f"Iniciando exclusão do usuário com ID: {user_id}")
        success = await self.keycloak_client.delete_user(user_id)
        if not success:
            raise NotFoundException(
                message=f"Não foi possível deletar o usuário com ID '{user_id}' pois ele não foi encontrado.")
        logger.info(f"Usuário com ID '{user_id}' deletado com sucesso.")