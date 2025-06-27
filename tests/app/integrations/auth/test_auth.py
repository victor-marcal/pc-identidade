"""
Testes para melhorar cobertura do auth.py
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from fastapi import HTTPException
from jose import jwt
from jose.exceptions import JWTError

from app.integrations.auth.auth import (
    get_jwks, 
    get_current_user, 
    check_seller_permission,
    TokenData,
    _jwks_cache
)


@pytest.fixture(autouse=True)
def clear_jwks_cache():
    """Clear JWKS cache before each test"""
    import app.integrations.auth.auth
    app.integrations.auth.auth._jwks_cache = None
    yield
    app.integrations.auth.auth._jwks_cache = None


@pytest.mark.asyncio
async def test_get_jwks_success():
    """Test get_jwks returns JWKS successfully"""
    mock_jwks = {"keys": [{"kid": "test_kid", "kty": "RSA"}]}
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_jwks
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        result = await get_jwks()
        
        assert result == mock_jwks
        mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_jwks_cached():
    """Test get_jwks returns cached value on second call"""
    import app.integrations.auth.auth
    
    # Set cache manually
    cached_jwks = {"keys": [{"kid": "cached_kid"}]}
    app.integrations.auth.auth._jwks_cache = cached_jwks
    
    # Should return cached value without making HTTP request
    result = await get_jwks()
    
    assert result == cached_jwks


@pytest.mark.asyncio
async def test_get_jwks_request_error():
    """Test get_jwks handles httpx.RequestError"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.RequestError("Connection error")
        
        with pytest.raises(HTTPException) as exc_info:
            await get_jwks()
        
        assert exc_info.value.status_code == 503
        assert "Não foi possível conectar ao serviço de autenticação" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_jwks_http_status_error():
    """Test get_jwks handles HTTP status errors"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "HTTP Error", request=MagicMock(), response=MagicMock()
        )
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        with pytest.raises(httpx.HTTPStatusError):
            await get_jwks()


@pytest.mark.asyncio
async def test_get_current_user_success():
    """Test get_current_user validates token successfully"""
    mock_jwks = {
        "keys": [{
            "kid": "test_kid",
            "kty": "RSA", 
            "use": "sig",
            "n": "test_n",
            "e": "test_e"
        }]
    }
    
    mock_payload = {
        "preferred_username": "test_user",
        "sellers": "seller1,seller2",
        "sub": "user_id_123",
        "exp": 1234567890
    }
    
    with patch('app.integrations.auth.auth.get_jwks') as mock_get_jwks:
        mock_get_jwks.return_value = mock_jwks
        
        with patch('jose.jwt.get_unverified_header') as mock_get_header:
            mock_get_header.return_value = {"kid": "test_kid"}
            
            with patch('jose.jwt.decode') as mock_decode:
                mock_decode.return_value = mock_payload
                
                result = await get_current_user("test_token")
                
                assert result.preferred_username == "test_user"
                assert result.sellers == ["seller1", "seller2"]
                assert result.sub == "user_id_123"
                assert result.exp == 1234567890


@pytest.mark.asyncio
async def test_get_current_user_sellers_as_list():
    """Test get_current_user handles sellers as list"""
    mock_jwks = {
        "keys": [{
            "kid": "test_kid",
            "kty": "RSA",
            "use": "sig", 
            "n": "test_n",
            "e": "test_e"
        }]
    }
    
    mock_payload = {
        "preferred_username": "test_user",
        "sellers": ["seller1", "seller2"],  # Already a list
        "sub": "user_id_123",
        "exp": 1234567890
    }
    
    with patch('app.integrations.auth.auth.get_jwks') as mock_get_jwks:
        mock_get_jwks.return_value = mock_jwks
        
        with patch('jose.jwt.get_unverified_header') as mock_get_header:
            mock_get_header.return_value = {"kid": "test_kid"}
            
            with patch('jose.jwt.decode') as mock_decode:
                mock_decode.return_value = mock_payload
                
                result = await get_current_user("test_token")
                
                assert result.sellers == ["seller1", "seller2"]


@pytest.mark.asyncio
async def test_get_current_user_empty_sellers():
    """Test get_current_user handles empty sellers"""
    mock_jwks = {
        "keys": [{
            "kid": "test_kid",
            "kty": "RSA",
            "use": "sig",
            "n": "test_n", 
            "e": "test_e"
        }]
    }
    
    mock_payload = {
        "preferred_username": "test_user",
        "sellers": "",  # Empty string
        "sub": "user_id_123",
        "exp": 1234567890
    }
    
    with patch('app.integrations.auth.auth.get_jwks') as mock_get_jwks:
        mock_get_jwks.return_value = mock_jwks
        
        with patch('jose.jwt.get_unverified_header') as mock_get_header:
            mock_get_header.return_value = {"kid": "test_kid"}
            
            with patch('jose.jwt.decode') as mock_decode:
                mock_decode.return_value = mock_payload
                
                result = await get_current_user("test_token")
                
                assert result.sellers == []


@pytest.mark.asyncio
async def test_get_current_user_missing_kid():
    """Test get_current_user handles missing kid in JWKS"""
    mock_jwks = {
        "keys": [{
            "kid": "different_kid",
            "kty": "RSA"
        }]
    }
    
    with patch('app.integrations.auth.auth.get_jwks') as mock_get_jwks:
        mock_get_jwks.return_value = mock_jwks
        
        with patch('jose.jwt.get_unverified_header') as mock_get_header:
            mock_get_header.return_value = {"kid": "test_kid"}
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("test_token")
            
            assert exc_info.value.status_code == 401
            assert "Não foi possível validar as credenciais" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_jwt_error():
    """Test get_current_user handles JWT decode errors"""
    mock_jwks = {
        "keys": [{
            "kid": "test_kid",
            "kty": "RSA",
            "use": "sig",
            "n": "test_n",
            "e": "test_e"
        }]
    }
    
    with patch('app.integrations.auth.auth.get_jwks') as mock_get_jwks:
        mock_get_jwks.return_value = mock_jwks
        
        with patch('jose.jwt.get_unverified_header') as mock_get_header:
            mock_get_header.return_value = {"kid": "test_kid"}
            
            with patch('jose.jwt.decode') as mock_decode:
                mock_decode.side_effect = JWTError("Invalid token")
                
                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user("test_token")
                
                assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_check_seller_permission_allowed():
    """Test check_seller_permission allows access for authorized seller"""
    current_user = TokenData(
        preferred_username="test_user",
        sellers=["seller1", "seller2"],
        sub="user_id",
        exp=1234567890
    )
    
    # Should not raise exception
    await check_seller_permission("seller1", current_user)


@pytest.mark.asyncio
async def test_check_seller_permission_forbidden():
    """Test check_seller_permission denies access for unauthorized seller"""
    current_user = TokenData(
        preferred_username="test_user",
        sellers=["seller1", "seller2"],
        sub="user_id",
        exp=1234567890
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await check_seller_permission("seller3", current_user)
    
    assert exc_info.value.status_code == 403
    assert "Você não tem permissão para acessar o seller 'seller3'" in exc_info.value.detail


def test_token_data_model():
    """Test TokenData model creation and validation"""
    token_data = TokenData(
        preferred_username="test_user",
        sellers=["seller1"],
        sub="user_id",
        exp=1234567890
    )
    
    assert token_data.preferred_username == "test_user"
    assert token_data.sellers == ["seller1"]
    assert token_data.sub == "user_id"
    assert token_data.exp == 1234567890


def test_token_data_model_with_alias():
    """Test TokenData model with field alias"""
    data = {
        "preferred_username": "test_user",
        "sellers": ["seller1"],
        "sub": "user_id", 
        "exp": 1234567890
    }
    
    token_data = TokenData(**data)
    
    assert token_data.preferred_username == "test_user"
