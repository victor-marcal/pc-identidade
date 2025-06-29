import pytest
from unittest.mock import AsyncMock, MagicMock
from app.common.exceptions import BadRequestException, NotFoundException
from app.models.seller_model import Seller
from app.models.seller_patch_model import SellerPatch
from app.api.common.auth_handler import UserAuthInfo
from app.models.base import UserModel
from app.api.v1.schemas.seller_schema import SellerCreate
from app.services.seller_service import SellerService
from app.clients.keycloak_admin_client import KeycloakAdminClient
from app.repositories import SellerRepository

# --- Mocks e Dados de Teste ---


@pytest.fixture
def fake_auth_info() -> UserAuthInfo:
    return UserAuthInfo(
        user=UserModel(name="test-user-sub-123", server="http://fake-keycloak/realms/test"),
        trace_id="fake-trace-id-abc",
        sellers=["001"],
    )

@pytest.fixture
def mock_repository():
    return AsyncMock(spec=SellerRepository)

@pytest.fixture
def mock_keycloak_client():
    return AsyncMock(spec=KeycloakAdminClient)

@pytest.fixture
def seller_create_data():
    return SellerCreate(seller_id='001', nome_fantasia='Loja X', cnpj='12345678901234')

@pytest.fixture
def existing_seller_model():
    return Seller(seller_id='001', nome_fantasia='Loja X', cnpj='12345678901234', created_by="system:init")

@pytest.fixture
def patch_data():
    return SellerPatch(nome_fantasia='Nova Loja')


@pytest.mark.asyncio
async def test_create_success(mock_repository, mock_keycloak_client, seller_create_data):
    # Setup
    mock_repository.find_by_id.return_value = None
    mock_repository.find_by_nome_fantasia.return_value = None
    mock_keycloak_client.create_user.return_value = "keycloak:new-user-id"
    mock_repository.create.side_effect = lambda seller: seller  # O mock de create retorna o que recebeu

    service = SellerService(mock_repository, mock_keycloak_client)

    result = await service.create(seller_create_data)

    assert result.seller_id == seller_create_data.seller_id
    assert result.created_by == "keycloak:new-user-id"
    mock_repository.create.assert_called_once()


# --- Testes para o Método `update` (PATCH) ---

@pytest.mark.asyncio
async def test_update_success(mock_repository, mock_keycloak_client, existing_seller_model, patch_data, fake_auth_info):
    mock_repository.find_by_id.return_value = existing_seller_model
    mock_repository.find_by_nome_fantasia.return_value = None
    mock_repository.patch.side_effect = lambda _, fields: existing_seller_model.model_copy(update=fields)

    service = SellerService(mock_repository, mock_keycloak_client)

    result = await service.update(existing_seller_model.seller_id, patch_data, auth_info=fake_auth_info)

    assert result.nome_fantasia == patch_data.nome_fantasia
    assert result.updated_by is not None
    mock_repository.patch.assert_called_once()


@pytest.mark.asyncio
async def test_update_not_found(mock_repository, mock_keycloak_client, patch_data, fake_auth_info):
    mock_repository.find_by_id.return_value = None
    service = SellerService(mock_repository, mock_keycloak_client)

    with pytest.raises(NotFoundException):
        await service.update("non-existent-id", patch_data, auth_info=fake_auth_info)


@pytest.mark.asyncio
async def test_update_nome_fantasia_conflict(mock_repository, mock_keycloak_client, existing_seller_model, patch_data,
                                             fake_auth_info):
    mock_repository.find_by_id.return_value = existing_seller_model
    mock_repository.find_by_nome_fantasia.return_value = Seller(seller_id="outro_id", nome_fantasia="Nova Loja",
                                                                cnpj="111")

    service = SellerService(mock_repository, mock_keycloak_client)

    with pytest.raises(BadRequestException):
        await service.update(existing_seller_model.seller_id, patch_data, auth_info=fake_auth_info)


# --- Testes para o Método `replace` (PUT) ---

@pytest.mark.asyncio
async def test_replace_success(mock_repository, mock_keycloak_client, existing_seller_model, fake_auth_info):
    mock_repository.find_by_id.return_value = existing_seller_model
    mock_repository.find_by_nome_fantasia.return_value = None

    replace_data = Seller(seller_id='001', nome_fantasia='Loja Substituida', cnpj='11111111111111')

    mock_repository.update.side_effect = lambda _, seller_to_update: seller_to_update

    service = SellerService(mock_repository, mock_keycloak_client)

    result = await service.replace(existing_seller_model.seller_id, replace_data, auth_info=fake_auth_info)

    assert result.nome_fantasia == "Loja Substituida"
    assert result.created_by == existing_seller_model.created_by  # Preservou o criador original
    assert result.updated_by == f"{fake_auth_info.user.server}:{fake_auth_info.user.name}"  # Verificou o novo atualizador
    mock_repository.update.assert_called_once()

@pytest.mark.asyncio
async def test_replace_not_found(mock_repository, mock_keycloak_client, existing_seller_model, fake_auth_info):
    mock_repository.find_by_id.return_value = None
    service = SellerService(mock_repository, mock_keycloak_client)

    with pytest.raises(NotFoundException):
        await service.replace("non-existent-id", existing_seller_model, auth_info=fake_auth_info)
