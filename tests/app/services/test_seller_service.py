import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date
from app.common.exceptions import BadRequestException, NotFoundException
from app.models.seller_model import Seller
from app.models.seller_patch_model import SellerPatch
from app.api.common.auth_handler import UserAuthInfo
from app.models.base import UserModel
from app.api.v1.schemas.seller_schema import SellerCreate
from app.services.seller_service import SellerService
from app.clients.keycloak_admin_client import KeycloakAdminClient
from app.repositories import SellerRepository
from app.models.enums import BrazilianState, AccountType, ProductCategory
from tests.helpers.test_fixtures import create_full_seller

# --- Mocks e Dados de Teste ---

EMPRESA_TESTE = 'Empresa Teste Ltda'
@pytest.fixture
def fake_auth_info() -> UserAuthInfo:
    return UserAuthInfo(
        user=UserModel(name="test-user-sub-123", server="https://fake-keycloak/realms/test"),
        trace_id="fake-trace-id-abc",
        sellers=["001"],
        info_token={"token": "fake-token"}
    )


@pytest.fixture
def mock_repository():
    return AsyncMock(spec=SellerRepository)


@pytest.fixture
def mock_keycloak_client():
    return AsyncMock(spec=KeycloakAdminClient)


@pytest.fixture
def seller_create_data():
    return SellerCreate(
        seller_id='001',
        company_name=EMPRESA_TESTE,
        trade_name='Loja X',
        cnpj='12345678901234',
        state_municipal_registration='123456789',
        commercial_address='Rua Teste, 123',
        contact_phone='11999999999',
        contact_email='contato@lojax.com',
        legal_rep_full_name='João Silva',
        legal_rep_cpf='12345678901',
        legal_rep_rg_number='123456789',
        legal_rep_rg_state=BrazilianState.SP,
        legal_rep_birth_date=date(1990, 1, 1),
        legal_rep_phone='11888888888',
        legal_rep_email='joao@lojax.com',
        bank_name='banco do brasil2',
        agency_account='1234-5/67890-3',
        account_type=AccountType.CURRENT,
        account_holder_name=EMPRESA_TESTE,
        product_categories=[ProductCategory.COMPUTING],
        business_description='artesanato'
    )


@pytest.fixture
def existing_seller_model():
    return Seller(
        seller_id='001',
        company_name=EMPRESA_TESTE,
        trade_name='Loja X',
        cnpj='12345678901234',
        state_municipal_registration='123456789',
        commercial_address='Rua Teste, 123',
        contact_phone='11999999999',
        contact_email='contato@lojax.com',
        legal_rep_full_name='João Silva1',
        legal_rep_cpf='12345678901',
        legal_rep_rg_number='123456789',
        legal_rep_rg_state=BrazilianState.SP,
        legal_rep_birth_date=date(1990, 1, 1),
        legal_rep_phone='11888888888',
        legal_rep_email='joao@lojax.com',
        bank_name='banco do brasil1',
        agency_account='1234-5/67890-1',
        account_type=AccountType.CURRENT,
        account_holder_name=EMPRESA_TESTE,
        product_categories=[ProductCategory.COMPUTING],
        business_description='cama, mesa e banho',
        created_by="system:init"
    )


@pytest.fixture
def patch_data():
    return SellerPatch(trade_name='Nova Loja')


@pytest.mark.asyncio
async def test_create_success(mock_repository, mock_keycloak_client, seller_create_data, fake_auth_info):
    # Setup
    mock_repository.find_by_id.return_value = None
    mock_repository.find_by_trade_name.return_value = None
    mock_keycloak_client.create_user.return_value = "keycloak:new-user-id"
    mock_repository.create.side_effect = lambda seller: seller  # O mock de create retorna o que recebeu

    service = SellerService(mock_repository, mock_keycloak_client)

    result = await service.create(seller_create_data, fake_auth_info)

    assert result.seller_id == seller_create_data.seller_id
    assert result.created_by == "https://fake-keycloak/realms/test:test-user-sub-123"
    mock_repository.create.assert_called_once()


