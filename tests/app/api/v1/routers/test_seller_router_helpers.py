"""
Testes focados para aumentar a cobertura do seller_router.py
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.api.v1.routers.seller_router import (
    _find_seller_by_id_with_access_check,
    _find_seller_by_cnpj_with_access_check,
    SELLER_NOT_FOUND_OR_ACCESS_DENIED
)
from app.api.common.auth_handler import UserAuthInfo
from app.models.base import UserModel


@pytest.fixture
def mock_user_auth_info():
    return UserAuthInfo(
        user=UserModel(name="test-user", server="test-server"),
        trace_id="test-trace",
        sellers=["seller1", "seller2"],
        info_token={"sub": "test-user"}
    )


@pytest.fixture
def mock_seller_service():
    return AsyncMock()


class TestSellerRouterHelpers:
    """Testes para as funções helper do seller router"""
    
    @pytest.mark.asyncio
    async def test_find_seller_by_id_with_access_check_success(self, mock_user_auth_info, mock_seller_service):
        """Testa busca de seller por ID com acesso permitido"""
        # Mock seller encontrado
        mock_seller = MagicMock()
        mock_seller.seller_id = "seller1"
        mock_seller_service.find_by_id.return_value = mock_seller
        
        result = await _find_seller_by_id_with_access_check(
            "seller1", mock_user_auth_info, mock_seller_service
        )
        
        assert result == mock_seller
        mock_seller_service.find_by_id.assert_called_once_with("seller1")
        
    @pytest.mark.asyncio
    async def test_find_seller_by_id_with_access_check_no_permission(self, mock_user_auth_info, mock_seller_service):
        """Testa busca de seller por ID sem permissão"""
        with pytest.raises(HTTPException) as exc_info:
            await _find_seller_by_id_with_access_check(
                "seller999", mock_user_auth_info, mock_seller_service
            )
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == SELLER_NOT_FOUND_OR_ACCESS_DENIED
        mock_seller_service.find_by_id.assert_not_called()
        
    @pytest.mark.asyncio
    async def test_find_seller_by_id_with_access_check_seller_not_found(self, mock_user_auth_info, mock_seller_service):
        """Testa busca de seller por ID quando seller não existe"""
        mock_seller_service.find_by_id.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await _find_seller_by_id_with_access_check(
                "seller1", mock_user_auth_info, mock_seller_service
            )
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Seller não encontrado"
        mock_seller_service.find_by_id.assert_called_once_with("seller1")
        
    @pytest.mark.asyncio
    async def test_find_seller_by_cnpj_with_access_check_success(self, mock_user_auth_info, mock_seller_service):
        """Testa busca de seller por CNPJ com acesso permitido"""
        # Mock seller encontrado
        mock_seller = MagicMock()
        mock_seller.seller_id = "seller1"
        mock_seller_service.find_by_cnpj.return_value = mock_seller
        
        result = await _find_seller_by_cnpj_with_access_check(
            "12345678901234", mock_user_auth_info, mock_seller_service
        )
        
        assert result == mock_seller
        mock_seller_service.find_by_cnpj.assert_called_once_with("12345678901234")
        
    @pytest.mark.asyncio
    async def test_find_seller_by_cnpj_with_access_check_seller_not_found(self, mock_user_auth_info, mock_seller_service):
        """Testa busca de seller por CNPJ quando seller não existe"""
        mock_seller_service.find_by_cnpj.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            await _find_seller_by_cnpj_with_access_check(
                "12345678901234", mock_user_auth_info, mock_seller_service
            )
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Seller não encontrado"
        mock_seller_service.find_by_cnpj.assert_called_once_with("12345678901234")
        
    @pytest.mark.asyncio
    async def test_find_seller_by_cnpj_with_access_check_no_permission(self, mock_user_auth_info, mock_seller_service):
        """Testa busca de seller por CNPJ sem permissão"""
        # Mock seller encontrado mas sem permissão
        mock_seller = MagicMock()
        mock_seller.seller_id = "seller999"  # Não está nas permissões do usuário
        mock_seller_service.find_by_cnpj.return_value = mock_seller
        
        with pytest.raises(HTTPException) as exc_info:
            await _find_seller_by_cnpj_with_access_check(
                "12345678901234", mock_user_auth_info, mock_seller_service
            )
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == SELLER_NOT_FOUND_OR_ACCESS_DENIED
        mock_seller_service.find_by_cnpj.assert_called_once_with("12345678901234")


class TestSellerRouterEndpoints:
    """Testes para os endpoints do seller router"""
    
    def test_seller_router_constant(self):
        """Testa a constante do router"""
        assert SELLER_NOT_FOUND_OR_ACCESS_DENIED == "Seller não encontrado ou acesso não permitido"
