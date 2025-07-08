"""
Helper functions and fixtures for creating test data with all required fields.
"""

from datetime import date
from app.models.seller_model import Seller
from app.models.enums import BrazilianState, AccountType, ProductCategory, SellerStatus
from app.api.v1.schemas.seller_schema import SellerCreate, SellerResponse


def create_full_seller(**overrides) -> Seller:
    """Create a Seller with all required fields."""
    default_data = {
        "seller_id": "test001",
        "status": SellerStatus.ACTIVE,
        "company_name": "Empresa Teste Ltda",
        "trade_name": "Loja Teste",
        "cnpj": "12345678000199",
        "state_municipal_registration": "123456789",
        "commercial_address": "Rua Teste, 123",
        "contact_phone": "11999999999",
        "contact_email": "contato@teste.com",
        "legal_rep_full_name": "João Silva",
        "legal_rep_cpf": "12345678901",
        "legal_rep_rg_number": "123456789",
        "legal_rep_rg_state": BrazilianState.SP,
        "legal_rep_birth_date": date(1990, 1, 1),
        "legal_rep_phone": "11888888888",
        "legal_rep_email": "joao@teste.com",
        "bank_name": "Banco do Brasil",
        "agency_account": "1234-5/67890-1",
        "account_type": AccountType.CURRENT,
        "account_holder_name": "Empresa Teste Ltda",
        "product_categories": [ProductCategory.COMPUTING],
        "business_description": "Venda de produtos eletrônicos",
        "created_by": "system:test"
    }
    default_data.update(overrides)
    return Seller(**default_data)


def create_seller_create(**overrides) -> SellerCreate:
    """Create a SellerCreate with all required fields."""
    default_data = {
        "seller_id": "test001",
        "company_name": "Empresa Teste Ltda",
        "trade_name": "Loja Teste",
        "cnpj": "12345678000199",
        "state_municipal_registration": "123456789",
        "commercial_address": "Rua Teste, 123",
        "contact_phone": "11999999999",
        "contact_email": "contato@teste.com",
        "legal_rep_full_name": "João Silva",
        "legal_rep_cpf": "12345678901",
        "legal_rep_rg_number": "123456789",
        "legal_rep_rg_state": BrazilianState.SP,
        "legal_rep_birth_date": date(1990, 1, 1),
        "legal_rep_phone": "11888888888",
        "legal_rep_email": "joao@teste.com",
        "bank_name": "Banco do Brasil",
        "agency_account": "1234-5/67890-1",
        "account_type": AccountType.CURRENT,
        "account_holder_name": "Empresa Teste Ltda",
        "product_categories": [ProductCategory.COMPUTING],
        "business_description": "Venda de produtos eletrônicos"
    }
    default_data.update(overrides)
    return SellerCreate(**default_data)


def create_minimal_seller_dict(**overrides) -> dict:
    """Create a dict with minimal Seller data for mocking database returns."""
    default_data = {
        "seller_id": "test001",
        "status": SellerStatus.ACTIVE.value,
        "company_name": "Empresa Teste Ltda",
        "trade_name": "Loja Teste",
        "cnpj": "12345678000199",
        "state_municipal_registration": "123456789",
        "commercial_address": "Rua Teste, 123",
        "contact_phone": "11999999999",
        "contact_email": "contato@teste.com",
        "legal_rep_full_name": "João Silva",
        "legal_rep_cpf": "12345678901",
        "legal_rep_rg_number": "123456789",
        "legal_rep_rg_state": BrazilianState.SP.value,
        "legal_rep_birth_date": date(1990, 1, 1),
        "legal_rep_phone": "11888888888",
        "legal_rep_email": "joao@teste.com",
        "bank_name": "Banco do Brasil",
        "agency_account": "1234-5/67890-1",
        "account_type": AccountType.CURRENT.value,
        "account_holder_name": "Empresa Teste Ltda",
        "product_categories": [ProductCategory.COMPUTING.value],
        "business_description": "Venda de produtos eletrônicos",
        "created_by": "system:test"
    }
    default_data.update(overrides)
    return default_data


def create_legacy_seller_dict(**overrides) -> dict:
    """Create a dict with legacy field names for mocking database returns."""
    default_data = {
        "seller_id": "test001",
        "status": SellerStatus.ACTIVE.value,
        "company_name": "Empresa Teste Ltda",
        "nome_fantasia": "Loja Teste",  # Legacy field name
        "cnpj": "12345678000199",
        "state_municipal_registration": "123456789",
        "commercial_address": "Rua Teste, 123",
        "contact_phone": "11999999999",
        "contact_email": "contato@teste.com",
        "legal_rep_full_name": "João Silva",
        "legal_rep_cpf": "12345678901",
        "legal_rep_rg_number": "123456789",
        "legal_rep_rg_state": BrazilianState.SP.value,
        "legal_rep_birth_date": date(1990, 1, 1),
        "legal_rep_phone": "11888888888",
        "legal_rep_email": "joao@teste.com",
        "bank_name": "Banco do Brasil",
        "agency_account": "1234-5/67890-1",
        "account_type": AccountType.CURRENT.value,
        "account_holder_name": "Empresa Teste Ltda",
        "product_categories": [ProductCategory.COMPUTING.value],
        "business_description": "Venda de produtos eletrônicos",
        "created_by": "system:test"
    }
    default_data.update(overrides)
    return default_data


def create_seller_response(**overrides) -> SellerResponse:
    """Create a SellerResponse with all required fields."""
    default_data = {
        "seller_id": "test001",
        "status": SellerStatus.ACTIVE,
        "company_name": "Empresa Teste Ltda",
        "trade_name": "Loja Teste",
        "cnpj": "12345678000199",
        "state_municipal_registration": "123456789",
        "commercial_address": "Rua Teste, 123",
        "contact_phone": "11999999999",
        "contact_email": "contato@teste.com",
        "legal_rep_full_name": "João Silva",
        "legal_rep_cpf": "12345678901",
        "legal_rep_rg_number": "123456789",
        "legal_rep_rg_state": BrazilianState.SP,
        "legal_rep_birth_date": date(1990, 1, 1),
        "legal_rep_phone": "11888888888",
        "legal_rep_email": "joao@teste.com",
        "bank_name": "Banco do Brasil",
        "agency_account": "1234-5/67890-1",
        "account_type": AccountType.CURRENT,
        "account_holder_name": "Empresa Teste Ltda",
        "product_categories": [ProductCategory.COMPUTING],
        "business_description": "Venda de produtos eletrônicos"
    }
    default_data.update(overrides)
    return SellerResponse(**default_data)
