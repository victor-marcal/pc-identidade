"""
Testes para o cliente de administração do Keycloak: keycloak_admin_client.py
"""
from unittest.mock import MagicMock, patch

import secrets
import string
import httpx
import pytest
from fastapi import HTTPException

from app.clients.keycloak_admin_client import KeycloakAdminClient
from app.common.exceptions.bad_request_exception import BadRequestException

# --- Dicionário de constantes para os testes ---
TEST_DATA = {
    "httpx_async_client": "httpx.AsyncClient",
    "admin_token": "mock_admin_token",
    "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "test_user": "test_user",
    "test_email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User",
    "sellers": ["seller_a", "seller_b"],
    "bad_request_error": "Bad request error",
    "conflict_error": '{"errorMessage": "User with username test_user already exists."}',
}


def generate_test_password(length: int = 12) -> str:
    """Gera uma senha segura para testes"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))


@pytest.fixture
def keycloak_client():
    """Fixture para uma instância de KeycloakAdminClient."""
    return KeycloakAdminClient()

# --- Testes para _get_admin_token ---

@pytest.mark.asyncio
async def test_get_admin_token_success(keycloak_client):
    """Testa se _get_admin_token retorna o token com sucesso."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": TEST_DATA["admin_token"]}
    mock_response.raise_for_status.return_value = None

    with patch(TEST_DATA["httpx_async_client"]) as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        token = await keycloak_client._get_admin_token()
        assert token == TEST_DATA["admin_token"]

