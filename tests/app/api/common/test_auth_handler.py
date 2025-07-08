"""
Testes focados em aumentar cobertura dos módulos com menor coverage
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request, HTTPException
from app.api.common.auth_handler import UserAuthInfo, do_auth, get_current_user, get_current_user_info, require_seller_permission
from app.models.base import UserModel
from app.common.exceptions import UnauthorizedException, ForbiddenException
from app.integrations.auth.keycloak_adapter import TokenExpiredException, InvalidTokenException, OAuthException


class TestAuthHandler:
    """Testes para auth_handler.py para aumentar cobertura"""
    
    @pytest.mark.asyncio
    async def test_do_auth_token_expired(self):
        """Test do_auth with expired token"""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        
        mock_adapter = AsyncMock()
        mock_adapter.validate_token.side_effect = TokenExpiredException("Token expired")
        
        with pytest.raises(UnauthorizedException, match="Seu token de acesso expirou."):
            await do_auth(request, "expired_token", "seller123", mock_adapter)
    
    @pytest.mark.asyncio
    async def test_do_auth_invalid_token(self):
        """Test do_auth with invalid token"""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        
        mock_adapter = AsyncMock()
        mock_adapter.validate_token.side_effect = InvalidTokenException("Invalid token")
        
        with pytest.raises(UnauthorizedException, match="Seu token de acesso é inválido."):
            await do_auth(request, "invalid_token", "seller123", mock_adapter)
    
    @pytest.mark.asyncio  
    async def test_do_auth_oauth_exception(self):
        """Test do_auth with OAuth exception"""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        
        mock_adapter = AsyncMock()
        mock_adapter.validate_token.side_effect = OAuthException("OAuth error")
        
        with pytest.raises(UnauthorizedException, match="Falha na autenticação."):
            await do_auth(request, "oauth_error_token", "seller123", mock_adapter)
    
    @pytest.mark.asyncio
    async def test_do_auth_forbidden_seller(self):
        """Test do_auth with seller not in user's list"""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.trace_id = "trace123"
        
        mock_adapter = AsyncMock()
        mock_adapter.validate_token.return_value = {
            "sub": "user123",
            "iss": "http://keycloak/realm/test",
            "sellers": "seller1,seller2"
        }
        
        with pytest.raises(ForbiddenException, match="Você não tem permissão para acessar este seller."):
            await do_auth(request, "valid_token", "seller999", mock_adapter)
    
    @pytest.mark.asyncio
    async def test_do_auth_success(self):
        """Test successful do_auth"""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.trace_id = "trace123"
        
        mock_adapter = AsyncMock()
        mock_adapter.validate_token.return_value = {
            "sub": "user123", 
            "iss": "http://keycloak/realm/test",
            "sellers": "seller1,seller2"
        }
        
        await do_auth(request, "valid_token", "seller1", mock_adapter)
        
        # Verificar se user foi definido no state
        assert hasattr(request.state, 'user')
        user_info = request.state.user
        assert user_info.user.name == "user123"
        assert user_info.user.server == "http://keycloak/realm/test"
        assert "seller1" in user_info.sellers
        assert user_info.trace_id == "trace123"
    
    async def test_get_current_user(self):
        """Test get_current_user"""
        request = MagicMock(spec=Request)
        user_info = UserAuthInfo(
            user=UserModel(name="test", server="http://test"),
            trace_id="trace123",
            sellers=["seller1"],
            info_token={}
        )
        request.state.user = user_info
        
        result = await get_current_user(request)
        assert result == user_info
    
    @pytest.mark.asyncio
    async def test_get_current_user_info_with_auth(self):
        """Test get_current_user_info with authentication"""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.trace_id = "trace123"
        
        mock_adapter = AsyncMock()
        mock_adapter.validate_token.return_value = {
            "sub": "test",
            "iss": "http://test",
            "sellers": "seller1"
        }
        
        result = await get_current_user_info(request, "valid_token", mock_adapter)
        assert result.user.name == "test"
        assert result.user.server == "http://test"
        assert result.sellers == ["seller1"]
    
    def test_require_seller_permission_success(self):
        """Test require_seller_permission with valid permission"""
        user_info = UserAuthInfo(
            user=UserModel(name="test", server="http://test"),
            trace_id="trace123",
            sellers=["seller1", "seller2"],
            info_token={}
        )
        
        # Should not raise exception
        result = require_seller_permission("seller1", user_info)
        assert result == user_info
    
    @pytest.mark.asyncio
    async def test_require_seller_permission_forbidden(self):
        """Test require_seller_permission with invalid permission"""
        user_info = UserAuthInfo(
            user=UserModel(name="test", server="http://test"),
            trace_id="trace123",
            sellers=["seller1", "seller2"],
            info_token={}
        )
        
        with pytest.raises(ForbiddenException, match="Você não tem permissão para acessar este seller."):
            await require_seller_permission("seller999", user_info)
    
    def test_user_auth_info_to_sellers_string(self):
        """Test UserAuthInfo.to_sellers with string input"""
        result = UserAuthInfo.to_sellers("seller1,seller2,seller3")
        assert result == ["seller1", "seller2", "seller3"]
    
    def test_user_auth_info_to_sellers_list(self):
        """Test UserAuthInfo.to_sellers with list input"""
        result = UserAuthInfo.to_sellers(["seller1", "seller2"])
        assert result == ["seller1", "seller2"]
    
    def test_user_auth_info_to_sellers_none(self):
        """Test UserAuthInfo.to_sellers with None input"""
        result = UserAuthInfo.to_sellers(None)
        assert result == []
    
    def test_user_auth_info_to_sellers_empty(self):
        """Test UserAuthInfo.to_sellers with empty string"""
        result = UserAuthInfo.to_sellers("")
        assert result == []
