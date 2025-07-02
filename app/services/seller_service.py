import os

import logging

from app.api.common.auth_handler import UserAuthInfo
from app.api.v1.schemas.seller_schema import SellerCreate
from app.clients.keycloak_admin_client import KeycloakAdminClient
from app.common.datetime import utcnow
from app.common.exceptions import BadRequestException, NotFoundException
from app.messages import (
    MSG_NOME_FANTASIA_JA_CADASTRADO,
    MSG_SELLER_CNPJ_NAO_ENCONTRADO,
    MSG_SELLER_ID_JA_CADASTRADO,
    MSG_SELLER_NAO_ENCONTRADO,
)
from app.models.seller_model import Seller
from app.models.seller_patch_model import SellerPatch
from app.repositories.seller_repository import SellerRepository

from ..models import Seller
from ..repositories import SellerRepository
from .base import CrudService

DEFAULT_USER = "system"

logger = logging.getLogger(__name__)


class SellerService(CrudService[Seller, str]):
    def __init__(self, repository: SellerRepository, keycloak_client: KeycloakAdminClient):
        super().__init__(repository)
        self.repository: SellerRepository = repository
        self.keycloak_client: KeycloakAdminClient = keycloak_client

    async def create(self, data: Seller) -> Seller:
        logger.info(f"Iniciando processo de criação para o seller_id: {data.seller_id}")
        # Verifica se seller_id já existe
        if await self.repository.find_by_id(data.seller_id):
            logger.warning(f"Tentativa de criar seller com ID duplicado: {data.seller_id}")
            raise BadRequestException(message=MSG_SELLER_ID_JA_CADASTRADO)

        # Verifica se nome_fantasia já existe
        if await self.repository.find_by_nome_fantasia(data.nome_fantasia):
            logger.warning(f"Tentativa de criar seller com nome_fantasia duplicado: {data.seller_id}")
            raise BadRequestException(message=MSG_NOME_FANTASIA_JA_CADASTRADO)

        # Tenta criar o usuário no Keycloak ANTES de criar no banco.
        try:
            logger.debug(f"Tentando criar usuário no Keycloak para o seller: {data.seller_id}")
            user_identifier = await self.keycloak_client.create_user(
                username=data.seller_id,
                email=f"{data.seller_id}@email.com",
                password=os.getenv("KEYCLOAK_DEFAULT_PASSWORD", "senha123"),
                seller_id=data.seller_id,
            )
            logger.info(f"Usuário criado com sucesso no Keycloak: {user_identifier}")
        except Exception:
            logger.error(f"Falha crítica ao tentar criar usuário no Keycloak para o seller: {data.seller_id}", exc_info=True)
            raise

        now = utcnow()

        seller_to_create = Seller(
            seller_id=data.seller_id,
            nome_fantasia=data.nome_fantasia,
            cnpj=data.cnpj,
            created_at=now,
            updated_at=now,
            created_by=user_identifier,
            updated_by=user_identifier,
            audit_created_at=now,
            audit_updated_at=now,
        )

        logger.debug(f"Enviando dados do seller '{data.seller_id}' para o repositório.")
        created_seller = await self.repository.create(seller_to_create)
        logger.info(f"Seller '{data.seller_id}' criado com sucesso no banco de dados.")

        return created_seller

    async def delete_by_id(self, entity_id) -> None:
        logger.info(f"Iniciando processo de exclusão para o seller_id: {entity_id}")
        deleted = await self.repository.delete_by_id(entity_id)
        if not deleted:
            logger.warning(f"Tentativa de excluir seller inexistente com ID: {entity_id}")
            raise NotFoundException(message=MSG_SELLER_NAO_ENCONTRADO.format(entity_id=entity_id))
        logger.info(f"Seller '{entity_id}' excluído com sucesso.")
        return deleted

    async def find_by_id(self, seller_id: str) -> Seller:
        seller = await self.repository.find_by_id(seller_id)
        if not seller:
            raise NotFoundException(message=MSG_SELLER_NAO_ENCONTRADO.format(entity_id=seller_id))
        return seller

    async def find_by_cnpj(self, cnpj: str) -> Seller:
        seller = await self.repository.find_by_cnpj(cnpj)
        if not seller:
            raise NotFoundException(message=MSG_SELLER_CNPJ_NAO_ENCONTRADO.format(cnpj=cnpj))
        return seller

    async def update(self, entity_id: str, data: SellerPatch, auth_info: UserAuthInfo) -> Seller:
        user_identifier = f"{auth_info.user.server}:{auth_info.user.name}"
        logger.info(f"Usuário '{user_identifier}' iniciando atualização (PATCH) para o seller_id: {entity_id}")
        current = await self.repository.find_by_id(entity_id)
        if not current:
            logger.warning(f"Usuário '{user_identifier}' tentou atualizar um seller inexistente: {entity_id}")
            raise NotFoundException(message=MSG_SELLER_NAO_ENCONTRADO.format(entity_id=entity_id))

        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            logger.info(f"Nenhum campo para atualizar no seller_id: {entity_id}. Nenhuma ação realizada.")
            return current

        if "nome_fantasia" in update_data:
            existing = await self.repository.find_by_nome_fantasia(update_data["nome_fantasia"])
            if existing and existing.seller_id != entity_id:
                logger.warning(f"Tentativa de atualizar seller '{entity_id}' com nome_fantasia que já está em uso.")
                raise BadRequestException(message=MSG_NOME_FANTASIA_JA_CADASTRADO)

        now = utcnow()

        update_data["updated_at"] = now
        update_data["updated_by"] = user_identifier
        update_data["audit_updated_at"] = now

        updated_seller = await self.repository.patch(entity_id, update_data)
        logger.info(f"Seller '{entity_id}' atualizado com sucesso pelo usuário '{user_identifier}'.")

        return updated_seller

    async def replace(self, entity_id: str, data: Seller, auth_info: UserAuthInfo) -> Seller:
        user_identifier = f"{auth_info.user.server}:{auth_info.user.name}"
        logger.info(f"Usuário '{user_identifier}' iniciando substituição (PUT) para o seller_id: {entity_id}")
        existing = await self.repository.find_by_id(entity_id)
        if not existing:
            logger.warning(f"Usuário '{user_identifier}' tentou substituir um seller inexistente: {entity_id}")
            raise NotFoundException(message=MSG_SELLER_NAO_ENCONTRADO.format(entity_id=entity_id))

        if await self.repository.find_by_nome_fantasia(data.nome_fantasia):
            if data.nome_fantasia != existing.nome_fantasia:
                logger.warning(
                    f"Conflito de nome fantasia ao tentar substituir o seller '{entity_id}'. "
                    f"O nome '{data.nome_fantasia}' já está em uso."
                )
                raise BadRequestException(message=MSG_NOME_FANTASIA_JA_CADASTRADO)

        now = utcnow()

        logger.debug(f"Montando objeto de substituição para o seller '{entity_id}'.")
        updated_seller = Seller(
            seller_id=entity_id,
            nome_fantasia=data.nome_fantasia,
            cnpj=data.cnpj,
            created_at=existing.created_at,
            created_by=existing.created_by,
            updated_at=now,
            updated_by=user_identifier,
            audit_created_at=existing.audit_created_at,
            audit_updated_at=now,
        )

        result = await self.repository.update(entity_id, updated_seller)

        logger.info(f"Seller '{entity_id}' substituído com sucesso pelo usuário '{user_identifier}'.")

        return result
