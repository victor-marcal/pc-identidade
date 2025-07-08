"""
Testes de autenticação com Keycloak para sellers e usuários.
Foca em cenários de autenticação, autorização, diferenças entre admin e usuário normal.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.api.common.auth_handler import (
    get_current_user_info,
    require_seller_permission,
    require_admin_user,
    do_auth,
    UserAuthInfo,
)
from app.models.base import UserModel
from app.common.exceptions import UnauthorizedException, ForbiddenException
from app.integrations.auth.keycloak_adapter import (
    TokenExpiredException,
    InvalidTokenException,
    OAuthException,
)


@pytest.fixture
def mock_request():
    """Mock do FastAPI Request"""
    request = MagicMock()
    request.state = MagicMock()
    request.state.trace_id = "trace-123"
    return request


@pytest.fixture
def valid_token_payload():
    """Token payload válido para um usuário normal"""
    return {
        "sub": "user-123",
        "iss": "http://keycloak:8080/realms/test",
        "sellers": ["seller1", "seller2"],
        "exp": 9999999999,  # Token não expirado
    }


@pytest.fixture
def admin_token_payload():
    """Token payload para um usuário administrador"""
    return {
        "sub": "admin-123",
        "iss": "http://keycloak:8080/realms/test",
        "sellers": ["seller1", "seller2"],
        "realm_access": {
            "roles": ["realm-admin", "user"]
        },
        "resource_access": {
            "realm-management": {
                "roles": ["realm-admin"]
            }
        },
        "exp": 9999999999,
    }


@pytest.fixture
def normal_user_auth_info(valid_token_payload):
    """UserAuthInfo para usuário normal"""
    return UserAuthInfo(
        user=UserModel(name="user-123", server="http://keycloak:8080/realms/test"),
        trace_id="trace-123",
        sellers=["seller1", "seller2"],
        info_token=valid_token_payload
    )


@pytest.fixture
def admin_user_auth_info(admin_token_payload):
    """UserAuthInfo para usuário administrador"""
    return UserAuthInfo(
        user=UserModel(name="admin-123", server="http://keycloak:8080/realms/test"),
        trace_id="trace-123",
        sellers=["seller1", "seller2"],
        info_token=admin_token_payload
    )


class TestAuthenticationFlow:
    """Testes do fluxo de autenticação principal"""

    @pytest.mark.asyncio
    async def test_get_current_user_info_success(self, mock_request, valid_token_payload):
        """Testa autenticação bem-sucedida de usuário"""
        mock_adapter = AsyncMock()
        mock_adapter.validate_token.return_value = valid_token_payload
        
        result = await get_current_user_info(mock_request, "valid-token", mock_adapter)
        
        assert isinstance(result, UserAuthInfo)
        assert result.user.name == "user-123"
        assert result.sellers == ["seller1", "seller2"]
        assert result.trace_id == "trace-123"
        mock_adapter.validate_token.assert_called_once_with("valid-token")

    @pytest.mark.asyncio
    async def test_get_current_user_info_no_token(self, mock_request):
        """Testa falha quando não há token"""
        mock_adapter = AsyncMock()
        
        with pytest.raises(UnauthorizedException) as exc_info:
            await get_current_user_info(mock_request, None, mock_adapter)
        
        assert "Não autenticado" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_current_user_info_expired_token(self, mock_request):
        """Testa falha com token expirado"""
        mock_adapter = AsyncMock()
        mock_adapter.validate_token.side_effect = TokenExpiredException("Token expired")
        
        with pytest.raises(UnauthorizedException) as exc_info:
            await get_current_user_info(mock_request, "expired-token", mock_adapter)
        
        assert "token de acesso expirou" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_current_user_info_invalid_token(self, mock_request):
        """Testa falha com token inválido"""
        mock_adapter = AsyncMock()
        mock_adapter.validate_token.side_effect = InvalidTokenException("Invalid token")
        
        with pytest.raises(UnauthorizedException) as exc_info:
            await get_current_user_info(mock_request, "invalid-token", mock_adapter)
        
        assert "token de acesso é inválido" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_current_user_info_oauth_exception(self, mock_request):
        """Testa falha com exceção OAuth"""
        mock_adapter = AsyncMock()
        mock_adapter.validate_token.side_effect = OAuthException("OAuth error")
        
        with pytest.raises(UnauthorizedException) as exc_info:
            await get_current_user_info(mock_request, "token", mock_adapter)
        
        assert "Falha na autenticação" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_current_user_info_generic_exception(self, mock_request):
        """Testa falha com exceção genérica"""
        mock_adapter = AsyncMock()
        mock_adapter.validate_token.side_effect = Exception("Generic error")
        
        with pytest.raises(UnauthorizedException) as exc_info:
            await get_current_user_info(mock_request, "token", mock_adapter)
        
        assert "Falha na autenticação" in str(exc_info.value)

    def test_user_auth_info_to_sellers_string(self):
        """Testa conversão de string para lista de sellers"""
        result = UserAuthInfo.to_sellers("seller1,seller2,seller3")
        assert result == ["seller1", "seller2", "seller3"]

    def test_user_auth_info_to_sellers_list(self):
        """Testa conversão de lista para lista de sellers"""
        result = UserAuthInfo.to_sellers(["seller1", "seller2"])
        assert result == ["seller1", "seller2"]

    def test_user_auth_info_to_sellers_empty_string(self):
        """Testa conversão de string vazia"""
        result = UserAuthInfo.to_sellers("")
        assert result == []

    def test_user_auth_info_to_sellers_none(self):
        """Testa conversão de None"""
        result = UserAuthInfo.to_sellers(None)
        assert result == []


class TestSellerPermissions:
    """Testes de permissões específicas para sellers"""

    def test_require_seller_permission_success(self, normal_user_auth_info):
        """Testa permissão válida para seller"""
        result = require_seller_permission("seller1", normal_user_auth_info)
        assert result == normal_user_auth_info

    def test_require_seller_permission_forbidden(self, normal_user_auth_info):
        """Testa acesso negado para seller não autorizado"""
        with pytest.raises(ForbiddenException) as exc_info:
            require_seller_permission("seller3", normal_user_auth_info)
        
        assert "não tem permissão para acessar este seller" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_do_auth_success(self, mock_request, valid_token_payload):
        """Testa função do_auth com sucesso"""
        mock_adapter = AsyncMock()
        mock_adapter.validate_token.return_value = valid_token_payload
        
        await do_auth(mock_request, "valid-token", "seller1", mock_adapter)
        
        # Verifica se o usuário foi salvo no request.state
        assert hasattr(mock_request.state, 'user')
        assert mock_request.state.user.user.name == "user-123"

    @pytest.mark.asyncio
    async def test_do_auth_seller_forbidden(self, mock_request, valid_token_payload):
        """Testa do_auth com seller não autorizado"""
        mock_adapter = AsyncMock()
        mock_adapter.validate_token.return_value = valid_token_payload
        
        with pytest.raises(ForbiddenException) as exc_info:
            await do_auth(mock_request, "valid-token", "seller3", mock_adapter)
        
        assert "não tem permissão para acessar este seller" in str(exc_info.value)


class TestAdminPermissions:
    """Testes de permissões administrativas"""

    def test_require_admin_user_success_realm_roles(self, admin_user_auth_info):
        """Testa acesso admin através de realm_access.roles"""
        result = require_admin_user(admin_user_auth_info)
        assert result == admin_user_auth_info

    def test_require_admin_user_success_resource_access(self):
        """Testa acesso admin através de resource_access"""
        token_payload = {
            "sub": "admin-123",
            "resource_access": {
                "realm-management": {
                    "roles": ["realm-admin"]
                }
            }
        }
        
        auth_info = UserAuthInfo(
            user=UserModel(name="admin-123", server="test"),
            trace_id="trace-123",
            sellers=["seller1"],
            info_token=token_payload
        )
        
        result = require_admin_user(auth_info)
        assert result == auth_info

    def test_require_admin_user_forbidden_no_admin_role(self, normal_user_auth_info):
        """Testa acesso negado para usuário sem role admin"""
        with pytest.raises(ForbiddenException) as exc_info:
            require_admin_user(normal_user_auth_info)
        
        assert "privilégios de administrador" in str(exc_info.value)

    def test_require_admin_user_forbidden_wrong_role(self):
        """Testa acesso negado com role errada"""
        token_payload = {
            "sub": "user-123",
            "realm_access": {
                "roles": ["user", "seller-manager"]  # Sem realm-admin
            }
        }
        
        auth_info = UserAuthInfo(
            user=UserModel(name="user-123", server="test"),
            trace_id="trace-123",
            sellers=["seller1"],
            info_token=token_payload
        )
        
        with pytest.raises(ForbiddenException) as exc_info:
            require_admin_user(auth_info)
        
        assert "privilégios de administrador" in str(exc_info.value)


class TestUserAuthorizationScenarios:
    """Testes de cenários de autorização para endpoints de usuários"""

    def test_user_can_access_own_data(self):
        """Testa que usuário pode acessar seus próprios dados"""
        token_payload = {"sub": "user-123"}
        auth_info = UserAuthInfo(
            user=UserModel(name="user-123", server="test"),
            trace_id="trace-123",
            sellers=["seller1"],
            info_token=token_payload
        )
        
        # Simula verificação do endpoint GET /users/{user_id}
        user_id = "user-123"
        realm_access = auth_info.info_token.get("realm_access", {})
        realm_roles = realm_access.get("roles", [])
        is_admin = "realm-admin" in realm_roles
        
        # Usuário não é admin mas está acessando seus próprios dados
        can_access = is_admin or auth_info.user.name == user_id
        assert can_access is True

    def test_user_cannot_access_other_user_data(self):
        """Testa que usuário não pode acessar dados de outros"""
        token_payload = {"sub": "user-123"}
        auth_info = UserAuthInfo(
            user=UserModel(name="user-123", server="test"),
            trace_id="trace-123",
            sellers=["seller1"],
            info_token=token_payload
        )
        
        # Simula verificação do endpoint GET /users/{user_id}
        user_id = "user-456"  # Tentando acessar outro usuário
        realm_access = auth_info.info_token.get("realm_access", {})
        realm_roles = realm_access.get("roles", [])
        is_admin = "realm-admin" in realm_roles
        
        # Usuário não é admin e não está acessando seus próprios dados
        can_access = is_admin or auth_info.user.name == user_id
        assert can_access is False

    def test_admin_can_access_any_user_data(self, admin_user_auth_info):
        """Testa que admin pode acessar dados de qualquer usuário"""
        # Simula verificação do endpoint GET /users/{user_id}
        user_id = "any-user-456"
        realm_access = admin_user_auth_info.info_token.get("realm_access", {})
        realm_roles = realm_access.get("roles", [])
        is_admin = "realm-admin" in realm_roles
        
        # Admin pode acessar dados de qualquer usuário
        can_access = is_admin or admin_user_auth_info.user.name == user_id
        assert can_access is True

    def test_user_can_delete_own_account(self):
        """Testa que usuário pode deletar sua própria conta"""
        token_payload = {"sub": "user-123"}
        auth_info = UserAuthInfo(
            user=UserModel(name="user-123", server="test"),
            trace_id="trace-123",
            sellers=["seller1"],
            info_token=token_payload
        )
        
        # Simula verificação do endpoint DELETE /users/{user_id}
        user_id = "user-123"
        realm_access = auth_info.info_token.get("realm_access", {})
        realm_roles = realm_access.get("roles", [])
        is_admin = "realm-admin" in realm_roles
        
        can_delete = is_admin or auth_info.user.name == user_id
        assert can_delete is True

    def test_user_cannot_delete_other_accounts(self):
        """Testa que usuário não pode deletar contas de outros"""
        token_payload = {"sub": "user-123"}
        auth_info = UserAuthInfo(
            user=UserModel(name="user-123", server="test"),
            trace_id="trace-123",
            sellers=["seller1"],
            info_token=token_payload
        )
        
        # Simula verificação do endpoint DELETE /users/{user_id}
        user_id = "user-456"
        realm_access = auth_info.info_token.get("realm_access", {})
        realm_roles = realm_access.get("roles", [])
        is_admin = "realm-admin" in realm_roles
        
        can_delete = is_admin or auth_info.user.name == user_id
        assert can_delete is False


class TestSellerAuthorizationScenarios:
    """Testes de cenários de autorização para endpoints de sellers"""

    def test_user_can_access_authorized_seller(self, normal_user_auth_info):
        """Testa acesso a seller autorizado"""
        seller_id = "seller1"
        has_permission = seller_id in normal_user_auth_info.sellers
        assert has_permission is True

    def test_user_cannot_access_unauthorized_seller(self, normal_user_auth_info):
        """Testa bloqueio de acesso a seller não autorizado"""
        seller_id = "seller3"
        has_permission = seller_id in normal_user_auth_info.sellers
        assert has_permission is False

    def test_user_multiple_sellers_access(self, normal_user_auth_info):
        """Testa acesso a múltiplos sellers autorizados"""
        for seller_id in ["seller1", "seller2"]:
            has_permission = seller_id in normal_user_auth_info.sellers
            assert has_permission is True

    def test_empty_sellers_list(self):
        """Testa usuário sem sellers atribuídos"""
        token_payload = {"sub": "user-123", "sellers": ""}
        auth_info = UserAuthInfo(
            user=UserModel(name="user-123", server="test"),
            trace_id="trace-123",
            sellers=UserAuthInfo.to_sellers(token_payload.get("sellers")),
            info_token=token_payload
        )
        
        seller_id = "seller1"
        has_permission = seller_id in auth_info.sellers
        assert has_permission is False
        assert auth_info.sellers == []

    def test_seller_list_from_token_string(self):
        """Testa parsing de lista de sellers do token como string"""
        token_payload = {"sub": "user-123", "sellers": "seller1,seller2,seller3"}
        sellers = UserAuthInfo.to_sellers(token_payload.get("sellers"))
        assert sellers == ["seller1", "seller2", "seller3"]

    def test_seller_list_from_token_array(self):
        """Testa parsing de lista de sellers do token como array"""
        token_payload = {"sub": "user-123", "sellers": ["seller1", "seller2"]}
        sellers = UserAuthInfo.to_sellers(token_payload.get("sellers"))
        assert sellers == ["seller1", "seller2"]
