from typing import Any, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from app.integrations.database.mongo_client import MongoClient
from app.models.query_model import QueryModel
from pydantic import BaseModel

from app.common.datetime import utcnow

from .async_crud_repository import AsyncCrudRepository

T = TypeVar("T", bound=BaseModel)
ID = TypeVar("ID", bound=UUID)
Q = TypeVar("Q", bound=QueryModel)

class AsyncMemoryRepository(AsyncCrudRepository[T], Generic[T]):

    def __init__(self, client: MongoClient, collection_name: str, model_class: Type[T]):
        """
        Repositório genérico para MongoDB.

        :param client: Instância do MongoClient.
        :param collection_name: Nome da coleção.
        :param model_class: Classe do modelo (usada para criar instâncias de saída).
        """
        self.collection = client.get_default_database()[collection_name]
        self.model_class = model_class

    async def create(self, entity: T) -> T:
        entity_dict = entity.model_dump(by_alias=True)
        entity_dict["seller_id"] = str(entity.seller_id)
        entity_dict["created_at"] = utcnow()
        entity_dict["updated_at"] = utcnow()
        await self.collection.insert_one(entity_dict)
        return self.model_class(**entity_dict)

    async def find_by_id(self, seller_id: str | UUID) -> T | None:
        if isinstance(seller_id, UUID):
            seller_id = str(seller_id)
        result = await self.collection.find_one({"seller_id": seller_id})
        if result is not None:
            result = self.model_class(**result)
        return result

    async def find(self, filters: dict, limit: int = 10, offset: int = 0, sort: Optional[dict] = None) -> List[T]:
        filtered_list = self.find(filters)

        # Aplica filtros dinamicamente
        for key, value in filters.items():
            filtered_list = [item for item in filtered_list if getattr(item, key, None) == value]

        # TODO: aplicar ordenação por sort se necessário

        return await filtered_list[offset : offset + limit]

    async def update(self, entity_id: ID, entity: Any) -> Optional[T]:
        # Converte a entidade para um dicionário, excluindo campos desnecessários
        entity_dict = entity.model_dump(by_alias=True, exclude={"identity"})
        entity_dict["updated_at"] = utcnow()

        # Busca o documento atual pelo ID
        current_document = await self.find_by_id(entity_id)

        if current_document:
            # Atualiza os campos diretamente no objeto existente
            for key, value in entity_dict.items():
                setattr(current_document, key, value)

            return current_document

        return None
    
    async def delete(self, filter: dict) -> bool:
        # XXX Atenção aqui!
        deleted = await self.collection.delete_many(filter)
        has_deleted = deleted.deleted_count > 0
        return has_deleted
