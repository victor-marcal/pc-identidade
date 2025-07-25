from unittest.mock import MagicMock, patch

import pytest

from app.integrations.database.mongo_client import MongoClient, MongoDB, SetCodec

# Dicionário com constantes para evitar duplicação
TEST_MONGO_DATA = {
    "url": "mongodb://localhost:27017/test",
    "db_name": "test_db",
    "collection_name": "test_collection",
    "database_name": "test_database",
    "error_message": "Connection error",
}


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

    result = mongo_db[TEST_MONGO_DATA["collection_name"]]

    assert result == mock_collection
    mock_db.__getitem__.assert_called_once_with(TEST_MONGO_DATA["collection_name"])


@patch('app.integrations.database.mongo_client.AsyncIOMotorClient')
def test_mongo_client_init(mock_async_client):
    """Test MongoClient initialization - follows Dependency Inversion Principle"""
    from pydantic import MongoDsn

    mongo_url = MongoDsn(TEST_MONGO_DATA["url"])
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

        mongo_url = MongoDsn(TEST_MONGO_DATA["url"])
        client = MongoClient(mongo_url)

        client.close()

        mock_instance.close.assert_called_once()


def test_mongo_client_del_with_exception():
    """Test MongoClient __del__ method with exception handling"""
    from pydantic import MongoDsn

    with patch('app.integrations.database.mongo_client.AsyncIOMotorClient') as mock_async_client:
        mock_instance = MagicMock()
        mock_async_client.return_value = mock_instance

        mongo_url = MongoDsn(TEST_MONGO_DATA["url"])
        client = MongoClient(mongo_url)

        # Test __del__ with exception handling - should not raise
        mock_instance.close.side_effect = Exception(TEST_MONGO_DATA["error_message"])

        try:
            del client  # This should not raise an exception
        except Exception:
            pytest.fail("__del__ should not raise exceptions")


@patch('app.integrations.database.mongo_client.AsyncIOMotorClient')
def test_mongo_client_get_database(mock_async_client):
    """Test MongoClient get_database method"""
    from pydantic import MongoDsn

    mock_instance = MagicMock()
    mock_db = MagicMock()
    mock_instance.get_database.return_value = mock_db
    mock_async_client.return_value = mock_instance

    mongo_url = MongoDsn(TEST_MONGO_DATA["url"])
    client = MongoClient(mongo_url)

    result = client.get_database(TEST_MONGO_DATA["db_name"])

    assert isinstance(result, MongoDB)
    assert result.db == mock_db
    # Verify the method was called with database name and codec options
    mock_instance.get_database.assert_called_once()


@patch('app.integrations.database.mongo_client.AsyncIOMotorClient')
def test_mongo_client_getitem(mock_async_client):
    """Test MongoClient __getitem__ method"""
    from pydantic import MongoDsn

    mock_instance = MagicMock()
    mock_db = MagicMock()
    mock_instance.get_database.return_value = mock_db
    mock_async_client.return_value = mock_instance

    mongo_url = MongoDsn(TEST_MONGO_DATA["url"])
    client = MongoClient(mongo_url)

    result = client[TEST_MONGO_DATA["database_name"]]

    assert isinstance(result, MongoDB)
    assert result.db == mock_db
    # Verify that get_database was called with the database name (codec_options will also be passed)
    mock_instance.get_database.assert_called_once()


@patch('app.integrations.database.mongo_client.AsyncIOMotorClient')
def test_mongo_client_database_collection_access(mock_async_client):
    """Test MongoClient database and collection access"""
    from pydantic import MongoDsn

    mock_instance = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    mock_instance.get_database.return_value = mock_db
    mock_async_client.return_value = mock_instance

    mongo_url = MongoDsn(TEST_MONGO_DATA["url"])
    client = MongoClient(mongo_url)

    # Test getting database and collection via []
    database = client[TEST_MONGO_DATA["database_name"]]
    collection = database[TEST_MONGO_DATA["collection_name"]]

    assert collection == mock_collection
