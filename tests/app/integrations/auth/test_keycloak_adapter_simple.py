"""
Testes simples para keycloak_adapter.py focados em cobertura
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx
import jwt
from app.integrations.auth.keycloak_adapter import KeycloakAdapter, TokenExpiredException, InvalidTokenException, OAuthException


class TestKeycloakAdapterSimple:
    """Testes simples para KeycloakAdapter"""
    
    @pytest.fixture
    def mock_redis_adapter(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_well_known_url(self):
        return "https://keycloak.example.com/.well-known/openid_configuration"
    
    @pytest.fixture
    def keycloak_adapter(self, mock_well_known_url, mock_redis_adapter):
        with patch('httpx.Client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {"jwks_uri": "https://keycloak.example.com/jwks"}
            mock_response.raise_for_status.return_value = None
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response
            
            return KeycloakAdapter(mock_well_known_url, mock_redis_adapter)
    
    @pytest.mark.asyncio
    async def test_validate_token_success(self, keycloak_adapter):
        """Testa validação de token com sucesso"""
        # Arrange
        token = "valid_token"
        expected_payload = {"sub": "user123", "email": "user@example.com"}
        
        # Mock jwt operations
        with patch('jwt.get_unverified_header') as mock_header, \
             patch('jwt.decode') as mock_decode, \
             patch.object(keycloak_adapter.jwks_client, 'get_signing_key_from_jwt') as mock_signing_key:
            
            mock_header.return_value = {"alg": "RS256"}
            mock_decode.return_value = expected_payload
            mock_signing_key.return_value = Mock(key="test_key")
            
            # Act
            result = await keycloak_adapter.validate_token(token)
            
            # Assert
            assert result == expected_payload
            mock_decode.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_token_expired(self, keycloak_adapter):
        """Testa validação de token expirado"""
        # Arrange
        token = "expired_token"
        
        # Mock jwt operations
        with patch('jwt.get_unverified_header') as mock_header, \
             patch('jwt.decode') as mock_decode, \
             patch.object(keycloak_adapter.jwks_client, 'get_signing_key_from_jwt') as mock_signing_key:
            
            mock_header.return_value = {"alg": "RS256"}
            mock_decode.side_effect = jwt.ExpiredSignatureError("Token expired")
            mock_signing_key.return_value = Mock(key="test_key")
            
            # Act & Assert
            with pytest.raises(TokenExpiredException):
                await keycloak_adapter.validate_token(token)
    
    @pytest.mark.asyncio
    async def test_validate_token_invalid(self, keycloak_adapter):
        """Testa validação de token inválido"""
        # Arrange
        token = "invalid_token"
        
        # Mock jwt operations
        with patch('jwt.get_unverified_header') as mock_header, \
             patch('jwt.decode') as mock_decode, \
             patch.object(keycloak_adapter.jwks_client, 'get_signing_key_from_jwt') as mock_signing_key:
            
            mock_header.return_value = {"alg": "RS256"}
            mock_decode.side_effect = jwt.InvalidTokenError("Invalid token")
            mock_signing_key.return_value = Mock(key="test_key")
            
            # Act & Assert
            with pytest.raises(InvalidTokenException):
                await keycloak_adapter.validate_token(token)
    
    @pytest.mark.asyncio
    async def test_validate_token_generic_exception(self, keycloak_adapter):
        """Testa validação de token com exceção genérica"""
        # Arrange
        token = "problematic_token"
        
        # Mock jwt operations
        with patch('jwt.get_unverified_header') as mock_header, \
             patch('jwt.decode') as mock_decode, \
             patch.object(keycloak_adapter.jwks_client, 'get_signing_key_from_jwt') as mock_signing_key:
            
            mock_header.return_value = {"alg": "RS256"}
            mock_decode.side_effect = Exception("Unexpected error")
            mock_signing_key.return_value = Mock(key="test_key")
            
            # Act & Assert
            with pytest.raises(OAuthException):
                await keycloak_adapter.validate_token(token)
    
    @pytest.mark.asyncio
    async def test_fetch_and_cache_keys_from_redis(self, keycloak_adapter):
        """Testa busca de chaves do Redis"""
        # Arrange
        cached_keys = {"keys": [{"kid": "test", "kty": "RSA"}]}
        keycloak_adapter.inmemory_adapter.get_json.return_value = cached_keys
        
        # Act
        await keycloak_adapter._fetch_and_cache_keys()
        
        # Assert
        assert keycloak_adapter.jwks_client.jwk_set == cached_keys
        keycloak_adapter.inmemory_adapter.get_json.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_and_cache_keys_from_keycloak(self, keycloak_adapter):
        """Testa busca de chaves diretamente do Keycloak"""
        # Arrange
        keycloak_adapter.inmemory_adapter.get_json.return_value = None
        jwk_set = {"keys": [{"kid": "test", "kty": "RSA"}]}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = jwk_set
            mock_response.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Act
            await keycloak_adapter._fetch_and_cache_keys()
            
            # Assert
            assert keycloak_adapter.jwks_client.jwk_set == jwk_set
            keycloak_adapter.inmemory_adapter.set_json.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_token_key_not_found_then_refetch(self, keycloak_adapter):
        """Testa validação quando chave não é encontrada e é necessário refetch"""
        # Arrange
        token = "token_with_new_key"
        keycloak_adapter.inmemory_adapter.get_json.return_value = None
        
        # Mock jwt operations
        with patch('jwt.get_unverified_header') as mock_header, \
             patch('jwt.decode') as mock_decode, \
             patch.object(keycloak_adapter.jwks_client, 'get_signing_key_from_jwt') as mock_signing_key, \
             patch('httpx.AsyncClient') as mock_client:
            
            # First call fails, second succeeds
            mock_signing_key.side_effect = [jwt.exceptions.PyJWKClientError("Key not found"), Mock(key="test_key")]
            mock_header.return_value = {"alg": "RS256"}
            mock_decode.return_value = {"sub": "user123"}
            
            # Mock HTTP response for key fetch
            mock_response = Mock()
            mock_response.json.return_value = {"keys": []}
            mock_response.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Act
            result = await keycloak_adapter.validate_token(token)
            
            # Assert
            assert result == {"sub": "user123"}
            assert mock_signing_key.call_count == 2
    
    def test_get_jwks_uri_success(self, mock_well_known_url, mock_redis_adapter):
        """Testa obtenção da URI JWKS"""
        with patch('httpx.Client') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {"jwks_uri": "https://keycloak.example.com/jwks"}
            mock_response.raise_for_status.return_value = None
            mock_client.return_value.__enter__.return_value.get.return_value = mock_response
            
            adapter = KeycloakAdapter(mock_well_known_url, mock_redis_adapter)
            
            # Act
            jwks_uri = adapter._get_jwks_uri()
            
            # Assert
            assert jwks_uri == "https://keycloak.example.com/jwks"
            mock_client.return_value.__enter__.return_value.get.assert_called_with(mock_well_known_url)
    
    def test_exceptions_instantiation(self):
        """Testa instanciação das exceções"""
        # Act & Assert
        oauth_exc = OAuthException("Test message")
        assert str(oauth_exc) == "Test message"
        
        token_exp_exc = TokenExpiredException("Token expired")
        assert str(token_exp_exc) == "Token expired"
        
        invalid_token_exc = InvalidTokenException("Invalid token")
        assert str(invalid_token_exc) == "Invalid token"
