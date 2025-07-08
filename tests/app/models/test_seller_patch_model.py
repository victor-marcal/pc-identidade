import pytest
from pydantic import ValidationError
from app.models.seller_patch_model import SellerPatch


class TestSellerPatchValidation:
    """Test SellerPatch validation following SOLID principles"""
    
    def test_valid_seller_patch(self):
        """Test valid SellerPatch creation"""
        patch_data = SellerPatch(trade_name="Loja Teste", cnpj="12345678000100")
        assert patch_data.trade_name == "Loja Teste"
        assert patch_data.cnpj == "12345678000100"

    def test_nome_fantasia_too_short(self):
        """Test trade_name validation with short name"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(trade_name="ab")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "O nome_fantasia deve conter ao menos 3 caracteres" in str(errors[0]["ctx"]["error"])

    def test_nome_fantasia_whitespace_only(self):
        """Test trade_name validation with whitespace only"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(trade_name="  ")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "O nome_fantasia deve conter ao menos 3 caracteres" in str(errors[0]["ctx"]["error"])

    def test_nome_fantasia_none_valid(self):
        """Test trade_name validation with None value"""
        patch_data = SellerPatch(trade_name=None)
        assert patch_data.trade_name is None

    def test_cnpj_invalid_format(self):
        """Test CNPJ validation with invalid format"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(cnpj="12345678901")  # Only 11 digits

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "CNPJ deve conter exatamente 14 dígitos numéricos" in str(errors[0]["ctx"]["error"])

    def test_cnpj_non_numeric(self):
        """Test CNPJ validation with non-numeric characters"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(cnpj="12.345.678/0001-90")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "CNPJ deve conter exatamente 14 dígitos numéricos" in str(errors[0]["ctx"]["error"])

    def test_cnpj_none_valid(self):
        """Test CNPJ validation with None value"""
        patch_data = SellerPatch(cnpj=None)
        assert patch_data.cnpj is None

    def test_valid_cnpj_format(self):
        """Test valid CNPJ format"""
        patch_data = SellerPatch(cnpj="12345678000100")
        assert patch_data.cnpj == "12345678000100"

    def test_empty_patch_valid(self):
        """Test empty SellerPatch is valid"""
        patch_data = SellerPatch()
        assert patch_data.trade_name is None
        assert patch_data.cnpj is None

    def test_seller_patch_nome_fantasia_none_validation(self):
        """Test that trade_name can be None - covers None branch"""
        seller_patch = SellerPatch(trade_name=None, cnpj="12345678000100")
        assert seller_patch.trade_name is None
        assert seller_patch.cnpj == "12345678000100"

    def test_seller_patch_cnpj_none_validation(self):
        """Test that CNPJ can be None - covers None branch"""
        seller_patch = SellerPatch(trade_name="Loja Teste", cnpj=None)
        assert seller_patch.trade_name == "Loja Teste"
        assert seller_patch.cnpj is None

    def test_seller_patch_nome_fantasia_whitespace_only(self):
        """Test trade_name with only whitespace - covers strip() branch"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(trade_name="   ")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "O nome_fantasia deve conter ao menos 3 caracteres" in str(errors[0]["ctx"]["error"])

    def test_seller_patch_cnpj_non_digit_characters(self):
        """Test CNPJ with non-digit characters"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(cnpj="1234567800010a")

        errors = exc_info.value.errors()
        assert len(errors) == 1

    def test_seller_patch_cnpj_wrong_length(self):
        """Test CNPJ with wrong length"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(cnpj="1234567800")

        errors = exc_info.value.errors()
        assert len(errors) == 1
