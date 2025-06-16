from fastapi import status
from app.models.seller_model import Seller


def test_get_sellers(client, mock_seller_service):
    mock_seller_service.find.return_value = [Seller(seller_id="1", nome_fantasia="Teste", cnpj="12345678000100")]

    response = client.get("/seller/v1/sellers")

    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.json()
    assert response.json()["results"][0]["seller_id"] == "1"


def test_get_by_id(client, mock_seller_service):
    mock_seller_service.find_by_id.return_value = Seller(seller_id="1", nome_fantasia="Teste", cnpj="12345678000100")

    response = client.get("/seller/v1/sellers/buscar?seller_id=1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["seller_id"] == "1"


def test_get_by_cnpj(client, mock_seller_service):
    mock_seller_service.find_by_cnpj.return_value = Seller(seller_id="1", nome_fantasia="Teste", cnpj="12345678000100")

    response = client.get("/seller/v1/sellers/buscar?cnpj=12345678000100")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["cnpj"] == "12345678000100"


def test_create_seller(client, mock_seller_service):
    seller_data = {"seller_id": "1", "nome_fantasia": "Teste", "cnpj": "12345678000100"}
    mock_seller_service.create.return_value = Seller(**seller_data)

    response = client.post("/seller/v1/sellers", json=seller_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["seller_id"] == "1"


def test_update_seller(client, mock_seller_service):
    updated = Seller(seller_id="1", nome_fantasia="Atualizado", cnpj="12345678000100")
    mock_seller_service.update.return_value = updated

    response = client.patch("/seller/v1/sellers/1", json={"nome_fantasia": "Atualizado"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["nome_fantasia"] == "Atualizado"


def test_replace_seller(client, mock_seller_service):
    replaced = Seller(seller_id="1", nome_fantasia="Novo", cnpj="12345678000100")
    mock_seller_service.replace.return_value = replaced

    response = client.put("/seller/v1/sellers/1", json={"nome_fantasia": "Novo", "cnpj": "12345678000100"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["nome_fantasia"] == "Novo"


def test_delete_seller(client, mock_seller_service):
    mock_seller_service.delete_by_id.return_value = None

    response = client.delete("/seller/v1/sellers/1")

    assert response.status_code == status.HTTP_204_NO_CONTENT
