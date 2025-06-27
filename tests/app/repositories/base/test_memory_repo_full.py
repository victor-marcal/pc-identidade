"""
Testes para melhorar cobertura do memory_repository.py
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.integrations.database.mongo_client import MongoClient
from app.models.seller_model import Seller
from app.repositories.base.memory_repository import AsyncMemoryRepository


@pytest.fixture
def mock_mongo_client():
    """Fixture para mock do MongoDB client"""
    mock_client = MagicMock(spec=MongoClient)
    mock_database = MagicMock()
    mock_collection = MagicMock()  # Changed from AsyncMock to MagicMock

    mock_client.get_database.return_value = mock_database
    mock_database.__getitem__.return_value = mock_collection

    return mock_client, mock_collection


@pytest.mark.asyncio
async def test_create_with_all_defaults(mock_mongo_client):
    """Test create method - covers all setdefault branches"""
    mock_client, mock_collection = mock_mongo_client
    mock_collection.insert_one = AsyncMock(return_value=None)

    seller = Seller(seller_id="1", nome_fantasia="Test", cnpj="12345678000100")
    repo = AsyncMemoryRepository(mock_client, "test_db", "sellers", Seller)

    with patch('app.repositories.base.memory_repository.utcnow') as mock_utcnow:
        mock_utcnow.return_value = "2023-01-01T00:00:00Z"
        await repo.create(seller)

        # Verify insert_one was called
        mock_collection.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_find_by_id_found(mock_mongo_client):
    """Test find_by_id when entity is found"""
    mock_client, mock_collection = mock_mongo_client
    mock_collection.find_one = AsyncMock(
        return_value={"seller_id": "1", "nome_fantasia": "Found", "cnpj": "12345678000100"}
    )

    repo = AsyncMemoryRepository(mock_client, "test_db", "sellers", Seller)
    result = await repo.find_by_id("1")

    assert result is not None
    assert result.seller_id == "1"


@pytest.mark.asyncio
async def test_find_by_id_not_found(mock_mongo_client):
    """Test find_by_id when entity is not found"""
    mock_client, mock_collection = mock_mongo_client
    mock_collection.find_one = AsyncMock(return_value=None)

    repo = AsyncMemoryRepository(mock_client, "test_db", "sellers", Seller)
    result = await repo.find_by_id("999")

    assert result is None


@pytest.mark.asyncio
async def test_find_with_sort(mock_mongo_client):
    """Test find with sort parameter"""
    mock_client, mock_collection = mock_mongo_client

    # Mock the cursor chain - Important: Use MagicMock, not AsyncMock for the cursor methods
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor

    # Mock async iteration
    async def mock_async_iter(self):
        yield {"seller_id": "1", "nome_fantasia": "Test", "cnpj": "12345678000100"}

    mock_cursor.__aiter__ = mock_async_iter
    mock_collection.find.return_value = mock_cursor  # This should return the cursor, not a coroutine

    repo = AsyncMemoryRepository(mock_client, "test_db", "sellers", Seller)
    result = await repo.find({}, sort={"nome_fantasia": 1})

    assert len(result) == 1
    mock_cursor.sort.assert_called_once_with([("nome_fantasia", 1)])


@pytest.mark.asyncio
async def test_find_without_sort(mock_mongo_client):
    """Test find without sort parameter"""
    mock_client, mock_collection = mock_mongo_client

    # Mock the cursor chain - Important: Use MagicMock, not AsyncMock
    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor

    # Mock async iteration
    async def mock_async_iter(self):
        yield {"seller_id": "1", "nome_fantasia": "Test", "cnpj": "12345678000100"}

    mock_cursor.__aiter__ = mock_async_iter
    mock_collection.find.return_value = mock_cursor

    repo = AsyncMemoryRepository(mock_client, "test_db", "sellers", Seller)
    result = await repo.find({})

    assert len(result) == 1
    # Verify sort was not called
    mock_cursor.sort.assert_not_called()


@pytest.mark.asyncio
async def test_update_found(mock_mongo_client):
    """Test update when entity is found"""
    mock_client, mock_collection = mock_mongo_client
    mock_collection.find_one_and_update = AsyncMock(
        return_value={"seller_id": "1", "nome_fantasia": "Updated", "cnpj": "12345678000100"}
    )

    repo = AsyncMemoryRepository(mock_client, "test_db", "sellers", Seller)
    seller = Seller(seller_id="1", nome_fantasia="Updated", cnpj="12345678000100")
    result = await repo.update("1", seller)

    assert result is not None
    assert result.nome_fantasia == "Updated"


@pytest.mark.asyncio
async def test_update_not_found(mock_mongo_client):
    """Test update when entity is not found"""
    mock_client, mock_collection = mock_mongo_client
    mock_collection.find_one_and_update = AsyncMock(return_value=None)

    repo = AsyncMemoryRepository(mock_client, "test_db", "sellers", Seller)
    seller = Seller(seller_id="999", nome_fantasia="Test", cnpj="12345678000100")
    result = await repo.update("999", seller)

    assert result is None


@pytest.mark.asyncio
async def test_delete_by_id_success(mock_mongo_client):
    """Test delete_by_id when entity is deleted"""
    mock_client, mock_collection = mock_mongo_client

    mock_result = MagicMock()
    mock_result.deleted_count = 1
    mock_collection.delete_one = AsyncMock(return_value=mock_result)

    repo = AsyncMemoryRepository(mock_client, "test_db", "sellers", Seller)
    result = await repo.delete_by_id("1")

    assert result is True


@pytest.mark.asyncio
async def test_delete_by_id_not_found(mock_mongo_client):
    """Test delete_by_id when entity is not found"""
    mock_client, mock_collection = mock_mongo_client

    mock_result = MagicMock()
    mock_result.deleted_count = 0
    mock_collection.delete_one = AsyncMock(return_value=mock_result)

    repo = AsyncMemoryRepository(mock_client, "test_db", "sellers", Seller)
    result = await repo.delete_by_id("999")

    assert result is False


@pytest.mark.asyncio
async def test_patch_found(mock_mongo_client):
    """Test patch when entity is found"""
    mock_client, mock_collection = mock_mongo_client
    mock_collection.find_one_and_update = AsyncMock(
        return_value={"seller_id": "1", "nome_fantasia": "Patched", "cnpj": "12345678000100"}
    )

    repo = AsyncMemoryRepository(mock_client, "test_db", "sellers", Seller)
    result = await repo.patch("1", {"nome_fantasia": "Patched"})

    assert result is not None
    assert result.nome_fantasia == "Patched"


@pytest.mark.asyncio
async def test_patch_not_found(mock_mongo_client):
    """Test patch when entity is not found"""
    mock_client, mock_collection = mock_mongo_client
    mock_collection.find_one_and_update = AsyncMock(return_value=None)

    repo = AsyncMemoryRepository(mock_client, "test_db", "sellers", Seller)
    result = await repo.patch("999", {"nome_fantasia": "Test"})

    assert result is None


@pytest.mark.asyncio
async def test_find_with_multiple_documents(mock_mongo_client):
    """Test find method with multiple documents"""
    mock_client, mock_collection = mock_mongo_client

    # Mock the cursor chain - Important: Use MagicMock, not AsyncMock
    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor

    # Mock async iteration with multiple documents
    async def mock_async_iter(self):
        yield {"seller_id": "1", "nome_fantasia": "Test1", "cnpj": "11111111000111"}
        yield {"seller_id": "2", "nome_fantasia": "Test2", "cnpj": "22222222000222"}
        yield {"seller_id": "3", "nome_fantasia": "Test3", "cnpj": "33333333000333"}

    mock_cursor.__aiter__ = mock_async_iter
    mock_collection.find.return_value = mock_cursor

    repo = AsyncMemoryRepository(mock_client, "test_db", "sellers", Seller)
    result = await repo.find({})

    assert len(result) == 3
    assert result[0].seller_id == "1"
    assert result[1].seller_id == "2"
    assert result[2].seller_id == "3"


@pytest.mark.asyncio
async def test_find_with_empty_result(mock_mongo_client):
    """Test find method with empty result"""
    mock_client, mock_collection = mock_mongo_client

    mock_cursor = MagicMock()
    mock_cursor.skip.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    
    # Mock async iterator para retornar lista vazia
    mock_cursor.__aiter__.return_value = iter([])
    mock_collection.find.return_value = mock_cursor

    repo = AsyncMemoryRepository(mock_client, "test_db", "sellers", Seller)
    result = await repo.find({})

    assert len(result) == 0
