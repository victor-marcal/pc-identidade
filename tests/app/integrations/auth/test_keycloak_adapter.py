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


@pytest.mark.asyncio
async def test_keycloak_adapter_init_success():
    """Testa inicialização bem-sucedida do KeycloakAdapter"""
    mock_well_known_data = {"jwks_uri": "https://keycloak.example.com/auth/realms/test/protocol/openid_connect/certs"}

    with patch('httpx.Client') as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_well_known_data
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        with patch('jwt.PyJWKClient') as mock_jwks_client:
            adapter = KeycloakAdapter("https://keycloak.example.com/.well-known/openid_connect")

            # Verifica que PyJWKClient foi inicializado com a URI correta
            mock_jwks_client.assert_called_once_with(mock_well_known_data["jwks_uri"])
            assert adapter.jwks_client is not None


@pytest.mark.asyncio
async def test_keycloak_adapter_init_http_error():
    """Testa erro HTTP durante inicialização"""
    with patch('httpx.Client') as mock_client:
        mock_client.return_value.__enter__.return_value.get.side_effect = httpx.HTTPStatusError(
            "HTTP Error", request=MagicMock(), response=MagicMock()
        )

        with pytest.raises(httpx.HTTPStatusError):
            KeycloakAdapter("https://keycloak.example.com/.well-known/openid_connect")


@pytest.mark.asyncio
async def test_validate_token_success():
    """Testa validação bem-sucedida de token"""
    mock_well_known_data = {"jwks_uri": "https://keycloak.example.com/auth/realms/test/protocol/openid_connect/certs"}

    mock_token_payload = {
        "sub": "user123",
        "preferred_username": "testuser",
        "sellers": "seller1,seller2",
        "exp": 1234567890,
    }

    with patch('httpx.Client') as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_well_known_data
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        with patch('jwt.PyJWKClient') as mock_jwks_client:
            mock_jwks_instance = MagicMock()
            mock_jwks_client.return_value = mock_jwks_instance
            mock_signing_key = MagicMock()
            mock_signing_key.key = "mock_key"
            mock_jwks_instance.get_signing_key_from_jwt.return_value = mock_signing_key

            with patch('jwt.get_unverified_header') as mock_get_header:
                mock_get_header.return_value = {"alg": "RS256"}

                with patch('jwt.decode') as mock_jwt_decode:
                    mock_jwt_decode.return_value = mock_token_payload

                    adapter = KeycloakAdapter("https://keycloak.example.com/.well-known/openid_connect")
                    result = await adapter.validate_token("mock_token")

                    assert result == mock_token_payload
                    mock_jwt_decode.assert_called_once()


@pytest.mark.asyncio
async def test_validate_token_jwt_error():
    """Testa erro de JWT durante validação"""
    mock_well_known_data = {"jwks_uri": "https://keycloak.example.com/auth/realms/test/protocol/openid_connect/certs"}

    with patch('httpx.Client') as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_well_known_data
        mock_response.raise_for_status.return_value = None
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        with patch('jwt.PyJWKClient') as mock_jwks_client:
            mock_jwks_instance = MagicMock()
            mock_jwks_client.return_value = mock_jwks_instance
            mock_signing_key = MagicMock()
            mock_signing_key.key = "mock_key"
            mock_jwks_instance.get_signing_key_from_jwt.return_value = mock_signing_key

            with patch('jwt.decode') as mock_jwt_decode:
                mock_jwt_decode.side_effect = Exception("JWT decode error")

                adapter = KeycloakAdapter("https://keycloak.example.com/.well-known/openid_connect")

                with pytest.raises(InvalidTokenException):
                    await adapter.validate_token("invalid_token")


def test_oauth_exceptions():
    """Testa as exceções personalizadas"""
    # Testa OAuthException base
    base_exc = OAuthException("Base error")
    assert str(base_exc) == "Base error"

    # Testa TokenExpiredException
    expired_exc = TokenExpiredException("Token expired")
    assert str(expired_exc) == "Token expired"
    assert isinstance(expired_exc, OAuthException)

    # Testa InvalidTokenException
    invalid_exc = InvalidTokenException("Invalid token")
    assert str(invalid_exc) == "Invalid token"
    assert isinstance(invalid_exc, OAuthException)
