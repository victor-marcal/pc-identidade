import os
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

from app.api.v1.schemas.seller_schema import SellerCreate
from app.api.common.auth_handler import UserAuthInfo

from ..models import Seller
from ..repositories import SellerRepository
from .base import CrudService

DEFAULT_USER = "system"


class SellerService(CrudService[Seller, str]):
    def __init__(self, repository: SellerRepository, keycloak_client: KeycloakAdminClient):
        super().__init__(repository)
        self.repository: SellerRepository = repository
        self.keycloak_client: KeycloakAdminClient = keycloak_client

    async def create(self, data: Seller) -> Seller:
        # Verifica se seller_id já existe
        if await self.repository.find_by_id(data.seller_id):
            raise BadRequestException(message=MSG_SELLER_ID_JA_CADASTRADO)

        # Verifica se nome_fantasia já existe
        if await self.repository.find_by_nome_fantasia(data.nome_fantasia):
            raise BadRequestException(message=MSG_NOME_FANTASIA_JA_CADASTRADO)

        # Tenta criar o usuário no Keycloak ANTES de criar no banco.
        user_identifier = await self.keycloak_client.create_user(
            username=data.seller_id,
            email=f"{data.seller_id}@email.com",
            password=os.getenv("KEYCLOAK_DEFAULT_PASSWORD", "senha123"),  # Senha configurável via env
            seller_id=data.seller_id,
        )

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

        return await self.repository.create(seller_to_create)

    async def delete_by_id(self, entity_id) -> None:
        deleted = await self.repository.delete_by_id(entity_id)
        if not deleted:
            raise NotFoundException(message=MSG_SELLER_NAO_ENCONTRADO.format(entity_id=entity_id))
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
        current = await self.repository.find_by_id(entity_id)
        if not current:
            raise NotFoundException(message=MSG_SELLER_NAO_ENCONTRADO.format(entity_id=entity_id))

        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            return current

        if "nome_fantasia" in update_data:
            existing = await self.repository.find_by_nome_fantasia(update_data["nome_fantasia"])
            if existing and existing.seller_id != entity_id:
                raise BadRequestException(message=MSG_NOME_FANTASIA_JA_CADASTRADO)

        user_identifier = f"{auth_info.user.server}:{auth_info.user.name}"
        now = utcnow()

        update_data["updated_at"] = now
        update_data["updated_by"] = user_identifier
        update_data["audit_updated_at"] = now

        return await self.repository.patch(entity_id, update_data)

    async def replace(self, entity_id: str, data: Seller, auth_info: UserAuthInfo) -> Seller:
        existing = await self.repository.find_by_id(entity_id)
        if not existing:
            raise NotFoundException(message=MSG_SELLER_NAO_ENCONTRADO.format(entity_id=entity_id))

        if await self.repository.find_by_nome_fantasia(data.nome_fantasia):
            if data.nome_fantasia != existing.nome_fantasia:
                raise BadRequestException(message=MSG_NOME_FANTASIA_JA_CADASTRADO)

        user_identifier = f"{auth_info.user.server}:{auth_info.user.name}"
        now = utcnow()

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

        return await self.repository.update(entity_id, updated_seller)