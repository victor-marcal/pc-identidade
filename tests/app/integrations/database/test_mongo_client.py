import pytest
from unittest.mock import MagicMock, patch
from app.integrations.database.mongo_client import MongoClient, MongoDB, SetCodec


def test_set_codec_properties():
    """Test SetCodec class properties - follows Single Responsibility Principle"""
    codec = SetCodec()
    
    assert codec.python_type == set
    assert codec.bson_type == 4


def test_set_codec_transform_python():
    """Test SetCodec transform_python method"""
    codec = SetCodec()
    
    result = codec.transform_python([1, 2, 3])
    
    assert result == [1, 2, 3]
    assert isinstance(result, list)


def test_set_codec_transform_bson():
    """Test SetCodec transform_bson method"""
    codec = SetCodec()
    
    result = codec.transform_bson({1, 2, 3})
    
    assert isinstance(result, list)
    assert set(result) == {1, 2, 3}


def test_mongo_db_init():
    """Test MongoDB initialization - follows Dependency Injection"""
    mock_db = MagicMock()
    mongo_db = MongoDB(mock_db)
    
    assert mongo_db.db == mock_db


def test_mongo_db_getitem():
    """Test MongoDB __getitem__ method"""
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    
    mongo_db = MongoDB(mock_db)
    
    result = mongo_db["test_collection"]
    
    assert result == mock_collection
    mock_db.__getitem__.assert_called_once_with("test_collection")


@patch('app.integrations.database.mongo_client.AsyncIOMotorClient')
def test_mongo_client_init(mock_async_client):
    """Test MongoClient initialization - follows Dependency Inversion Principle"""
    from pydantic import MongoDsn
    
    mongo_url = MongoDsn("mongodb://localhost:27017/test")
    mock_instance = MagicMock()
    mock_async_client.return_value = mock_instance
    
    client = MongoClient(mongo_url)
    
    assert client.mongo_url == mongo_url
    assert client.motor_client == mock_instance
    mock_async_client.assert_called_once_with(str(mongo_url))


def test_mongo_client_close():
    """Test MongoClient close method"""
    from pydantic import MongoDsn
    
    with patch('app.integrations.database.mongo_client.AsyncIOMotorClient') as mock_async_client:
        mock_instance = MagicMock()
        mock_async_client.return_value = mock_instance
        
        mongo_url = MongoDsn("mongodb://localhost:27017/test")
        client = MongoClient(mongo_url)
        
        client.close()
        
        mock_instance.close.assert_called_once()


def test_mongo_client_del_with_exception():
    """Test MongoClient __del__ method with exception handling"""
    from pydantic import MongoDsn
    
    with patch('app.integrations.database.mongo_client.AsyncIOMotorClient') as mock_async_client:
        mock_instance = MagicMock()
        mock_async_client.return_value = mock_instance
        
        mongo_url = MongoDsn("mongodb://localhost:27017/test")
        client = MongoClient(mongo_url)
        
        # Test __del__ with exception handling - should not raise
        mock_instance.close.side_effect = Exception("Connection error")
        
        try:
            del client  # This should not raise an exception
        except Exception:
            pytest.fail("__del__ should not raise exceptions")


@patch('app.integrations.database.mongo_client.AsyncIOMotorClient')
def test_mongo_client_get_default_database(mock_async_client):
    """Test MongoClient get_default_database method"""
    from pydantic import MongoDsn
    
    mock_instance = MagicMock()
    mock_db = MagicMock()
    mock_instance.get_default_database.return_value = mock_db
    mock_async_client.return_value = mock_instance
    
    mongo_url = MongoDsn("mongodb://localhost:27017/test")
    client = MongoClient(mongo_url)
    
    result = client.get_default_database()
    
    assert isinstance(result, MongoDB)
    assert result.db == mock_db
    mock_instance.get_default_database.assert_called_once()


@patch('app.integrations.database.mongo_client.AsyncIOMotorClient')
def test_mongo_client_getitem(mock_async_client):
    """Test MongoClient __getitem__ method"""
    from pydantic import MongoDsn
    
    mock_instance = MagicMock()
    mock_db = MagicMock()
    mock_instance.__getitem__.return_value = mock_db
    mock_async_client.return_value = mock_instance
    
    mongo_url = MongoDsn("mongodb://localhost:27017/test")
    client = MongoClient(mongo_url)
    
    result = client["test_database"]
    
    assert isinstance(result, MongoDB)
    assert result.db == mock_db
    mock_instance.__getitem__.assert_called_once_with("test_database")


@patch('app.integrations.database.mongo_client.AsyncIOMotorClient')
def test_mongo_client_get_collection(mock_async_client):
    """Test MongoClient get_collection method"""
    from pydantic import MongoDsn
    
    mock_instance = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_instance.get_default_database.return_value = mock_db
    mock_async_client.return_value = mock_instance
    
    mongo_url = MongoDsn("mongodb://localhost:27017/test")
    client = MongoClient(mongo_url)
    
    result = client.get_collection("test_collection")
    
    assert result == mock_collection
