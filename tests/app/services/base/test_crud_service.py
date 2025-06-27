import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.base.crud_service import CrudService
from app.api.common.schemas.pagination import Paginator


class MockCrudService(CrudService):
    """Mock implementation for testing - follows Single Responsibility Principle"""
    
    def __init__(self, repository):
        self.repository = repository


class MockEntity:
    """Simple mock entity for testing"""
    def __init__(self, entity_id: str, name: str):
        self.entity_id = entity_id
        self.name = name


def test_crud_service_init():
    """Test CrudService initialization - follows Dependency Inversion Principle"""
    mock_repo = MagicMock()
    service = MockCrudService(mock_repo)
    
    assert service.repository == mock_repo


def test_crud_service_context_property():
    """Test CrudService context property"""
    mock_repo = MagicMock()
    service = MockCrudService(mock_repo)
    
    assert service.context is None


def test_crud_service_author_property():
    """Test CrudService author property"""
    mock_repo = MagicMock()
    service = MockCrudService(mock_repo)
    
    assert service.author is None


@pytest.mark.asyncio
async def test_crud_service_find():
    """Test CrudService find method with proper parameters"""
    mock_repo = AsyncMock()
    mock_entity = MockEntity("1", "Test")
    mock_repo.find.return_value = [mock_entity]
    
    service = MockCrudService(mock_repo)
    paginator = Paginator(request_path="/test", limit=10, offset=0)
    filters = {"name": "Test"}
    
    result = await service.find(paginator, filters)
    
    assert result == [mock_entity]
    mock_repo.find.assert_called_once_with(
        filters=filters, 
        limit=10, 
        offset=0, 
        sort=None
    )


@pytest.mark.asyncio
async def test_crud_service_find_by_id():
    """Test CrudService find_by_id method"""
    mock_repo = AsyncMock()
    mock_entity = MockEntity("test_id", "Test")
    mock_repo.find_by_id.return_value = mock_entity
    
    service = MockCrudService(mock_repo)
    
    result = await service.find_by_id("test_id")
    
    assert result == mock_entity
    mock_repo.find_by_id.assert_called_once_with("test_id")


@pytest.mark.asyncio
async def test_crud_service_create():
    """Test CrudService create method"""
    mock_repo = AsyncMock()
    mock_entity = MockEntity("new_id", "New Entity")
    mock_repo.create.return_value = mock_entity
    
    service = MockCrudService(mock_repo)
    
    result = await service.create(mock_entity)
    
    assert result == mock_entity
    mock_repo.create.assert_called_once_with(mock_entity)


@pytest.mark.asyncio
async def test_crud_service_update():
    """Test CrudService update method"""
    mock_repo = AsyncMock()
    mock_entity = MockEntity("test_id", "Updated Entity")
    mock_repo.update.return_value = mock_entity
    
    service = MockCrudService(mock_repo)
    
    result = await service.update("test_id", mock_entity)
    
    assert result == mock_entity
    mock_repo.update.assert_called_once_with("test_id", mock_entity)


@pytest.mark.asyncio
async def test_crud_service_delete_by_id():
    """Test CrudService delete_by_id method"""
    mock_repo = AsyncMock()
    mock_repo.delete_by_id.return_value = None
    
    service = MockCrudService(mock_repo)
    
    result = await service.delete_by_id("test_id")
    
    assert result is None
    mock_repo.delete_by_id.assert_called_once_with("test_id")


@pytest.mark.asyncio
async def test_crud_service_find_with_sort():
    """Test CrudService find method with sorting"""
    mock_repo = AsyncMock()
    mock_entity = MockEntity("1", "Test")
    mock_repo.find.return_value = [mock_entity]
    
    service = MockCrudService(mock_repo)
    paginator = Paginator(request_path="/test", limit=5, offset=10, sort="name:desc")
    filters = {}
    
    result = await service.find(paginator, filters)
    
    assert result == [mock_entity]
    mock_repo.find.assert_called_once_with(
        filters=filters, 
        limit=5, 
        offset=10, 
        sort={"name": -1}
    )
