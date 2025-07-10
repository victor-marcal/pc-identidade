import pytest
from datetime import date, timedelta
from pydantic import ValidationError
from app.api.v1.schemas.seller_schema import SellerCreate, SellerResponse, SellerUpdate, SellerReplace
from app.models.enums import BrazilianState, AccountType, ProductCategory, SellerStatus


# --- DADOS DE TESTE ---

@pytest.fixture
def valid_data_dict() -> dict:
    """Fornece um dicionário com dados válidos para criar um seller."""
    return {
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
        "bank_name": "Banco Do Brasil",
        "agency_account": "1234-5 / 12345-6",
        "account_type": AccountType.CURRENT,
        "product_categories": [ProductCategory.AUDIO, ProductCategory.BOOKS],
        "business_description": "Comércio de eletrônicos e livros",
        "account_holder_name": "Empresa ABC Ltda"
    }


# --- TESTES DE VALIDAÇÃO EXISTENTES (Refatorados para usar a fixture) ---

def test_seller_create_valid(valid_data_dict):
    seller = SellerCreate(**valid_data_dict)
    assert seller.seller_id == "abc123"
    assert seller.bank_name == "banco do brasil"  # Testa normalização


def test_seller_response_valid(valid_data_dict):
    response_data = {**valid_data_dict, "status": SellerStatus.ACTIVE}
    seller = SellerResponse(**response_data)
    assert seller.status == SellerStatus.ACTIVE


def test_seller_update_valid_partial():
    seller = SellerUpdate(trade_name="Nova Loja ABC")
    assert seller.trade_name == "Nova Loja ABC"


def test_seller_replace_valid(valid_data_dict):
    seller = SellerReplace(**valid_data_dict)
    assert seller.cnpj == "12345678000100"


def test_invalid_seller_id_characters(valid_data_dict):
    with pytest.raises(ValidationError):
        SellerCreate(**{**valid_data_dict, "seller_id": "ABC_123"})


def test_invalid_nome_fantasia_short(valid_data_dict):
    with pytest.raises(ValidationError):
        SellerCreate(**{**valid_data_dict, "trade_name": "Lo"})


def test_invalid_cnpj_format(valid_data_dict):
    with pytest.raises(ValidationError):
        SellerCreate(**{**valid_data_dict, "cnpj": "12.345.678/0001-00"})


def test_seller_id_obrigatorio(valid_data_dict):
    with pytest.raises(ValidationError, match="O seller_id é obrigatório"):
        SellerCreate(**{**valid_data_dict, "seller_id": ""})


# --- NOVOS TESTES PARA AUMENTAR A COBERTURA ---

class TestValidators:
    """Agrupa testes para os validadores de campo na classe SellerBase."""

    def test_invalid_state_municipal_registration(self, valid_data_dict):
        with pytest.raises(ValidationError, match="Inscrição Estadual/Municipal deve conter apenas números"):
            SellerCreate(**{**valid_data_dict, "state_municipal_registration": "12345abc"})

    def test_invalid_cpf(self, valid_data_dict):
        with pytest.raises(ValidationError, match="CPF deve conter exatamente 11 dígitos numéricos"):
            SellerCreate(**{**valid_data_dict, "legal_rep_cpf": "1234567890"})
        with pytest.raises(ValidationError, match="CPF deve conter exatamente 11 dígitos numéricos"):
            SellerCreate(**{**valid_data_dict, "legal_rep_cpf": "1234567890a"})

    def test_invalid_rg_number(self, valid_data_dict):
        with pytest.raises(ValidationError, match="RG deve conter apenas números"):
            SellerCreate(**{**valid_data_dict, "legal_rep_rg_number": "123.456"})

    def test_future_birth_date(self, valid_data_dict):
        future_date = date.today() + timedelta(days=1)
        with pytest.raises(ValidationError, match="Data de nascimento não pode ser futura"):
            SellerCreate(**{**valid_data_dict, "legal_rep_birth_date": future_date})

    def test_phone_number_normalization(self, valid_data_dict):
        data = {**valid_data_dict, "contact_phone": "(11) 98765-4321"}
        seller = SellerCreate(**data)
        assert seller.contact_phone == "11987654321"

    def test_empty_product_categories(self, valid_data_dict):
        with pytest.raises(ValidationError, match="Pelo menos uma categoria de produto deve ser selecionada"):
            SellerCreate(**{**valid_data_dict, "product_categories": []})


class TestUpdateValidators:
    """Agrupa testes específicos para os validadores da classe SellerUpdate."""

    def test_update_with_none_values(self):
        """Testa se a classe aceita campos nulos, cobrindo os 'if v is not None'."""
        try:
            SellerUpdate(trade_name=None, cnpj=None, product_categories=None)
        except ValidationError:
            pytest.fail("SellerUpdate não deveria falhar com campos nulos.")

    def test_update_invalid_trade_name(self):
        """Testa a validação de nome fantasia curto no SellerUpdate."""
        with pytest.raises(ValidationError, match="O nome_fantasia deve conter ao menos 3 caracteres"):
            SellerUpdate(trade_name="Lo")

    def test_update_invalid_cnpj(self):
        """Testa a validação de formato de CNPJ no SellerUpdate."""
        with pytest.raises(ValidationError, match="O CNPJ deve conter exatamente 14 dígitos numéricos"):
            SellerUpdate(cnpj="12345")

    def test_update_invalid_cpf(self):
        """Testa a validação de formato de CPF no SellerUpdate."""
        with pytest.raises(ValidationError, match="CPF deve conter exatamente 11 dígitos numéricos"):
            SellerUpdate(legal_rep_cpf="1234567890a")

    def test_update_future_birth_date(self):
        """Testa se a atualização da data de nascimento rejeita datas futuras."""
        future_date = date.today() + timedelta(days=1)
        with pytest.raises(ValidationError, match="Data de nascimento não pode ser futura"):
            SellerUpdate(legal_rep_birth_date=future_date)

    def test_update_with_empty_product_categories(self):
        """Testa se a atualização com uma lista de categorias vazia é rejeitada."""
        with pytest.raises(ValidationError, match="Pelo menos uma categoria de produto deve ser selecionada"):
            SellerUpdate(product_categories=[])
