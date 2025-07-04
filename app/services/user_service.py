import logging
from app.clients.keycloak_admin_client import KeycloakAdminClient
from app.api.v1.schemas.user_schema import UserCreate, UserResponse, UserPatch
from app.common.exceptions import NotFoundException, BadRequestException

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

        valid_users = []
        for user in users_info:
            # Verifica se os campos obrigatórios existem e não são nulos
            user_id = user.get("id")
            username = user.get("username")
            email = user.get("email")

            if user_id and username and email:
                valid_users.append(
                    UserResponse(
                        id=user_id,
                        username=username,
                        email=email,
                        first_name=user.get("firstName"),
                        last_name=user.get("lastName"),
                        enabled=user.get("enabled", False),
                        attributes=user.get("attributes"),
                    )
                )
            else:
                # Loga um aviso para que possa encontrar e corrigir o usuário no Keycloak
                logger.warning(
                    f"Usuário ignorado devido a dados incompletos. "
                    f"ID: {user_id}, Username: {username}"
                )

        return valid_users

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

    async def patch_user(self, user_id: str, patch_data: UserPatch) -> UserResponse:
        """
        Atualiza parcialmente os dados de um usuário, incluindo a senha.
        """
        logger.info(f"Iniciando atualização parcial para o usuário com ID: {user_id}")

        user_info_to_update = patch_data.model_dump(exclude_unset=True, exclude={"password"})

        try:
            if user_info_to_update:
                await self.keycloak_client.update_user(user_id, user_info_to_update)
                logger.info(f"Dados de perfil do usuário '{user_id}' atualizados.")

            if patch_data.password:
                await self.keycloak_client.reset_user_password(user_id, patch_data.password)
                logger.info(f"Senha do usuário '{user_id}' foi redefinida.")

        except BadRequestException as e:
            raise e

        return await self.get_user_by_id(user_id)
