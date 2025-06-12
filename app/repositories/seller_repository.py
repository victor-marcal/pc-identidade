from typing import Optional
from uuid import UUID

from app.integrations.database.mongo_client import MongoClient

from ..models import Seller
from .base import AsyncMemoryRepository


class SellerRepository(AsyncMemoryRepository[Seller]):

    COLLECTION_NAME = "sellers"

    def __init__(self,client: "MongoClient"):
        super().__init__(client, collection_name=self.COLLECTION_NAME,model_class=Seller)

    async def find_by_nome_fantasia(self, nome_fantasia: str) -> Optional[Seller]:
        return await self.collection.find_one({"nome_fantasia": nome_fantasia})

    async def delete_by_id(self, seller_id: UUID) -> bool:
        return await self.delete({"seller_id": str(seller_id)})

    async def find_by_cnpj(self, cnpj: str) -> Optional[Seller]:
        return await self.collection.find_one({"cnpj": cnpj})

__all__ = ["SellerRepository"]
