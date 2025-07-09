"""
Helper functions and fixtures for creating test data with all required fields.
"""

from datetime import date
from app.models.seller_model import Seller
from app.models.enums import BrazilianState, AccountType, ProductCategory, SellerStatus
from app.api.v1.schemas.seller_schema import SellerCreate, SellerResponse

LOJA_TESTE = "Loja Teste"

def create_full_seller(**overrides) -> Seller:
    """Create a Seller with all required fields."""
    default_data = {
        "seller_id": "test001",
        "status": SellerStatus.ACTIVE,
        "company_name": "Empresa Teste1 Ltda",
        "trade_name": LOJA_TESTE,
        "cnpj": "12345678000199",
        "state_municipal_registration": "123456789",
        "commercial_address": "Rua Teste, 123",
        "contact_phone": "11999999999",
        "contact_email": "contato1@teste.com",
        "legal_rep_full_name": "João Silva3",
        "legal_rep_cpf": "12345678901",
        "legal_rep_rg_number": "123456789",
        "legal_rep_rg_state": BrazilianState.SP,
        "legal_rep_birth_date": date(1990, 1, 1),
        "legal_rep_phone": "11888888888",
        "legal_rep_email": "joao@teste.com",
        "bank_name": "Banco do Brasil2",
        "agency_account": "1234-5/67890-2",
        "account_type": AccountType.CURRENT,
        "account_holder_name": "Empresa Teste2 Ltda",
        "product_categories": [ProductCategory.COMPUTING],
        "business_description": "beleza e perfumaria",
        "created_by": "system:test"
    }
    default_data.update(overrides)
    return Seller(**default_data)


def create_seller_create(**overrides) -> SellerCreate:
    """Create a SellerCreate with all required fields."""
    default_data = {
        "seller_id": "test001",
        "company_name": "Empresa Teste3 Ltda",
        "trade_name": LOJA_TESTE,
        "cnpj": "12345678000199",
        "state_municipal_registration": "123456789",
        "commercial_address": "Rua Teste, 1237",
        "contact_phone": "11999999999",
        "contact_email": "contato@teste.com",
        "legal_rep_full_name": "João Silva2",
        "legal_rep_cpf": "12345678901",
        "legal_rep_rg_number": "123456789",
        "legal_rep_rg_state": BrazilianState.SP,
        "legal_rep_birth_date": date(1990, 1, 1),
        "legal_rep_phone": "11888888888",
        "legal_rep_email": "joao4@teste.com",
        "bank_name": "Banco do Brasil3",
        "agency_account": "1234-5/67890-3",
        "account_type": AccountType.CURRENT,
        "account_holder_name": "Empresa Teste4 Ltda",
        "product_categories": [ProductCategory.COMPUTING],
        "business_description": "Áudio"
    }
    default_data.update(overrides)
    return SellerCreate(**default_data)


def create_minimal_seller_dict(**overrides) -> dict:
    """Create a dict with minimal Seller data for mocking database returns."""
    default_data = {
        "seller_id": "test001",
        "status": SellerStatus.ACTIVE.value,
        "company_name": "Empresa Teste Ltda",
        "trade_name": LOJA_TESTE,
        "cnpj": "12345678000199",
        "state_municipal_registration": "123456789",
        "commercial_address": "Rua Teste, 1236",
        "contact_phone": "11999999999",
        "contact_email": "contato2@teste.com",
        "legal_rep_full_name": "João Silva1",
        "legal_rep_cpf": "12345678901",
        "legal_rep_rg_number": "123456789",
        "legal_rep_rg_state": BrazilianState.SP.value,
        "legal_rep_birth_date": date(1990, 1, 1),
        "legal_rep_phone": "11888888888",
        "legal_rep_email": "joao3@teste.com",
        "bank_name": "Banco do Brasil1",
        "agency_account": "1234-5/67890-4",
        "account_type": AccountType.CURRENT.value,
        "account_holder_name": "Empresa Teste5 Ltda",
        "product_categories": [ProductCategory.COMPUTING.value],
        "business_description": "Bebê",
        "created_by": "system:test2"
    }
    default_data.update(overrides)
    return default_data


def create_legacy_seller_dict(**overrides) -> dict:
    """Create a dict with legacy field names for mocking database returns."""
    default_data = {
        "seller_id": "test001",
        "status": SellerStatus.ACTIVE.value,
        "company_name": "Empresa Teste9 Ltda",
        "nome_fantasia": LOJA_TESTE,
        "cnpj": "12345678000199",
        "state_municipal_registration": "123456789",
        "commercial_address": "Rua Teste, 1235",
        "contact_phone": "11999999999",
        "contact_email": "contato3@teste.com",
        "legal_rep_full_name": "João Pedro",
        "legal_rep_cpf": "12345678901",
        "legal_rep_rg_number": "123456789",
        "legal_rep_rg_state": BrazilianState.SP.value,
        "legal_rep_birth_date": date(1990, 1, 1),
        "legal_rep_phone": "11888888888",
        "legal_rep_email": "joao1@teste.com",
        "bank_name": "Banco do Brasil4",
        "agency_account": "1234-5/67890-5",
        "account_type": AccountType.CURRENT.value,
        "account_holder_name": "Empresa Teste6 Ltda",
        "product_categories": [ProductCategory.COMPUTING.value],
        "business_description": "Automotivo",
        "created_by": "system:test1"
    }
    default_data.update(overrides)
    return default_data


def create_seller_response(**overrides) -> SellerResponse:
    """Create a SellerResponse with all required fields."""
    default_data = {
        "seller_id": "test001",
        "status": SellerStatus.ACTIVE,
        "company_name": "Empresa Teste7 Ltda",
        "trade_name": LOJA_TESTE,
        "cnpj": "12345678000199",
        "state_municipal_registration": "123456789",
        "commercial_address": "Rua Teste, 1234",
        "contact_phone": "11999999999",
        "contact_email": "contato4@teste.com",
        "legal_rep_full_name": "João Silva",
        "legal_rep_cpf": "12345678901",
        "legal_rep_rg_number": "123456789",
        "legal_rep_rg_state": BrazilianState.SP,
        "legal_rep_birth_date": date(1990, 1, 1),
        "legal_rep_phone": "11888888888",
        "legal_rep_email": "joao2@teste.com",
        "bank_name": "Banco do Brasil",
        "agency_account": "1234-5/67890-1",
        "account_type": AccountType.CURRENT,
        "account_holder_name": "Empresa Teste8 Ltda",
        "product_categories": [ProductCategory.COMPUTING],
        "business_description": "brinquedos"
    }
    default_data.update(overrides)
    return SellerResponse(**default_data)
