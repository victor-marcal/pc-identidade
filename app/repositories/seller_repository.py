from uuid import UUID

from app.common.exceptions import NotFoundException

from ..models import Seller
from .base import AsyncMemoryRepository


class SellerRepository(AsyncMemoryRepository[Seller, UUID]):

    def __init__(self):
        super().__init__(model_class=Seller) 

    async def find_by_name(self, name: str) -> Seller:
        """
        Busca um alguma coisa pelo nome.
        """
        result = next((s for s in self.memory if s.name == name), None)
        if result:
            return result
        raise NotFoundException()
    
    async def find_by_nome_fantasia(self, nome_fantasia: str) -> Seller:
        """
        Busca um Seller pelo nome_fantasia.
        """
        result = next((s for s in self.memory if s.nome_fantasia == nome_fantasia), None)
        if result:
            return result
        raise NotFoundException()


__all__ = ["SellerRepository"]