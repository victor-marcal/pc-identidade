import re

from app.common.exceptions.application_exception import ApplicationException
from app.common.exceptions.bad_request_exception import BadRequestException
from app.common.exceptions.not_found_exception import NotFoundException
from app.common.datetime import utcnow
from app.models.seller_model import Seller
from app.repositories.seller_repository import SellerRepository

from app.models.seller_patch_model import SellerPatch

from ..models import Seller
from ..repositories import SellerRepository
from .base import CrudService


class SellerService(CrudService[Seller, str]):
    def __init__(self, repository: SellerRepository):
        super().__init__(repository)
        self.repository: SellerRepository = repository

    async def create(self, data: Seller) -> Seller:
        # Verifica se seller_id já existe
        if await self.repository.find_by_id(data.seller_id):
            raise BadRequestException(message="O seller_id informado já está cadastrado. Escolha outro.")

        # Verifica se nome_fantasia já existe
        if await self.repository.find_by_nome_fantasia(data.nome_fantasia):
            raise BadRequestException(message="O nome_fantasia informado já está cadastrado. Escolha outro.")

        return await self.repository.create(data)

    async def update(self, entity_id: str, data: SellerPatch) -> Seller:
        current = await self.repository.find_by_id(entity_id)
        if not current:
            raise NotFoundException(message=f"Seller com ID '{entity_id}' não encontrado.")

        if data.nome_fantasia is not None:
            existing = await self.repository.find_by_nome_fantasia(data.nome_fantasia)
            if existing and existing.seller_id != entity_id:
                raise BadRequestException(message="O nome_fantasia informado já está cadastrado. Escolha outro.")
            current.nome_fantasia = data.nome_fantasia

        if data.cnpj is not None:
            current.cnpj = data.cnpj

        # Atualiza timestamp da modificação
        current.updated_at = utcnow()

        return await self.repository.update(entity_id, current)

    async def delete_by_id(self, entity_id) -> None:
        deleted = await self.repository.delete_by_id(entity_id)
        if not deleted:
            raise NotFoundException(message=f"Seller com ID '{entity_id}' não encontrado.")
        return deleted
