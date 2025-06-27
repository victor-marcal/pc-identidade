"""
Testes para melhorar cobertura do keycloak_admin_client.py
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from fastapi import HTTPException

from app.clients.keycloak_admin_client import KeycloakAdminClient
from app.common.exceptions.bad_request_exception import BadRequestException


@pytest.fixture
def keycloak_client():
    """Fixture para KeycloakAdminClient"""
    return KeycloakAdminClient()


@pytest.mark.asyncio
async def test_init_sets_urls(keycloak_client):
    """Test KeycloakAdminClient initialization sets correct URLs"""
    assert keycloak_client.settings is not None
    assert "admin/realms" in keycloak_client.base_url
    assert "protocol/openid-connect/token" in keycloak_client.token_url


@pytest.mark.asyncio
async def test_get_admin_token_success(keycloak_client):
    """Test _get_admin_token returns token successfully"""
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "test_token"}
    mock_response.raise_for_status.return_value = None
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        token = await keycloak_client._get_admin_token()
        
        assert token == "test_token"
        mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_admin_token_http_error(keycloak_client):
    """Test _get_admin_token handles HTTP errors"""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Error", request=MagicMock(), response=MagicMock()
    )
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        with pytest.raises(httpx.HTTPStatusError):
            await keycloak_client._get_admin_token()


@pytest.mark.asyncio
async def test_create_user_success(keycloak_client):
    """Test create_user creates user successfully"""
    # Mock the admin token call
    with patch.object(keycloak_client, '_get_admin_token') as mock_get_token:
        mock_get_token.return_value = "admin_token"
        
        # Mock the user creation call
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.raise_for_status.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Should not raise any exception
            await keycloak_client.create_user(
                username="test_user",
                email="test@example.com", 
                password="password123",
                seller_id="seller_1"
            )
            
            mock_get_token.assert_called_once()
            mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_conflict_409(keycloak_client):
    """Test create_user handles 409 conflict (user already exists)"""
    # Mock the admin token call
    with patch.object(keycloak_client, '_get_admin_token') as mock_get_token:
        mock_get_token.return_value = "admin_token"
        
        # Mock the user creation call with 409 status
        mock_response = MagicMock()
        mock_response.status_code = 409
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            with pytest.raises(BadRequestException) as exc_info:
                await keycloak_client.create_user(
                    username="existing_user",
                    email="test@example.com",
                    password="password123", 
                    seller_id="seller_1"
                )
            
            assert "já existe no Keycloak" in str(exc_info.value.message)


@pytest.mark.asyncio
async def test_create_user_http_status_error(keycloak_client):
    """Test create_user handles HTTPStatusError"""
    # Mock the admin token call
    with patch.object(keycloak_client, '_get_admin_token') as mock_get_token:
        mock_get_token.return_value = "admin_token"
        
        # Mock the user creation call that raises HTTPStatusError
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request error"
        
        http_error = httpx.HTTPStatusError(
            "HTTP Error",
            request=MagicMock(),
            response=mock_response
        )
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            mock_response.raise_for_status.side_effect = http_error
            
            with pytest.raises(HTTPException) as exc_info:
                await keycloak_client.create_user(
                    username="test_user",
                    email="test@example.com",
                    password="password123",
                    seller_id="seller_1"
                )
            
            assert exc_info.value.status_code == 500
            assert "Erro ao criar usuário no Keycloak" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_user_admin_token_error(keycloak_client):
    """Test create_user handles error when getting admin token"""
    # Mock the admin token call to raise an exception
    with patch.object(keycloak_client, '_get_admin_token') as mock_get_token:
        mock_response = MagicMock()
        mock_response.text = "Token acquisition failed"
        mock_get_token.side_effect = httpx.HTTPStatusError(
            "Token error",
            request=MagicMock(),
            response=mock_response
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await keycloak_client.create_user(
                username="test_user",
                email="test@example.com",
                password="password123",
                seller_id="seller_1"
            )
        
        assert exc_info.value.status_code == 500
        assert "Erro ao criar usuário no Keycloak" in exc_info.value.detail


@pytest.mark.asyncio 
async def test_create_user_payload_structure(keycloak_client):
    """Test create_user sends correct payload structure"""
    # Mock the admin token call
    with patch.object(keycloak_client, '_get_admin_token') as mock_get_token:
        mock_get_token.return_value = "admin_token"
        
        # Mock the user creation call
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.raise_for_status.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_post = mock_client.return_value.__aenter__.return_value.post
            mock_post.return_value = mock_response
            
            await keycloak_client.create_user(
                username="test_user",
                email="test@example.com",
                password="password123",
                seller_id="seller_1"
            )
            
            # Verify the call was made with correct structure
            call_args = mock_post.call_args
            assert call_args[1]['json']['username'] == "test_user"
            assert call_args[1]['json']['email'] == "test@example.com"
            assert call_args[1]['json']['enabled'] is True
            assert call_args[1]['json']['emailVerified'] is True
            assert call_args[1]['json']['credentials'][0]['value'] == "password123"
            assert call_args[1]['json']['attributes']['sellers'] == ["seller_1"]
            assert call_args[1]['json']['requiredActions'] == []
