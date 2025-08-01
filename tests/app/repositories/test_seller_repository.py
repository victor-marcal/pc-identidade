from unittest import mock

import pytest

from app.models.seller_model import Seller
from app.repositories.seller_repository import SellerRepository
from tests.helpers.test_fixtures import create_minimal_seller_dict

NOME_FANTASIA = "Loja Legal"
LOJA = "Loja Trade Name"


@pytest.mark.asyncio
class TestSellerRepository:
    async def test_find_by_nome_fantasia(self, mock_mongo_client):
        client, collection = mock_mongo_client
        collection.find_one = mock.AsyncMock(
            return_value=create_minimal_seller_dict(seller_id="seller01", trade_name=NOME_FANTASIA)
        )

        repo = SellerRepository(client, "test_db")
        result = await repo.find_by_nome_fantasia(NOME_FANTASIA)

        collection.find_one.assert_called_once_with({"nome_fantasia": NOME_FANTASIA})
        assert isinstance(result, Seller)
        assert result.trade_name == NOME_FANTASIA

    async def test_find_by_nome_fantasia_not_found(self, mock_mongo_client):
        client, collection = mock_mongo_client
        collection.find_one = mock.AsyncMock(return_value=None)

        repo = SellerRepository(client, "test_db")
        result = await repo.find_by_nome_fantasia("Loja Inexistente")

        assert result is None

    async def test_find_by_cnpj(self, mock_mongo_client):
        client, collection = mock_mongo_client
        collection.find_one = mock.AsyncMock(
            return_value=create_minimal_seller_dict(seller_id="seller02", trade_name="Loja CNPJ", cnpj="99887766554433")
        )

        repo = SellerRepository(client, "test_db")
        result = await repo.find_by_cnpj("99887766554433")

        collection.find_one.assert_called_once_with({"cnpj": "99887766554433"})
        assert isinstance(result, Seller)
        assert result.cnpj == "99887766554433"

    async def test_find_by_cnpj_not_found(self, mock_mongo_client):
        client, collection = mock_mongo_client
        collection.find_one = mock.AsyncMock(return_value=None)

        repo = SellerRepository(client, "test_db")
        result = await repo.find_by_cnpj("00000000000000")

        assert result is None

    async def test_find_by_trade_name(self, mock_mongo_client):
        client, collection = mock_mongo_client
        collection.find_one = mock.AsyncMock(
            return_value=create_minimal_seller_dict(seller_id="seller03", trade_name=LOJA)
        )

        repo = SellerRepository(client, "test_db")
        result = await repo.find_by_trade_name(LOJA)

        collection.find_one.assert_called_once_with({"trade_name": LOJA})
        assert isinstance(result, Seller)
        assert result.trade_name == LOJA

    async def test_find_by_trade_name_not_found(self, mock_mongo_client):
        client, collection = mock_mongo_client
        collection.find_one = mock.AsyncMock(return_value=None)

        repo = SellerRepository(client, "test_db")
        result = await repo.find_by_trade_name("Loja Inexistente")

        assert result is None
