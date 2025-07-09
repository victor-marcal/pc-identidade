# Dados de teste atualizados para schemas do Seller
from datetime import date
from app.models.enums import BrazilianState, AccountType, ProductCategory

VALID_SELLER_DATA = {
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
    "account_type": AccountType.CHECKING,
    "account_holder_name": "João Silva1",
    "product_categories": [ProductCategory.ELECTRONICS, ProductCategory.BOOKS],
    "business_description": "Comércio de eletrônicos e livros"
}

VALID_SELLER_UPDATE = {
    "trade_name": "Nova Loja ABC",
    "contact_phone": "11999888777"
}

def create_valid_seller_auth_info():
    """Cria UserAuthInfo válido com todos os campos necessários"""
    from app.api.common.auth_handler import UserAuthInfo
    from app.models.base import UserModel
    
    return UserAuthInfo(
        user=UserModel(name="test-user-123", server="https://keycloak/realms/test"),
        trace_id="test-trace-id",
        sellers=["abc123"],
        info_token={"sub": "test-user-123", "iss": "https://keycloak/realms/test"}
    )
