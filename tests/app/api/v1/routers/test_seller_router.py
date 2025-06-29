from unittest.mock import AsyncMock
from starlette.testclient import TestClient
from starlette import status

from app.models.seller_model import Seller

SELLER_BASE = "/seller/v1/sellers"


def test_get_all_sellers(client: TestClient, mock_seller_service: AsyncMock):
    sellers_list = [Seller(seller_id="1", nome_fantasia="Teste", cnpj="12345678000100")]
    mock_seller_service.find.return_value = sellers_list

    response = client.get(SELLER_BASE)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"][0]["seller_id"] == "1"
    mock_seller_service.find.assert_called_once()

def test_create_seller(client: TestClient, mock_seller_service: AsyncMock):
    new_seller_data = {"seller_id": "2", "nome_fantasia": "Novo", "cnpj": "12345678000101"}
    mock_seller_service.create.return_value = Seller(**new_seller_data)

    response = client.post(SELLER_BASE, json=new_seller_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["nome_fantasia"] == "Novo"
    mock_seller_service.create.assert_called_once()


def test_update_seller(client: TestClient, mock_seller_service: AsyncMock):
    updated_seller = Seller(seller_id="1", nome_fantasia="Atualizado", cnpj="12345678000100")
    mock_seller_service.update.return_value = updated_seller

    response = client.patch(f"{SELLER_BASE}/1", json={"nome_fantasia": "Atualizado"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["nome_fantasia"] == "Atualizado"
    mock_seller_service.update.assert_called_once()

def test_get_by_id_protected(client: TestClient, mock_seller_service: AsyncMock):
    seller = Seller(seller_id="luizalabs", nome_fantasia="Magalu", cnpj="12345678000100")
    mock_seller_service.find_by_id.return_value = seller

    response = client.get(f"{SELLER_BASE}/luizalabs")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["seller_id"] == "luizalabs"
    mock_seller_service.find_by_id.assert_called_once_with("luizalabs")
