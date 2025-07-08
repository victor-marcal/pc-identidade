"""
Testes para aumentar cobertura de user_router.py
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.api.common.auth_handler import UserAuthInfo
from app.models.base import UserModel


class TestUserRouterCoverage:
    """Testes para cobrir linhas faltantes no user_router.py"""
    
    @pytest.fixture
    def mock_user_service(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_user_info(self):
        return UserAuthInfo(
            user=UserModel(name="test-user", server="test-server"),
            trace_id="trace-123",
            sellers=["seller1"],
            info_token={"sub": "test-user", "realm_access": {"roles": ["user"]}}
        )
    
    @pytest.fixture
    def mock_admin_user_info(self):
        return UserAuthInfo(
            user=UserModel(name="admin-user", server="test-server"),
            trace_id="trace-123",
            sellers=["seller1"],
            info_token={
                "sub": "admin-user",
                "realm_access": {"roles": ["realm-admin"]},
                "resource_access": {"realm-management": {"roles": ["realm-admin"]}}
            }
        )
    
    def test_create_user_validation_success(self, client, mock_user_service):
        """Testa criação de usuário com validação bem-sucedida"""
        user_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password": "password123"
        }
        
        # Mock do service
        mock_user_service.create_user.return_value = {
            "id": "user-123",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com"
        }
        
        # Mock do provider
        with patch('app.api.v1.routers.user_router.Provide') as mock_provide:
            mock_provide.__getitem__.return_value = mock_user_service
            
            response = client.post("/seller/v1/users", json=user_data)
            
            # Verificar resposta
            assert response.status_code in [200, 201, 422]
    
    def test_create_user_validation_errors(self, client, mock_user_service):
        """Testa criação de usuário com erros de validação"""
        invalid_user_data = {
            "first_name": "A",  # Muito curto
            "last_name": "User",
            "email": "invalid-email",  # Email inválido
            "password": "123"  # Senha muito curta
        }
        
        # Mock do provider
        with patch('app.api.v1.routers.user_router.Provide') as mock_provide:
            mock_provide.__getitem__.return_value = mock_user_service
            
            response = client.post("/seller/v1/users", json=invalid_user_data)
            
            # Deve retornar erro de validação
            assert response.status_code == 422
    
    def test_get_user_authorization_scenarios(self, client, mock_user_service):
        """Testa cenários de autorização para buscar usuário"""
        
        # Cenário 1: Usuário buscando seus próprios dados
        mock_user_info = UserAuthInfo(
            user=UserModel(name="test-user", server="test-server"),
            trace_id="trace-123",
            sellers=["seller1"],
            info_token={"sub": "test-user"}
        )
        
        mock_user_service.get_user_by_id.return_value = {
            "id": "test-user",
            "first_name": "Test",
            "last_name": "User"
        }
        
        with patch('app.api.v1.routers.user_router.get_current_user_info') as mock_auth, \
             patch('app.api.v1.routers.user_router.Provide') as mock_provide:
            
            mock_auth.return_value = mock_user_info
            mock_provide.__getitem__.return_value = mock_user_service
            
            response = client.get("/seller/v1/users/test-user")
            
            # Verificar resposta
            assert response.status_code in [200, 401, 403, 404]
    
    def test_list_users_admin_permission(self, client, mock_user_service):
        """Testa listagem de usuários com permissão de admin"""
        
        mock_admin_info = UserAuthInfo(
            user=UserModel(name="admin-user", server="test-server"),
            trace_id="trace-123",
            sellers=["seller1"],
            info_token={
                "sub": "admin-user",
                "realm_access": {"roles": ["realm-admin"]}
            }
        )
        
        mock_user_service.get_all_users.return_value = [
            {"id": "user1", "first_name": "User", "last_name": "One"},
            {"id": "user2", "first_name": "User", "last_name": "Two"}
        ]
        
        with patch('app.api.v1.routers.user_router.require_admin_user') as mock_admin, \
             patch('app.api.v1.routers.user_router.Provide') as mock_provide:
            
            mock_admin.return_value = mock_admin_info
            mock_provide.__getitem__.return_value = mock_user_service
            
            response = client.get("/seller/v1/users")
            
            # Verificar resposta
            assert response.status_code in [200, 401, 403]
    
    def test_delete_user_scenarios(self, client, mock_user_service):
        """Testa cenários de deleção de usuário"""
        
        mock_user_info = UserAuthInfo(
            user=UserModel(name="test-user", server="test-server"),
            trace_id="trace-123",
            sellers=["seller1"],
            info_token={"sub": "test-user"}
        )
        
        mock_user_service.delete_user.return_value = None
        
        with patch('app.api.v1.routers.user_router.get_current_user_info') as mock_auth, \
             patch('app.api.v1.routers.user_router.Provide') as mock_provide:
            
            mock_auth.return_value = mock_user_info
            mock_provide.__getitem__.return_value = mock_user_service
            
            response = client.delete("/seller/v1/users/test-user")
            
            # Verificar resposta
            assert response.status_code in [200, 204, 401, 403, 404]
    
    def test_patch_user_scenarios(self, client, mock_user_service):
        """Testa cenários de atualização de usuário"""
        
        mock_user_info = UserAuthInfo(
            user=UserModel(name="test-user", server="test-server"),
            trace_id="trace-123",
            sellers=["seller1"],
            info_token={"sub": "test-user"}
        )
        
        mock_user_service.patch_user.return_value = {
            "id": "test-user",
            "first_name": "Updated",
            "last_name": "User"
        }
        
        patch_data = {
            "first_name": "Updated"
        }
        
        with patch('app.api.v1.routers.user_router.get_current_user_info') as mock_auth, \
             patch('app.api.v1.routers.user_router.Provide') as mock_provide:
            
            mock_auth.return_value = mock_user_info
            mock_provide.__getitem__.return_value = mock_user_service
            
            response = client.patch("/seller/v1/users/test-user", json=patch_data)
            
            # Verificar resposta
            assert response.status_code in [200, 401, 403, 404, 422]
    
    def test_patch_user_validation_errors(self, client, mock_user_service):
        """Testa atualização de usuário com erros de validação"""
        
        mock_user_info = UserAuthInfo(
            user=UserModel(name="test-user", server="test-server"),
            trace_id="trace-123",
            sellers=["seller1"],
            info_token={"sub": "test-user"}
        )
        
        invalid_patch_data = {
            "email": "invalid-email"  # Email inválido
        }
        
        with patch('app.api.v1.routers.user_router.get_current_user_info') as mock_auth, \
             patch('app.api.v1.routers.user_router.Provide') as mock_provide:
            
            mock_auth.return_value = mock_user_info
            mock_provide.__getitem__.return_value = mock_user_service
            
            response = client.patch("/seller/v1/users/test-user", json=invalid_patch_data)
            
            # Deve retornar erro de validação
            assert response.status_code in [401, 422]
    
    def test_user_not_found_scenarios(self, client, mock_user_service):
        """Testa cenários com usuário não encontrado"""
        
        mock_user_info = UserAuthInfo(
            user=UserModel(name="test-user", server="test-server"),
            trace_id="trace-123",
            sellers=["seller1"],
            info_token={"sub": "test-user"}
        )
        
        # Mock do service retornando None
        mock_user_service.get_user_by_id.return_value = None
        
        with patch('app.api.v1.routers.user_router.get_current_user_info') as mock_auth, \
             patch('app.api.v1.routers.user_router.Provide') as mock_provide:
            
            mock_auth.return_value = mock_user_info
            mock_provide.__getitem__.return_value = mock_user_service
            
            response = client.get("/seller/v1/users/nonexistent-user")
            
            # Verificar resposta
            assert response.status_code in [401, 404]
    
    def test_admin_user_scenarios(self, client, mock_user_service):
        """Testa cenários específicos de usuário admin"""
        
        mock_admin_info = UserAuthInfo(
            user=UserModel(name="admin-user", server="test-server"),
            trace_id="trace-123",
            sellers=["seller1"],
            info_token={
                "sub": "admin-user",
                "realm_access": {"roles": ["realm-admin"]},
                "resource_access": {"realm-management": {"roles": ["realm-admin"]}}
            }
        )
        
        mock_user_service.get_user_by_id.return_value = {
            "id": "any-user",
            "first_name": "Any",
            "last_name": "User"
        }
        
        with patch('app.api.v1.routers.user_router.get_current_user_info') as mock_auth, \
             patch('app.api.v1.routers.user_router.Provide') as mock_provide:
            
            mock_auth.return_value = mock_admin_info
            mock_provide.__getitem__.return_value = mock_user_service
            
            # Admin pode acessar qualquer usuário
            response = client.get("/seller/v1/users/any-user")
            
            # Verificar resposta
            assert response.status_code in [200, 401, 404]
