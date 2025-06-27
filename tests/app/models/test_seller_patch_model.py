import pytest
from pydantic import ValidationError
from app.models.seller_patch_model import SellerPatch


class TestSellerPatchValidation:
    """Test SellerPatch validation following SOLID principles"""

    def test_valid_seller_patch(self):
        """Test valid SellerPatch creation"""
        patch_data = SellerPatch(
            nome_fantasia="Loja Teste",
            cnpj="12345678000100"
        )
        
        assert patch_data.nome_fantasia == "Loja Teste"
        assert patch_data.cnpj == "12345678000100"

    def test_nome_fantasia_too_short(self):
        """Test nome_fantasia validation with short name"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(nome_fantasia="ab")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "nome_fantasia deve conter ao menos 3 caracteres" in str(errors[0]["ctx"]["error"])

    def test_nome_fantasia_whitespace_only(self):
        """Test nome_fantasia validation with whitespace only"""
        with pytest.raises(ValidationError) as exc_info:
            SellerPatch(nome_fantasia="  ")
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "nome_fantasia deve conter ao menos 3 caracteres" in str(errors[0]["ctx"]["error"])

    def test_nome_fantasia_none_valid(self):
        """Test nome_fantasia validation with None value"""
        patch_data = SellerPatch(nome_fantasia=None)
        
        assert patch_data.nome_fantasia is None

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
            SellerPatch(cnpj="1234567890123a")  # Contains letter
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "CNPJ deve conter exatamente 14 dígitos numéricos" in str(errors[0]["ctx"]["error"])

    def test_cnpj_none_valid(self):
        """Test CNPJ validation with None value"""
        patch_data = SellerPatch(cnpj=None)
        
        assert patch_data.cnpj is None

    def test_valid_cnpj_format(self):
        """Test CNPJ validation with valid format"""
        patch_data = SellerPatch(cnpj="12345678000100")
        
        assert patch_data.cnpj == "12345678000100"

    def test_empty_patch_valid(self):
        """Test empty SellerPatch is valid"""
        patch_data = SellerPatch()
        
        assert patch_data.nome_fantasia is None
        assert patch_data.cnpj is None
