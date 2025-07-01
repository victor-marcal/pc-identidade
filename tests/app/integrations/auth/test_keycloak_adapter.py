"""
Testes para o KeycloakAdapter
"""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.integrations.auth.keycloak_adapter import (
    InvalidTokenException,
    KeycloakAdapter,
    OAuthException,
    TokenExpiredException,
)

# Dicionário com constantes para evitar duplicação
TEST_KEYCLOAK_DATA = {
    "well_known_url": "https://keycloak.example.com/.well-known/openid_connect",
    "jwks_uri": "https://keycloak.example.com/auth/realms/test/protocol/openid_connect/certs",
    "mock_key": "mock_key",
    "mock_token": "mock_token",
    "invalid_token": "invalid_token",
    "user_id": "user123",
    "username": "testuser",
    "sellers": "seller1,seller2",
    "exp_time": 1234567890,
    "algorithm": "RS256",
    "http_error": "HTTP Error",
    "jwt_error": "JWT decode error",
    "base_error": "Base error",
    "token_expired": "Token expired",
    "invalid_token_msg": "Invalid token",
    # Constantes para patches e módulos
    "httpx_client": "httpx.Client",
    "jwt_pyjwk_client": "jwt.PyJWKClient",
    "jwt_get_unverified_header": "jwt.get_unverified_header",
    "jwt_decode": "jwt.decode",
}


@pytest.mark.asyncio
async def test_keycloak_adapter_init_success():
    """Testa inicialização bem-sucedida do KeycloakAdapter"""
    mock_well_known_data = {"jwks_uri": TEST_KEYCLOAK_DATA["jwks_uri"]}

    with patch(TEST_KEYCLOAK_DATA["httpx_client"]) as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_well_known_data
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        with patch(TEST_KEYCLOAK_DATA["jwt_pyjwk_client"]) as mock_jwks_client:
            adapter = KeycloakAdapter(TEST_KEYCLOAK_DATA["well_known_url"])

            # Verifica que PyJWKClient foi inicializado com a URI correta
            mock_jwks_client.assert_called_once_with(mock_well_known_data["jwks_uri"])
            assert adapter.jwks_client is not None


@pytest.mark.asyncio
async def test_keycloak_adapter_init_http_error():
    """Testa erro HTTP durante inicialização"""
    with patch(TEST_KEYCLOAK_DATA["httpx_client"]) as mock_client:
        mock_client.return_value.__enter__.return_value.get.side_effect = httpx.HTTPStatusError(
            TEST_KEYCLOAK_DATA["http_error"], request=MagicMock(), response=MagicMock()
        )

        with pytest.raises(httpx.HTTPStatusError):
            KeycloakAdapter(TEST_KEYCLOAK_DATA["well_known_url"])


@pytest.mark.asyncio
async def test_validate_token_success():
    """Testa validação bem-sucedida de token"""
    mock_well_known_data = {"jwks_uri": TEST_KEYCLOAK_DATA["jwks_uri"]}

    mock_token_payload = {
        "sub": TEST_KEYCLOAK_DATA["user_id"],
        "preferred_username": TEST_KEYCLOAK_DATA["username"],
        "sellers": TEST_KEYCLOAK_DATA["sellers"],
        "exp": TEST_KEYCLOAK_DATA["exp_time"],
    }

    with patch(TEST_KEYCLOAK_DATA["httpx_client"]) as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_well_known_data
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        with patch(TEST_KEYCLOAK_DATA["jwt_pyjwk_client"]) as mock_jwks_client:
            mock_jwks_instance = MagicMock()
            mock_jwks_client.return_value = mock_jwks_instance
            mock_signing_key = MagicMock()
            mock_signing_key.key = TEST_KEYCLOAK_DATA["mock_key"]
            mock_jwks_instance.get_signing_key_from_jwt.return_value = mock_signing_key

            with patch(TEST_KEYCLOAK_DATA["jwt_get_unverified_header"]) as mock_get_header:
                mock_get_header.return_value = {"alg": TEST_KEYCLOAK_DATA["algorithm"]}

                with patch(TEST_KEYCLOAK_DATA["jwt_decode"]) as mock_jwt_decode:
                    mock_jwt_decode.return_value = mock_token_payload

                    adapter = KeycloakAdapter(TEST_KEYCLOAK_DATA["well_known_url"])
                    result = await adapter.validate_token(TEST_KEYCLOAK_DATA["mock_token"])

                    assert result == mock_token_payload
                    mock_jwt_decode.assert_called_once()


@pytest.mark.asyncio
async def test_validate_token_jwt_error():
    """Testa erro de JWT durante validação"""
    mock_well_known_data = {"jwks_uri": TEST_KEYCLOAK_DATA["jwks_uri"]}

    with patch(TEST_KEYCLOAK_DATA["httpx_client"]) as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_well_known_data
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        with patch(TEST_KEYCLOAK_DATA["jwt_pyjwk_client"]) as mock_jwks_client:
            mock_jwks_instance = MagicMock()
            mock_jwks_client.return_value = mock_jwks_instance
            mock_signing_key = MagicMock()
            mock_signing_key.key = TEST_KEYCLOAK_DATA["mock_key"]
            mock_jwks_instance.get_signing_key_from_jwt.return_value = mock_signing_key

            with patch(TEST_KEYCLOAK_DATA["jwt_decode"]) as mock_jwt_decode:
                mock_jwt_decode.side_effect = Exception(TEST_KEYCLOAK_DATA["jwt_error"])

                adapter = KeycloakAdapter(TEST_KEYCLOAK_DATA["well_known_url"])

                with pytest.raises(InvalidTokenException):
                    await adapter.validate_token(TEST_KEYCLOAK_DATA["invalid_token"])


def test_oauth_exceptions():
    """Testa as exceções personalizadas"""
    # Testa OAuthException base
    base_exc = OAuthException(TEST_KEYCLOAK_DATA["base_error"])
    assert str(base_exc) == TEST_KEYCLOAK_DATA["base_error"]

    # Testa TokenExpiredException
    expired_exc = TokenExpiredException(TEST_KEYCLOAK_DATA["token_expired"])
    assert str(expired_exc) == TEST_KEYCLOAK_DATA["token_expired"]
    assert isinstance(expired_exc, OAuthException)

    # Testa InvalidTokenException
    invalid_exc = InvalidTokenException(TEST_KEYCLOAK_DATA["invalid_token_msg"])
    assert str(invalid_exc) == TEST_KEYCLOAK_DATA["invalid_token_msg"]
    assert isinstance(invalid_exc, OAuthException)
