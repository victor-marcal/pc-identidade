"""
Testes para melhorar cobertura do keycloak_admin_client.py
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException

from app.clients.keycloak_admin_client import KeycloakAdminClient
from app.common.exceptions.bad_request_exception import BadRequestException

# Dicionário com constantes para evitar duplicação
TEST_ADMIN_CLIENT_DATA = {
    "httpx_async_client": "httpx.AsyncClient",
    "test_email": "test@example.com",
    "test_token": "test_token",
    "admin_token": "admin_token",
    "test_user": "test_user",
    "existing_user": "existing_user",
    "password": "password123",
    "seller_id": "seller_1",
    "bad_request_error": "Bad request error",
    "token_acquisition_failed": "Token acquisition failed",
    "user_exists_message": "já existe no Keycloak",
    "error_creating_user": "Erro ao criar usuário no Keycloak",
    "token_error": "Token error",
}


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
    mock_response.json.return_value = {"access_token": TEST_ADMIN_CLIENT_DATA["test_token"]}
    mock_response.raise_for_status.return_value = None

    with patch(TEST_ADMIN_CLIENT_DATA["httpx_async_client"]) as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

        token = await keycloak_client._get_admin_token()

        assert token == TEST_ADMIN_CLIENT_DATA["test_token"]
        mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_admin_token_http_error(keycloak_client):
    """Test _get_admin_token handles HTTP errors"""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Error", request=MagicMock(), response=MagicMock()
    )

    with patch(TEST_ADMIN_CLIENT_DATA["httpx_async_client"]) as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await keycloak_client._get_admin_token()


@pytest.mark.asyncio
async def test_create_user_success(keycloak_client):
    """Test create_user creates user successfully"""
    # Mock the admin token call
    with patch.object(keycloak_client, '_get_admin_token') as mock_get_token:
        mock_get_token.return_value = TEST_ADMIN_CLIENT_DATA["admin_token"]

        # Mock the user creation call
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.raise_for_status.return_value = None

        with patch(TEST_ADMIN_CLIENT_DATA["httpx_async_client"]) as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            # Should not raise any exception
            await keycloak_client.create_user(
                username=TEST_ADMIN_CLIENT_DATA["test_user"],
                email=TEST_ADMIN_CLIENT_DATA["test_email"],
                password=TEST_ADMIN_CLIENT_DATA["password"],
                seller_id=TEST_ADMIN_CLIENT_DATA["seller_id"],
            )

            mock_get_token.assert_called_once()
            mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_conflict_409(keycloak_client):
    """Test create_user handles 409 conflict (user already exists)"""
    # Mock the admin token call
    with patch.object(keycloak_client, '_get_admin_token') as mock_get_token:
        mock_get_token.return_value = TEST_ADMIN_CLIENT_DATA["admin_token"]

        # Mock the user creation call with 409 status
        mock_response = MagicMock()
        mock_response.status_code = 409

        with patch(TEST_ADMIN_CLIENT_DATA["httpx_async_client"]) as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

            with pytest.raises(BadRequestException) as exc_info:
                await keycloak_client.create_user(
                    username=TEST_ADMIN_CLIENT_DATA["existing_user"],
                    email=TEST_ADMIN_CLIENT_DATA["test_email"],
                    password=TEST_ADMIN_CLIENT_DATA["password"],
                    seller_id=TEST_ADMIN_CLIENT_DATA["seller_id"],
                )

            assert TEST_ADMIN_CLIENT_DATA["user_exists_message"] in str(exc_info.value.message)


@pytest.mark.asyncio
async def test_create_user_http_status_error(keycloak_client):
    """Test create_user handles HTTPStatusError"""
    # Mock the admin token call
    with patch.object(keycloak_client, '_get_admin_token') as mock_get_token:
        mock_get_token.return_value = TEST_ADMIN_CLIENT_DATA["admin_token"]

        # Mock the user creation call that raises HTTPStatusError
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = TEST_ADMIN_CLIENT_DATA["bad_request_error"]

        http_error = httpx.HTTPStatusError("HTTP Error", request=MagicMock(), response=mock_response)

        with patch(TEST_ADMIN_CLIENT_DATA["httpx_async_client"]) as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            mock_response.raise_for_status.side_effect = http_error

            with pytest.raises(HTTPException) as exc_info:
                await keycloak_client.create_user(
                    username=TEST_ADMIN_CLIENT_DATA["test_user"],
                    email=TEST_ADMIN_CLIENT_DATA["test_email"],
                    password=TEST_ADMIN_CLIENT_DATA["password"],
                    seller_id=TEST_ADMIN_CLIENT_DATA["seller_id"],
                )

            assert exc_info.value.status_code == 500
            assert TEST_ADMIN_CLIENT_DATA["error_creating_user"] in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_user_admin_token_error(keycloak_client):
    """Test create_user handles error when getting admin token"""
    # Mock the admin token call to raise an exception
    with patch.object(keycloak_client, '_get_admin_token') as mock_get_token:
        mock_response = MagicMock()
        mock_response.text = TEST_ADMIN_CLIENT_DATA["token_acquisition_failed"]
        mock_get_token.side_effect = httpx.HTTPStatusError(
            TEST_ADMIN_CLIENT_DATA["token_error"], request=MagicMock(), response=mock_response
        )

        with pytest.raises(HTTPException) as exc_info:
            await keycloak_client.create_user(
                username=TEST_ADMIN_CLIENT_DATA["test_user"],
                email=TEST_ADMIN_CLIENT_DATA["test_email"],
                password=TEST_ADMIN_CLIENT_DATA["password"],
                seller_id=TEST_ADMIN_CLIENT_DATA["seller_id"],
            )

        assert exc_info.value.status_code == 500
        assert TEST_ADMIN_CLIENT_DATA["error_creating_user"] in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_user_payload_structure(keycloak_client):
    """Test create_user sends correct payload structure"""
    # Mock the admin token call
    with patch.object(keycloak_client, '_get_admin_token') as mock_get_token:
        mock_get_token.return_value = TEST_ADMIN_CLIENT_DATA["admin_token"]

        # Mock the user creation call
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.raise_for_status.return_value = None

        with patch(TEST_ADMIN_CLIENT_DATA["httpx_async_client"]) as mock_client:
            mock_post = mock_client.return_value.__aenter__.return_value.post
            mock_post.return_value = mock_response

            await keycloak_client.create_user(
                username=TEST_ADMIN_CLIENT_DATA["test_user"],
                email=TEST_ADMIN_CLIENT_DATA["test_email"],
                password=TEST_ADMIN_CLIENT_DATA["password"],
                seller_id=TEST_ADMIN_CLIENT_DATA["seller_id"],
            )

            # Verify the call was made with correct structure
            call_args = mock_post.call_args
            assert call_args[1]['json']['username'] == TEST_ADMIN_CLIENT_DATA["test_user"]
            assert call_args[1]['json']['email'] == TEST_ADMIN_CLIENT_DATA["test_email"]
            assert call_args[1]['json']['enabled'] is True
            assert call_args[1]['json']['emailVerified'] is True
            assert call_args[1]['json']['credentials'][0]['value'] == TEST_ADMIN_CLIENT_DATA["password"]
            assert call_args[1]['json']['attributes']['sellers'] == [TEST_ADMIN_CLIENT_DATA["seller_id"]]
            assert call_args[1]['json']['requiredActions'] == []