@pytest.mark.asyncio
async def test_get_admin_token_http_error_raises_http_exception(keycloak_client):
    """Testa se _get_admin_token lança HTTPException em caso de erro HTTP."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Error", request=MagicMock(), response=MagicMock(text="Auth failed")
    )

    with patch(TEST_DATA["httpx_async_client"]) as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        with pytest.raises(HTTPException) as exc_info:
            await keycloak_client._get_admin_token()
        assert exc_info.value.status_code == 500
        assert "Falha ao autenticar com o Keycloak" in exc_info.value.detail

# --- Testes para create_user ---

@pytest.mark.asyncio
async def test_create_user_success(keycloak_client):
    """Testa a criação de usuário bem-sucedida."""
    with patch.object(keycloak_client, '_get_admin_token', return_value=TEST_DATA["admin_token"]):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.headers = {"Location": f"users/{TEST_DATA['user_id']}"}

        with patch(TEST_DATA["httpx_async_client"]) as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            user_id = await keycloak_client.create_user(
                username=TEST_DATA["test_user"],
                email=TEST_DATA["test_email"],
                password=TEST_DATA["password"],
                first_name=TEST_DATA["first_name"],
                last_name=TEST_DATA["last_name"],
                sellers=TEST_DATA["sellers"]
            )
            assert user_id == TEST_DATA["user_id"]

@pytest.mark.asyncio
async def test_create_user_conflict_409_raises_bad_request(keycloak_client):
    """Testa se um conflito 409 lança BadRequestException."""
    with patch.object(keycloak_client, '_get_admin_token', return_value=TEST_DATA["admin_token"]):
        mock_response = MagicMock(status_code=409)

        with patch(TEST_DATA["httpx_async_client"]) as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            with pytest.raises(BadRequestException):
                await keycloak_client.create_user(
                    username="existing_user", email="e@e.com", password=generate_test_password(), first_name="f", last_name="l", sellers=[]
                )

# --- Novos Testes para Cobertura ---

@pytest.mark.asyncio
async def test_get_user_success(keycloak_client):
    """Testa a busca de usuário bem-sucedida."""
    with patch.object(keycloak_client, '_get_admin_token', return_value=TEST_DATA["admin_token"]):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": TEST_DATA["user_id"], "username": TEST_DATA["test_user"]}

        with patch(TEST_DATA["httpx_async_client"]) as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            user = await keycloak_client.get_user(TEST_DATA["user_id"])
            assert user["id"] == TEST_DATA["user_id"]

@pytest.mark.asyncio
async def test_get_user_not_found(keycloak_client):
    """Testa a busca de usuário que não existe (404)."""
    with patch.object(keycloak_client, '_get_admin_token', return_value=TEST_DATA["admin_token"]):
        mock_response = MagicMock(status_code=404)

        with patch(TEST_DATA["httpx_async_client"]) as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            user = await keycloak_client.get_user("non_existent_id")
            assert user is None

@pytest.mark.asyncio
async def test_get_users_success(keycloak_client):
    """Testa a listagem de todos os usuários."""
    with patch.object(keycloak_client, '_get_admin_token', return_value=TEST_DATA["admin_token"]):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": "1"}, {"id": "2"}]

        with patch(TEST_DATA["httpx_async_client"]) as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            users = await keycloak_client.get_users()
            assert len(users) == 2
            assert users[0]["id"] == "1"

@pytest.mark.asyncio
async def test_delete_user_success(keycloak_client):
    """Testa a exclusão de usuário bem-sucedida."""
    with patch.object(keycloak_client, '_get_admin_token', return_value=TEST_DATA["admin_token"]):
        mock_response = MagicMock(status_code=204)

        with patch(TEST_DATA["httpx_async_client"]) as mock_client:
            mock_client.return_value.__aenter__.return_value.delete.return_value = mock_response
            result = await keycloak_client.delete_user(TEST_DATA["user_id"])
            assert result is True

@pytest.mark.asyncio
async def test_delete_user_not_found(keycloak_client):
    """Testa a exclusão de um usuário que não existe (404)."""
    with patch.object(keycloak_client, '_get_admin_token', return_value=TEST_DATA["admin_token"]):
        mock_response = MagicMock(status_code=404)

        with patch(TEST_DATA["httpx_async_client"]) as mock_client:
            mock_client.return_value.__aenter__.return_value.delete.return_value = mock_response
            result = await keycloak_client.delete_user("non_existent_id")
            assert result is False

@pytest.mark.asyncio
async def test_update_user_success(keycloak_client):
    """Testa a atualização de dados de um usuário."""
    with patch.object(keycloak_client, '_get_admin_token', return_value=TEST_DATA["admin_token"]):
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = {"id": TEST_DATA["user_id"], "firstName": "Old"}

        mock_put_response = MagicMock(status_code=204)

        with patch(TEST_DATA["httpx_async_client"]) as mock_client:
            mock_aio_client = mock_client.return_value.__aenter__.return_value
            mock_aio_client.get.return_value = mock_get_response
            mock_aio_client.put.return_value = mock_put_response

            await keycloak_client.update_user(TEST_DATA["user_id"], {"first_name": "New"})

            # Verifica se o PUT foi chamado com os dados corretos
            call_args = mock_aio_client.put.call_args
            assert call_args[1]['json']['firstName'] == "New"

@pytest.mark.asyncio
async def test_update_user_conflict_raises_bad_request(keycloak_client):
    """Testa se um erro 400/409 na atualização lança BadRequestException."""
    with patch.object(keycloak_client, '_get_admin_token', return_value=TEST_DATA["admin_token"]):
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = {} # Mock da busca inicial

        mock_put_response = MagicMock(status_code=409)
        mock_put_response.json.return_value = {"errorMessage": "Conflict"}

        http_error = httpx.HTTPStatusError("Conflict", request=MagicMock(), response=mock_put_response)
        mock_put_response.raise_for_status.side_effect = http_error

        with patch(TEST_DATA["httpx_async_client"]) as mock_client:
            mock_aio_client = mock_client.return_value.__aenter__.return_value
            mock_aio_client.get.return_value = mock_get_response
            mock_aio_client.put.return_value = mock_put_response

            with pytest.raises(BadRequestException) as exc_info:
                await keycloak_client.update_user(TEST_DATA["user_id"], {"email": "conflict@email.com"})

            assert "Conflict" in str(exc_info.value)

@pytest.mark.asyncio
async def test_reset_user_password_success(keycloak_client):
    """Testa a redefinição de senha bem-sucedida."""
    with patch.object(keycloak_client, '_get_admin_token', return_value=TEST_DATA["admin_token"]):
        mock_response = MagicMock(status_code=204)

        with patch(TEST_DATA["httpx_async_client"]) as mock_client:
            mock_client.return_value.__aenter__.return_value.put.return_value = mock_response

            await keycloak_client.reset_user_password(TEST_DATA["user_id"], "new_secure_password")

            mock_client.return_value.__aenter__.return_value.put.assert_called_once()
