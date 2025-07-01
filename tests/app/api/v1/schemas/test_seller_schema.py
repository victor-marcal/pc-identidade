import pytest
from pydantic import ValidationError

from app.api.v1.schemas.seller_schema import SellerCreate, SellerReplace, SellerResponse, SellerUpdate

# Dicionário com constantes para evitar duplicação
TEST_SELLER_SCHEMA_DATA = {
    "nova_loja": "Nova Loja",
    "loja_teste": "Loja Teste",
    "loja_boa": "Loja Boa",
    "seller_id": "abc123",
    "cnpj_valid": "12345678000100",
    "cnpj_new": "12345678901234",
    "cnpj_short": "123",
    "invalid_seller_id": "ABC_123",
    "short_name": "Lo",
    "cnpj_formatted": "12.345.678/0001-00",
    "whitespace": "  ",
    "empty_string": "",
    "loja": "Loja",
    "required_message": "O seller_id é obrigatório.",
}

valid_data = {
    "seller_id": TEST_SELLER_SCHEMA_DATA["seller_id"],
    "nome_fantasia": TEST_SELLER_SCHEMA_DATA["loja_teste"],
    "cnpj": TEST_SELLER_SCHEMA_DATA["cnpj_valid"],
}


def test_seller_create_valid():
    seller = SellerCreate(**valid_data)
    assert seller.seller_id == TEST_SELLER_SCHEMA_DATA["seller_id"]


def test_seller_response_valid():
    seller = SellerResponse(**valid_data)
    assert seller.cnpj == TEST_SELLER_SCHEMA_DATA["cnpj_valid"]


def test_seller_update_valid_partial():
    seller = SellerUpdate(nome_fantasia=TEST_SELLER_SCHEMA_DATA["nova_loja"])
    assert seller.nome_fantasia == TEST_SELLER_SCHEMA_DATA["nova_loja"]


def test_seller_replace_valid():
    data = {"nome_fantasia": TEST_SELLER_SCHEMA_DATA["nova_loja"], "cnpj": TEST_SELLER_SCHEMA_DATA["cnpj_new"]}
    seller = SellerReplace(**data)
    assert seller.cnpj == TEST_SELLER_SCHEMA_DATA["cnpj_new"]


def test_invalid_seller_id_characters():
    with pytest.raises(ValidationError):
        SellerCreate(**{**valid_data, "seller_id": TEST_SELLER_SCHEMA_DATA["invalid_seller_id"]})


def test_invalid_nome_fantasia_short():
    with pytest.raises(ValidationError):
        SellerCreate(**{**valid_data, "nome_fantasia": TEST_SELLER_SCHEMA_DATA["short_name"]})


def test_invalid_cnpj_format():
    with pytest.raises(ValidationError):
        SellerCreate(**{**valid_data, "cnpj": TEST_SELLER_SCHEMA_DATA["cnpj_formatted"]})


def test_update_invalid_nome_fantasia():
    with pytest.raises(ValidationError):
        SellerUpdate(nome_fantasia=TEST_SELLER_SCHEMA_DATA["whitespace"])


def test_replace_invalid_cnpj_length():
    with pytest.raises(ValidationError):
        SellerReplace(nome_fantasia=TEST_SELLER_SCHEMA_DATA["loja_boa"], cnpj=TEST_SELLER_SCHEMA_DATA["cnpj_short"])


def test_seller_id_obrigatorio():
    with pytest.raises(ValidationError) as exc_info:
        SellerCreate(
            seller_id=TEST_SELLER_SCHEMA_DATA["empty_string"],
            nome_fantasia=TEST_SELLER_SCHEMA_DATA["loja"],
            cnpj=TEST_SELLER_SCHEMA_DATA["cnpj_new"],
        )
    assert TEST_SELLER_SCHEMA_DATA["required_message"] in str(exc_info.value)
