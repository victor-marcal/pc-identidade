import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_mongo_client():
    client = MagicMock()
    collection = MagicMock()

    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.find_one_and_update = AsyncMock()
    collection.delete_one = AsyncMock()

    class AsyncCursor:
        def __init__(self, docs):
            self.docs = docs

        def skip(self, n):
            return self

        def limit(self, n):
            return self

        def sort(self, *args, **kwargs):
            return self

        def __aiter__(self):
            async def gen():
                for doc in self.docs:
                    yield doc
            return gen()

    collection.find.return_value = AsyncCursor([])

    # Corrigido aqui: adiciona a chave 'sellers' ao dicionário
    client.get_default_database.return_value = {
        "test_collection": collection,
        "sellers": collection,
    }

    return client, collection