# --- Testes para o Método `update` (PATCH) ---


@pytest.mark.asyncio
async def test_update_success(mock_repository, mock_keycloak_client, existing_seller_model, patch_data, fake_auth_info):
    mock_repository.find_by_id.return_value = existing_seller_model
    mock_repository.find_by_trade_name.return_value = None
    mock_repository.patch.side_effect = lambda _, fields: existing_seller_model.model_copy(update=fields)

    service = SellerService(mock_repository, mock_keycloak_client)

    result = await service.update(existing_seller_model.seller_id, patch_data, auth_info=fake_auth_info)

    assert result.trade_name == patch_data.trade_name
    assert result.updated_by is not None
    mock_repository.patch.assert_called_once()


@pytest.mark.asyncio
async def test_update_not_found(mock_repository, mock_keycloak_client, patch_data, fake_auth_info):
    mock_repository.find_by_id.return_value = None
    service = SellerService(mock_repository, mock_keycloak_client)

    with pytest.raises(NotFoundException):
        await service.update("non-existent-id", patch_data, auth_info=fake_auth_info)


@pytest.mark.asyncio
async def test_update_nome_fantasia_conflict(
    mock_repository, mock_keycloak_client, existing_seller_model, patch_data, fake_auth_info
):
    mock_repository.find_by_id.return_value = existing_seller_model
    mock_repository.find_by_trade_name.return_value = create_full_seller(
        seller_id="outro_id",
        company_name='Outra Empresa Ltda',
        trade_name='Nova Loja',
        cnpj='98765432109876',
        state_municipal_registration='987654321',
        commercial_address='Rua Outra, 456',
        contact_phone='11777777777',
        contact_email='contato@outra.com',
        legal_rep_full_name='Maria Silva',
        legal_rep_cpf='98765432109',
        legal_rep_rg_number='987654321',
        legal_rep_rg_state=BrazilianState.RJ,
        legal_rep_birth_date=date(1985, 5, 5),
        legal_rep_phone='11666666666',
        legal_rep_email='maria@outra.com',
        bank_name='banco do brasil',
        agency_account='9876-5/43210-9',
        account_type=AccountType.SAVINGS,
        account_holder_name='Outra Empresa Ltda',
        product_categories=[ProductCategory.FLOWERS_GARDEN],
        business_description='Venda de produtos para casa e jardim'
    )

    service = SellerService(mock_repository, mock_keycloak_client)

    with pytest.raises(BadRequestException):
        await service.update(existing_seller_model.seller_id, patch_data, auth_info=fake_auth_info)


# --- Testes para o Método `replace` (PUT) ---


@pytest.mark.asyncio
async def test_replace_success(mock_repository, mock_keycloak_client, existing_seller_model, fake_auth_info):
    mock_repository.find_by_id.return_value = existing_seller_model
    mock_repository.find_by_trade_name.return_value = None
    replace_data = create_full_seller(seller_id='001', trade_name='Loja Substituida', cnpj='11111111111111')

    mock_repository.update.side_effect = lambda _, seller_to_update: seller_to_update

    service = SellerService(mock_repository, mock_keycloak_client)

    result = await service.replace(existing_seller_model.seller_id, replace_data, auth_info=fake_auth_info)

    assert result.trade_name == "Loja Substituida"
    assert result.created_by == existing_seller_model.created_by  # Preservou o criador original
    assert (
        result.updated_by == f"{fake_auth_info.user.server}:{fake_auth_info.user.name}"
    )  # Verificou o novo atualizador
    mock_repository.update.assert_called_once()


@pytest.mark.asyncio
async def test_replace_not_found(mock_repository, mock_keycloak_client, existing_seller_model, fake_auth_info):
    mock_repository.find_by_id.return_value = None
    service = SellerService(mock_repository, mock_keycloak_client)

    with pytest.raises(NotFoundException):
        await service.replace("non-existent-id", existing_seller_model, auth_info=fake_auth_info)
