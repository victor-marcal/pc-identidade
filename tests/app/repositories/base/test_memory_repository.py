from unittest import mock
from uuid import UUID

import pytest

from app.models.seller_model import Seller
from app.repositories.base.memory_repository import AsyncMemoryRepository
from tests.helpers.test_fixtures import create_full_seller, create_minimal_seller_dict


@pytest.mark.asyncio
class TestAsyncMemoryRepository:
    async def test_create(self, mock_mongo_client):
        client, collection = mock_mongo_client
        model = create_full_seller(seller_id="seller01", trade_name="Loja Exemplo")
        collection.insert_one.return_value = mock.MagicMock()

        repo = AsyncMemoryRepository(client, "test_db", "test_collection", Seller)
        result = await repo.create(model)

        collection.insert_one.assert_called_once()
        assert result.seller_id == model.seller_id

    async def test_find_by_id(self, mock_mongo_client):
        client, collection = mock_mongo_client
        collection.find_one.return_value = create_minimal_seller_dict(
            seller_id="seller01", trade_name="Loja Exemplo2"
        )

        repo = AsyncMemoryRepository(client, "test_db", "test_collection", Seller)
        result = await repo.find_by_id("seller01")

        assert result.seller_id == "seller01"

    async def test_find(self, mock_mongo_client):
        client, collection = mock_mongo_client
        doc = create_minimal_seller_dict(seller_id="seller01", trade_name="Loja Exemplo3")

        async def cursor_simulator():
            yield doc

        collection.find.return_value = mock.MagicMock()
        collection.find.return_value.skip.return_value = collection.find.return_value
        collection.find.return_value.limit.return_value = cursor_simulator()

        repo = AsyncMemoryRepository(client, "test_db", "test_collection", Seller)
        result = await repo.find({"seller_id": "seller01"})

        assert len(result) == 1
        assert result[0].seller_id == "seller01"

    async def test_update(self, mock_mongo_client):
        STORE_UPDATE = "Loja Atualizada"
        client, collection = mock_mongo_client
        collection.find_one_and_update.return_value = create_minimal_seller_dict(
            seller_id="seller01", trade_name=STORE_UPDATE
        )

        model = create_full_seller(seller_id="seller01", trade_name=STORE_UPDATE)
        repo = AsyncMemoryRepository(client, "test_db", "test_collection", Seller)
        result = await repo.update("seller01", model)

        assert result.trade_name == STORE_UPDATE

    async def test_delete_by_id(self, mock_mongo_client):
        client, collection = mock_mongo_client
        collection.delete_one.return_value = mock.MagicMock(deleted_count=1)

        repo = AsyncMemoryRepository(client, "test_db", "test_collection", Seller)
        result = await repo.delete_by_id("seller01")

        assert result is True

    async def test_patch(self, mock_mongo_client):
        STORE_PATCH = "Loja Patch"
        client, collection = mock_mongo_client
        collection.find_one_and_update.return_value = create_minimal_seller_dict(
            seller_id="seller01", trade_name=STORE_PATCH
        )

        repo = AsyncMemoryRepository(client, "test_db", "test_collection", Seller)
        result = await repo.patch("seller01", {"trade_name": STORE_PATCH})

        assert result.trade_name == STORE_PATCH
