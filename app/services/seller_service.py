from app.common.exceptions.application_exception import ApplicationException
from app.common.exceptions.bad_request_exception import BadRequestException
from app.common.exceptions.not_found_exception import NotFoundException
from app.models.seller_model import Seller
from app.repositories.seller_repository import SellerRepository
from ..models import Seller
from ..repositories import SellerRepository
from .base import CrudService


class SellerService(CrudService[Seller, str]):
    def __init__(self, repository: SellerRepository):
        super().__init__(repository)

    async def find_by_name(self, name: str) -> Seller:
        """
        Busca um Seller pelo nome.
        """
        return await self.repository.find_by_name(name=name)

    async def create(self, data: Seller) -> Seller:
        try:
            await self.repository.find_by_nome_fantasia(data.nome_fantasia)
            raise BadRequestException("O nome_fantasia informado já está cadastrado. Escolha outro.")
        except:
            pass  # nome_fantasia está livre
        return await self.repository.create(data)

    async def update(self, entity_id: str, data: Seller) -> Seller:
        try:
            existing = await self.repository.find_by_nome_fantasia(data.nome_fantasia)
            if existing.seller_id != entity_id:
                raise ApplicationException("O nome_fantasia informado já está cadastrado. Escolha outro.")
        except:
            pass
        return await self.repository.update(entity_id, data)
    
