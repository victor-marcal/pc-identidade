import pytest
from datetime import date
from pydantic import ValidationError
from app.api.v1.schemas.seller_schema import SellerCreate, SellerResponse, SellerUpdate, SellerReplace
from app.models.enums import BrazilianState, AccountType, ProductCategory, SellerStatus

# Dados válidos atualizados para o novo schema
valid_data = {
    "seller_id": "abc123",
    "company_name": "Empresa ABC Ltda",
    "trade_name": "Loja ABC",
    "cnpj": "12345678000100",
    "state_municipal_registration": "123456789",
    "commercial_address": "Rua das Flores, 123, Centro, São Paulo, SP",
    "contact_phone": "11987654321",
    "contact_email": "contato@empresa.com",
    "legal_rep_full_name": "João Silva",
    "legal_rep_cpf": "12345678901",
    "legal_rep_rg_number": "123456789",
    "legal_rep_rg_state": BrazilianState.SP,
    "legal_rep_birth_date": date(1980, 5, 15),
    "legal_rep_phone": "11987654321",
    "legal_rep_email": "joao@empresa.com",
    "bank_name": "Banco do Brasil",
    "agency_account": "1234-5 / 12345-6",
    "account_type": AccountType.CURRENT,
    "account_holder_name": "João Silva",
    "product_categories": [ProductCategory.AUDIO, ProductCategory.BOOKS],
    "business_description": "Comércio de eletrônicos e livros"
}

TEST_SELLER_SCHEMA_DATA = {
    "nova_loja": "Nova Loja ABC",
    "cnpj_new": "98765432000111",
    "short_name": "Lo",
    "invalid_seller_id": "ABC_123",
    "cnpj_formatted": "12.345.678/0001-00",
    "cnpj_short": "123",
    "whitespace": "  ",
    "empty_string": "",
}


def test_seller_create_valid():
    seller = SellerCreate(**valid_data)
    assert seller.seller_id == "abc123"
    assert seller.trade_name == "Loja ABC"


def test_seller_response_valid():
    response_data = {**valid_data, "status": SellerStatus.ACTIVE}
    seller = SellerResponse(**response_data)
    assert seller.seller_id == "abc123"
    assert seller.cnpj == "12345678000100"


def test_seller_update_valid_partial():
    seller = SellerUpdate(trade_name=TEST_SELLER_SCHEMA_DATA["nova_loja"])
    assert seller.trade_name == TEST_SELLER_SCHEMA_DATA["nova_loja"]


def test_seller_replace_valid():
    data = {**valid_data}
    data["trade_name"] = TEST_SELLER_SCHEMA_DATA["nova_loja"]
    data["cnpj"] = TEST_SELLER_SCHEMA_DATA["cnpj_new"]
    seller = SellerReplace(**data)
    assert seller.trade_name == TEST_SELLER_SCHEMA_DATA["nova_loja"]
    assert seller.cnpj == TEST_SELLER_SCHEMA_DATA["cnpj_new"]


def test_invalid_seller_id_characters():
    with pytest.raises(ValidationError):
        SellerCreate(**{**valid_data, "seller_id": TEST_SELLER_SCHEMA_DATA["invalid_seller_id"]})


def test_invalid_nome_fantasia_short():
    with pytest.raises(ValidationError):
        SellerCreate(**{**valid_data, "trade_name": TEST_SELLER_SCHEMA_DATA["short_name"]})


def test_invalid_cnpj_format():
    with pytest.raises(ValidationError):
        SellerCreate(**{**valid_data, "cnpj": TEST_SELLER_SCHEMA_DATA["cnpj_formatted"]})


def test_update_invalid_nome_fantasia():
    with pytest.raises(ValidationError):
        SellerUpdate(trade_name=TEST_SELLER_SCHEMA_DATA["whitespace"])


def test_replace_invalid_cnpj_length():
    with pytest.raises(ValidationError):
        SellerReplace(**{**valid_data, "cnpj": TEST_SELLER_SCHEMA_DATA["cnpj_short"]})


def test_seller_id_obrigatorio():
    with pytest.raises(ValidationError) as exc_info:
        SellerCreate(**{**valid_data, "seller_id": TEST_SELLER_SCHEMA_DATA["empty_string"]})
    assert "O seller_id é obrigatório" in str(exc_info.value)
