import pytest
from pydantic import ValidationError

from app.api.v1.schemas.seller_schema import SellerCreate, SellerReplace, SellerResponse, SellerUpdate

valid_data = {"seller_id": "abc123", "nome_fantasia": "Loja Teste", "cnpj": "12345678000100"}


def test_seller_create_valid():
    seller = SellerCreate(**valid_data)
    assert seller.seller_id == "abc123"


def test_seller_response_valid():
    seller = SellerResponse(**valid_data)
    assert seller.cnpj == "12345678000100"


def test_seller_update_valid_partial():
    seller = SellerUpdate(nome_fantasia="Nova Loja")
    assert seller.nome_fantasia == "Nova Loja"


def test_seller_replace_valid():
    data = {"nome_fantasia": "Nova Loja", "cnpj": "12345678901234"}
    seller = SellerReplace(**data)
    assert seller.cnpj == "12345678901234"


def test_invalid_seller_id_characters():
    with pytest.raises(ValidationError):
        SellerCreate(**{**valid_data, "seller_id": "ABC_123"})


def test_invalid_nome_fantasia_short():
    with pytest.raises(ValidationError):
        SellerCreate(**{**valid_data, "nome_fantasia": "Lo"})


def test_invalid_cnpj_format():
    with pytest.raises(ValidationError):
        SellerCreate(**{**valid_data, "cnpj": "12.345.678/0001-00"})


def test_update_invalid_nome_fantasia():
    with pytest.raises(ValidationError):
        SellerUpdate(nome_fantasia="  ")


def test_replace_invalid_cnpj_length():
    with pytest.raises(ValidationError):
        SellerReplace(nome_fantasia="Loja Boa", cnpj="123")


def test_seller_id_obrigatorio():
    with pytest.raises(ValidationError) as exc_info:
        SellerCreate(seller_id="", nome_fantasia="Loja", cnpj="12345678901234")
    assert "O seller_id é obrigatório." in str(exc_info.value)
