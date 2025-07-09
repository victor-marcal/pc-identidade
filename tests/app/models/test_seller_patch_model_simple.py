"""
Testes simples para melhorar cobertura de seller_patch_model.py
"""

import pytest
from datetime import date
from app.models.seller_patch_model import SellerPatch
from app.models.enums import SellerStatus, BrazilianState, AccountType, ProductCategory

TEST_COMPANY = "Test Company"
EMAIL_TESTE = "test@example.com"

class TestSellerPatch:
    """Testes para SellerPatch"""

    def test_seller_patch_empty_creation(self):
        """Testa criação vazia do SellerPatch"""
        SellerPatch()

    def test_seller_patch_with_company_name(self):
        """Testa criação com nome da empresa"""
        patch = SellerPatch(company_name=TEST_COMPANY)
        assert patch.company_name == TEST_COMPANY

    def test_seller_patch_with_trade_name(self):
        """Testa criação com nome fantasia"""
        patch = SellerPatch(trade_name="Test Trade Name")
        assert patch.trade_name == "Test Trade Name"

    def test_seller_patch_with_cnpj(self):
        """Testa criação com CNPJ"""
        patch = SellerPatch(cnpj="12345678901234")
        assert patch.cnpj == "12345678901234"

    def test_seller_patch_with_contact_phone(self):
        """Testa criação com telefone de contato"""
        patch = SellerPatch(contact_phone="11999999999")
        assert patch.contact_phone == "11999999999"

    def test_seller_patch_with_contact_email(self):
        """Testa criação com email de contato"""
        patch = SellerPatch(contact_email=EMAIL_TESTE)
        assert patch.contact_email == EMAIL_TESTE

    def test_seller_patch_with_legal_rep_info(self):
        """Testa criação com informações do representante legal"""
        patch = SellerPatch(
            legal_rep_full_name="John Doe",
            legal_rep_cpf="12345678901",
            legal_rep_rg_number="123456789",
            legal_rep_rg_state=BrazilianState.SP,
            legal_rep_birth_date=date(1990, 1, 1),
            legal_rep_phone="11999999999",
            legal_rep_email="john@example.com"
        )
        assert patch.legal_rep_full_name == "John Doe"
        assert patch.legal_rep_cpf == "12345678901"

    def test_seller_patch_with_banking_info(self):
        """Testa criação com informações bancárias"""
        patch = SellerPatch(
            bank_name="Banco do Brasil",
            agency_account="0001-1",
            account_type=AccountType.CURRENT,
            account_holder_name="Test Holder"
        )
        assert patch.bank_name == "banco do brasil"  # lowercase validation
        assert patch.agency_account == "0001-1"

    def test_seller_patch_with_product_categories(self):
        """Testa criação com categorias de produtos"""
        patch = SellerPatch(
            product_categories=[ProductCategory.AUTOMOTIVE, ProductCategory.BABY]
        )
        assert len(patch.product_categories) == 2

    def test_seller_patch_dict_conversion(self):
        """Testa conversão para dicionário"""
        patch = SellerPatch(company_name=TEST_COMPANY)
        patch_dict = patch.model_dump()
        assert isinstance(patch_dict, dict)
        assert patch_dict["company_name"] == TEST_COMPANY

    def test_seller_patch_cnpj_validation(self):
        """Testa validação de CNPJ"""
        # CNPJ válido
        patch = SellerPatch(cnpj="12345678901234")
        assert patch.cnpj == "12345678901234"
        
    def test_seller_patch_trade_name_validation(self):
        """Testa validação de nome fantasia"""
        patch = SellerPatch(trade_name="Valid Trade Name")
        assert patch.trade_name == "Valid Trade Name"

    def test_seller_patch_phone_validation(self):
        """Testa validação de telefone"""
        patch = SellerPatch(contact_phone="(11) 99999-9999")
        assert patch.contact_phone == "11999999999"  # Remove formatting

    def test_seller_patch_business_description(self):
        """Testa descrição do negócio"""
        patch = SellerPatch(business_description="Test business description")
        assert patch.business_description == "Test business description"

    def test_seller_patch_state_registration(self):
        """Testa inscrição estadual"""
        patch = SellerPatch(state_municipal_registration="12345678")
        assert patch.state_municipal_registration == "12345678"

    def test_seller_patch_commercial_address(self):
        """Testa endereço comercial"""
        patch = SellerPatch(commercial_address="Test Address, 123")
        assert patch.commercial_address == "Test Address, 123"

    def test_seller_patch_model_dump_exclude_none(self):
        """Testa dump do modelo excluindo valores None"""
        patch = SellerPatch(company_name=TEST_COMPANY)
        patch_dict = patch.model_dump(exclude_none=True)
        assert "company_name" in patch_dict
        assert patch_dict["company_name"] == TEST_COMPANY

    def test_seller_patch_multiple_fields(self):
        """Testa criação com múltiplos campos"""
        patch = SellerPatch(
            company_name=TEST_COMPANY,
            trade_name="Test Trade",
            cnpj="12345678901234",
            contact_phone="11999999999",
            contact_email=EMAIL_TESTE
        )
        assert patch.company_name == TEST_COMPANY
        assert patch.trade_name == "Test Trade"
        assert patch.cnpj == "12345678901234"
        assert patch.contact_phone == "11999999999"
        assert patch.contact_email == EMAIL_TESTE
