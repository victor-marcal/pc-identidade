from uuid import UUID

from app.common.exceptions import NotFoundException

from ..models import Something
from .base import AsyncMemoryRepository


class SomethingRepository(AsyncMemoryRepository[Something, UUID]):

    async def find_by_name(self, name: str) -> Something:
        """
        Busca um alguma coisa pelo nome.
        """
        result = next((s for s in self.memory if s["name"] == name), None)
        if result:
            return result
        raise NotFoundException()


__all__ = ["SomethingRepository"]
