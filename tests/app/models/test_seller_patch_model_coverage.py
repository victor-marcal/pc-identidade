"""
Testes adicionais para seller_patch_model.py visando 100% de cobertura
"""

import pytest
from pydantic import ValidationError
from datetime import date
from app.models.seller_patch_model import SellerPatch
from app.models.enums import BrazilianState, AccountType, ProductCategory


class TestSellerPatchModelMissingCoverage:
    """Testes para cobrir branches não cobertas do seller_patch_model.py"""
    
    def test_trade_name_validation_none(self):
        """Test trade_name validation with None value"""
        patch = SellerPatch(trade_name=None)
        assert patch.trade_name is None
    
    def test_trade_name_validation_empty_string(self):
        """Test trade_name validation with empty string"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(trade_name="")
        
        assert "O nome_fantasia deve conter ao menos 3 caracteres" in str(exc_info.value)
    
    def test_trade_name_validation_whitespace_only(self):
        """Test trade_name validation with whitespace only"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(trade_name="   ")
        
        assert "O nome_fantasia deve conter ao menos 3 caracteres" in str(exc_info.value)
    
    def test_trade_name_validation_too_short(self):
        """Test trade_name validation with string too short"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(trade_name="ab")
        
        assert "O nome_fantasia deve conter ao menos 3 caracteres" in str(exc_info.value)
    
    def test_trade_name_validation_valid(self):
        """Test trade_name validation with valid string"""
        patch = SellerPatch(trade_name="Valid Company Name")
        assert patch.trade_name == "Valid Company Name"
    
    def test_cnpj_validation_none(self):
        """Test cnpj validation with None value"""
        patch = SellerPatch(cnpj=None)
        assert patch.cnpj is None
    
    def test_cnpj_validation_empty_string(self):
        """Test cnpj validation with empty string"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(cnpj="")
        
        assert "O CNPJ deve conter exatamente 14 dígitos numéricos" in str(exc_info.value)
    
    def test_cnpj_validation_wrong_length(self):
        """Test cnpj validation with wrong length"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(cnpj="123456789")
        
        assert "O CNPJ deve conter exatamente 14 dígitos numéricos" in str(exc_info.value)
    
    def test_cnpj_validation_non_numeric(self):
        """Test cnpj validation with non-numeric characters"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(cnpj="1234567800010a")
        
        assert "O CNPJ deve conter exatamente 14 dígitos numéricos" in str(exc_info.value)
    
    def test_cnpj_validation_valid(self):
        """Test cnpj validation with valid CNPJ"""
        patch = SellerPatch(cnpj="12345678000100")
        assert patch.cnpj == "12345678000100"
    
    def test_company_name_validation_none(self):
        """Test company_name validation with None value"""
        patch = SellerPatch(company_name=None)
        assert patch.company_name is None
    
    def test_company_name_validation_empty_string(self):
        """Test company_name validation with empty string"""
        # company_name is optional and doesn't have validation, so empty string should be accepted
        patch = SellerPatch(company_name="")
        assert patch.company_name == ""
    
    def test_company_name_validation_valid(self):
        """Test company_name validation with valid string"""
        patch = SellerPatch(company_name="Valid Company Ltd")
        assert patch.company_name == "Valid Company Ltd"
    
    def test_state_municipal_registration_validation_none(self):
        """Test state_municipal_registration validation with None value"""
        patch = SellerPatch(state_municipal_registration=None)
        assert patch.state_municipal_registration is None
    
    def test_state_municipal_registration_validation_empty_string(self):
        """Test state_municipal_registration validation with empty string"""
        # state_municipal_registration is optional and empty string should be accepted
        patch = SellerPatch(state_municipal_registration="")
        assert patch.state_municipal_registration == ""
    
    def test_state_municipal_registration_validation_valid(self):
        """Test state_municipal_registration validation with valid string"""
        patch = SellerPatch(state_municipal_registration="123456789")
        assert patch.state_municipal_registration == "123456789"
    
    def test_commercial_address_validation_none(self):
        """Test commercial_address validation with None value"""
        patch = SellerPatch(commercial_address=None)
        assert patch.commercial_address is None
    
    def test_commercial_address_validation_empty_string(self):
        """Test commercial_address validation with empty string"""
        # commercial_address is optional and empty string should be accepted
        patch = SellerPatch(commercial_address="")
        assert patch.commercial_address == ""
    
    def test_commercial_address_validation_valid(self):
        """Test commercial_address validation with valid string"""
        patch = SellerPatch(commercial_address="123 Main Street")
        assert patch.commercial_address == "123 Main Street"
    
    def test_contact_phone_validation_none(self):
        """Test contact_phone validation with None value"""
        patch = SellerPatch(contact_phone=None)
        assert patch.contact_phone is None
    
    def test_contact_phone_validation_empty_string(self):
        """Test contact_phone validation with empty string"""
        # contact_phone is optional and empty string should be accepted
        patch = SellerPatch(contact_phone="")
        assert patch.contact_phone == ""
    
    def test_contact_phone_validation_valid(self):
        """Test contact_phone validation with valid string"""
        patch = SellerPatch(contact_phone="11999999999")
        assert patch.contact_phone == "11999999999"
    
    def test_contact_email_validation_none(self):
        """Test contact_email validation with None value"""
        patch = SellerPatch(contact_email=None)
        assert patch.contact_email is None
    
    def test_contact_email_validation_empty_string(self):
        """Test contact_email validation with empty string"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(contact_email="")
        
        assert "An email address must have an @-sign" in str(exc_info.value)
    
    def test_contact_email_validation_valid(self):
        """Test contact_email validation with valid string"""
        patch = SellerPatch(contact_email="test@example.com")
        assert patch.contact_email == "test@example.com"
    
    def test_all_optional_fields_none(self):
        """Test that all fields can be None"""
        patch = SellerPatch()
        
        assert patch.trade_name is None
        assert patch.cnpj is None
        assert patch.company_name is None
        assert patch.state_municipal_registration is None
        assert patch.commercial_address is None
        assert patch.contact_phone is None
        assert patch.contact_email is None
        assert patch.legal_rep_full_name is None
        assert patch.legal_rep_cpf is None
        assert patch.legal_rep_rg_number is None
        assert patch.legal_rep_rg_state is None
        assert patch.legal_rep_birth_date is None
        assert patch.legal_rep_phone is None
        assert patch.legal_rep_email is None
        assert patch.bank_name is None
        assert patch.agency_account is None
        assert patch.account_type is None
        assert patch.account_holder_name is None
        assert patch.product_categories is None
        assert patch.business_description is None
    
    def test_all_fields_with_valid_values(self):
        """Test patch with all fields having valid values"""
        patch = SellerPatch(
            trade_name="Test Company",
            cnpj="12345678000100",
            company_name="Test Company Ltd",
            state_municipal_registration="123456789",
            commercial_address="123 Main Street",
            contact_phone="11999999999",
            contact_email="test@example.com",
            legal_rep_full_name="John Doe",
            legal_rep_cpf="12345678901",
            legal_rep_rg_number="123456789",
            legal_rep_rg_state=BrazilianState.SP,
            legal_rep_birth_date=date(1990, 1, 1),
            legal_rep_phone="11888888888",
            legal_rep_email="john@example.com",
            bank_name="Test Bank",
            agency_account="1234-5/67890-1",
            account_type=AccountType.CURRENT,
            account_holder_name="Test Company Ltd",
            product_categories=[ProductCategory.COMPUTING],
            business_description="Test business description"
        )
        
        assert patch.trade_name == "Test Company"
        assert patch.cnpj == "12345678000100"
        assert patch.company_name == "Test Company Ltd"
