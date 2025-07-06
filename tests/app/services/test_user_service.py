"""
Testes unitários para o UserService.
"""
import pytest
from unittest.mock import AsyncMock

from app.services.user_service import UserService
from app.api.v1.schemas.user_schema import UserCreate, UserPatch
from app.common.exceptions import NotFoundException, BadRequestException

# --- Dados de Teste ---
TEST_USER_ID = "a1b2c3d4-e5f6-7890-1234-567890abcdef"
TEST_USER_DATA = {
    "id": TEST_USER_ID,
    "username": "testuser",
    "email": "test@example.com",
    "firstName": "Test",
    "lastName": "User",
    "enabled": True,
    "attributes": {"sellers": ["seller_a"]},
}


# --- Fixtures ---

@pytest.fixture
def mock_keycloak_client():
    """Cria um mock para o KeycloakAdminClient."""
    return AsyncMock()


@pytest.fixture
def user_service(mock_keycloak_client):
    """Cria uma instância do UserService com o cliente mockado."""
    return UserService(keycloak_client=mock_keycloak_client)


# --- Testes para create_user ---

@pytest.mark.asyncio
async def test_create_user_success(user_service, mock_keycloak_client):
    """
    Testa se create_user chama o cliente para criar e depois buscar o usuário.
    """
    mock_keycloak_client.create_user.return_value = TEST_USER_ID
    mock_keycloak_client.get_user.return_value = TEST_USER_DATA

    user_create_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123",
        first_name="Test",
        last_name="User"
    )

    result = await user_service.create_user(user_create_data)

    mock_keycloak_client.create_user.assert_called_once()
    mock_keycloak_client.get_user.assert_called_once_with(TEST_USER_ID)
    assert result.id == TEST_USER_ID
    assert result.username == "testuser"


# --- Testes para get_user_by_id ---

@pytest.mark.asyncio
async def test_get_user_by_id_success(user_service, mock_keycloak_client):
    """Testa a busca de um usuário existente."""
    mock_keycloak_client.get_user.return_value = TEST_USER_DATA

    result = await user_service.get_user_by_id(TEST_USER_ID)

    mock_keycloak_client.get_user.assert_called_once_with(TEST_USER_ID)
    assert result.id == TEST_USER_ID


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_service, mock_keycloak_client):
    """Testa a busca de um usuário inexistente, esperando NotFoundException."""
    mock_keycloak_client.get_user.return_value = None

    with pytest.raises(NotFoundException):
        await user_service.get_user_by_id("non_existent_id")


# --- Testes para get_all_users ---

@pytest.mark.asyncio
async def test_get_all_users_success(user_service, mock_keycloak_client):
    """Testa a listagem de usuários válidos."""
    users_from_keycloak = [
        TEST_USER_DATA,
        {"id": "id2", "username": "user2", "email": "user2@e.com", "enabled": True}
    ]
    mock_keycloak_client.get_users.return_value = users_from_keycloak

    result = await user_service.get_all_users()

    assert len(result) == 2
    assert result[0].username == "testuser"
    assert result[1].username == "user2"


@pytest.mark.asyncio
async def test_get_all_users_with_invalid_data(user_service, mock_keycloak_client, caplog):
    """Testa se a listagem ignora usuários com dados incompletos e loga um aviso."""
    users_from_keycloak = [
        TEST_USER_DATA,
        {"id": "invalid_id"}  # Usuário sem username e email
    ]
    mock_keycloak_client.get_users.return_value = users_from_keycloak

    result = await user_service.get_all_users()

    assert len(result) == 1
    assert "Usuário ignorado devido a dados incompletos" in caplog.text



@pytest.mark.asyncio
async def test_delete_user_success(user_service, mock_keycloak_client):
    """Testa a exclusão bem-sucedida de um usuário."""
    mock_keycloak_client.delete_user.return_value = True

    await user_service.delete_user(TEST_USER_ID)

    mock_keycloak_client.delete_user.assert_called_once_with(TEST_USER_ID)


@pytest.mark.asyncio
async def test_delete_user_not_found(user_service, mock_keycloak_client):
    """Testa a exclusão de um usuário inexistente, esperando NotFoundException."""
    mock_keycloak_client.delete_user.return_value = False

    with pytest.raises(NotFoundException):
        await user_service.delete_user("non_existent_id")


# --- Testes para patch_user ---

@pytest.mark.asyncio
async def test_patch_user_all_fields(user_service, mock_keycloak_client):
    """Testa o PATCH atualizando dados de perfil e senha."""
    mock_keycloak_client.get_user.return_value = TEST_USER_DATA
    patch_data = UserPatch(first_name="NewName", password="NewPassword")

    await user_service.patch_user(TEST_USER_ID, patch_data)

    mock_keycloak_client.update_user.assert_called_once_with(TEST_USER_ID, {"first_name": "NewName"})
    mock_keycloak_client.reset_user_password.assert_called_once_with(TEST_USER_ID, "NewPassword")
    mock_keycloak_client.get_user.assert_called_once_with(TEST_USER_ID)


@pytest.mark.asyncio
async def test_patch_user_only_profile(user_service, mock_keycloak_client):
    """Testa o PATCH atualizando apenas dados de perfil."""
    mock_keycloak_client.get_user.return_value = TEST_USER_DATA
    patch_data = UserPatch(email="new@email.com")

    await user_service.patch_user(TEST_USER_ID, patch_data)

    mock_keycloak_client.update_user.assert_called_once_with(TEST_USER_ID, {"email": "new@email.com"})
    mock_keycloak_client.reset_user_password.assert_not_called()


@pytest.mark.asyncio
async def test_patch_user_only_password(user_service, mock_keycloak_client):
    """Testa o PATCH atualizando apenas a senha."""
    mock_keycloak_client.get_user.return_value = TEST_USER_DATA
    patch_data = UserPatch(password="OnlyNewPassword")

    await user_service.patch_user(TEST_USER_ID, patch_data)

    mock_keycloak_client.update_user.assert_not_called()
    mock_keycloak_client.reset_user_password.assert_called_once_with(TEST_USER_ID, "OnlyNewPassword")


@pytest.mark.asyncio
async def test_patch_user_raises_bad_request(user_service, mock_keycloak_client):
    """Testa se o patch_user propaga a BadRequestException do cliente."""
    # Simula o cliente levantando um erro de conflito
    mock_keycloak_client.update_user.side_effect = BadRequestException(message="Conflict")
    patch_data = UserPatch(email="conflict@email.com")

    with pytest.raises(BadRequestException):
        await user_service.patch_user(TEST_USER_ID, patch_data)
