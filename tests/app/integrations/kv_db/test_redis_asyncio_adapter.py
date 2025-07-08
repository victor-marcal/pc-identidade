import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from app.integrations.kv_db.redis_asyncio_adapter import RedisAsyncioAdapter


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock_redis = AsyncMock()
    return mock_redis


@pytest.fixture
def redis_adapter(mock_redis):
    """Create RedisAsyncioAdapter with mocked Redis client."""
    with patch('app.integrations.kv_db.redis_asyncio_adapter.Redis.from_url', return_value=mock_redis):
        adapter = RedisAsyncioAdapter("redis://localhost:6379")
    return adapter


class TestRedisAsyncioAdapter:
    
    @pytest.mark.asyncio
    async def test_init(self):
        """Test adapter initialization."""
        with patch('app.integrations.kv_db.redis_asyncio_adapter.Redis.from_url') as mock_from_url:
            mock_redis = AsyncMock()
            mock_from_url.return_value = mock_redis
            
            adapter = RedisAsyncioAdapter("redis://localhost:6379")
            
            assert adapter.redis_url == "redis://localhost:6379"
            assert adapter.redis_client == mock_redis
            mock_from_url.assert_called_once_with("redis://localhost:6379")

    @pytest.mark.asyncio
    async def test_aclose(self, redis_adapter, mock_redis):
        """Test closing Redis connection."""
        await redis_adapter.aclose()
        mock_redis.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_exists_true(self, redis_adapter, mock_redis):
        """Test exists method when key exists."""
        mock_redis.exists.return_value = 1
        
        result = await redis_adapter.exists("test_key")
        
        assert result is True
        mock_redis.exists.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_exists_false(self, redis_adapter, mock_redis):
        """Test exists method when key doesn't exist."""
        mock_redis.exists.return_value = 0
        
        result = await redis_adapter.exists("test_key")
        
        assert result is False
        mock_redis.exists.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_str_exists(self, redis_adapter, mock_redis):
        """Test get_str when key exists."""
        mock_redis.get.return_value = b"test_value"
        
        result = await redis_adapter.get_str("test_key")
        
        assert result == "test_value"
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_str_not_exists(self, redis_adapter, mock_redis):
        """Test get_str when key doesn't exist."""
        mock_redis.get.return_value = None
        
        result = await redis_adapter.get_str("test_key")
        
        assert result is None
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_set_str_with_string(self, redis_adapter, mock_redis):
        """Test set_str with string value."""
        await redis_adapter.set_str("test_key", "test_value", 60)
        
        mock_redis.set.assert_called_once_with("test_key", "test_value", 60)

    @pytest.mark.asyncio
    async def test_set_str_with_non_string(self, redis_adapter, mock_redis):
        """Test set_str with non-string value."""
        await redis_adapter.set_str("test_key", 123, 60)
        
        mock_redis.set.assert_called_once_with("test_key", "123", 60)

    @pytest.mark.asyncio
    async def test_set_str_with_none(self, redis_adapter, mock_redis):
        """Test set_str with None value (should delete)."""
        await redis_adapter.set_str("test_key", None)
        
        mock_redis.delete.assert_called_once_with("test_key")
        mock_redis.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_str_without_expiration(self, redis_adapter, mock_redis):
        """Test set_str without expiration."""
        await redis_adapter.set_str("test_key", "test_value")
        
        mock_redis.set.assert_called_once_with("test_key", "test_value", None)

    @pytest.mark.asyncio
    async def test_get_json_valid(self, redis_adapter, mock_redis):
        """Test get_json with valid JSON."""
        test_data = {"key": "value", "number": 123}
        mock_redis.get.return_value = json.dumps(test_data).encode()
        
        result = await redis_adapter.get_json("test_key")
        
        assert result == test_data
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_json_none(self, redis_adapter, mock_redis):
        """Test get_json when key doesn't exist."""
        mock_redis.get.return_value = None
        
        result = await redis_adapter.get_json("test_key")
        
        assert result is None
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_set_json_dict(self, redis_adapter, mock_redis):
        """Test set_json with dictionary."""
        test_data = {"key": "value"}
        expected_json = json.dumps(test_data)
        
        await redis_adapter.set_json("test_key", test_data, 60)
        
        mock_redis.set.assert_called_once_with("test_key", expected_json, 60)

    @pytest.mark.asyncio
    async def test_set_json_list(self, redis_adapter, mock_redis):
        """Test set_json with list."""
        test_data = [1, 2, 3]
        expected_json = json.dumps(test_data)
        
        await redis_adapter.set_json("test_key", test_data)
        
        mock_redis.set.assert_called_once_with("test_key", expected_json, None)

    @pytest.mark.asyncio
    async def test_set_json_none(self, redis_adapter, mock_redis):
        """Test set_json with None value."""
        await redis_adapter.set_json("test_key", None)
        
        mock_redis.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_delete(self, redis_adapter, mock_redis):
        """Test delete method."""
        await redis_adapter.delete("test_key")
        
        mock_redis.delete.assert_called_once_with("test_key")

    # TODO: Fix context manager tests - mock setup issue
    # @pytest.mark.asyncio
    # async def test_locks_context_manager(self, redis_adapter):
    #     """Test locks context manager."""
    #     pass

    # @pytest.mark.asyncio
    # async def test_locks_default_prefix(self, redis_adapter):
    #     """Test locks context manager with default prefix."""
    #     pass
