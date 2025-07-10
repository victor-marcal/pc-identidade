"""
Testes simples para melhorar cobertura de seller_service.py
"""

import pytest
from datetime import date
from unittest.mock import AsyncMock, Mock, patch
from fastapi import HTTPException
from app.services.seller_service import SellerService
from app.models.seller_model import Seller
from app.api.common.auth_handler import UserAuthInfo
from app.models.base import UserModel
from app.api.v1.schemas.seller_schema import SellerCreate, SellerUpdate, SellerReplace
from app.common.exceptions.bad_request_exception import BadRequestException
from app.common.exceptions.not_found_exception import NotFoundException
from app.models.enums import BrazilianState, AccountType, ProductCategory
from unittest.mock import MagicMock


class TestSellerServiceSimple:
    """Testes simples para SellerService"""

    @pytest.fixture
    def mock_repository(self):
        repository = AsyncMock()
        repository.find_by_id = AsyncMock(return_value=None)
        repository.find_by_trade_name = AsyncMock(return_value=None)
        repository.create = AsyncMock(return_value={"_id": "test_id"})
        repository.find = AsyncMock(return_value=[])
        repository.update = AsyncMock(return_value={"_id": "test_id"})
        repository.delete = AsyncMock(return_value=True)
        return repository

    @pytest.fixture
    def mock_keycloak_client(self):
        client = AsyncMock()
        client.update_user_attributes = AsyncMock()
        return client

    @pytest.fixture
    def seller_service(self, mock_repository, mock_keycloak_client):
        service = SellerService(
            repository=mock_repository,
            keycloak_client=mock_keycloak_client
        )
        # Mock the webhook_service that gets created internally
        service.webhook_service = AsyncMock()
        service.webhook_service.send_update_message = AsyncMock()
        return service

    @pytest.fixture
    def user_auth_info(self):
        return UserAuthInfo(
            user=UserModel(name="test-user", server="test-server"),
            trace_id="test-trace",
            sellers=["existing_seller"],
            info_token={"sub": "test-user"}
        )

    @pytest.fixture
    def seller_create_data(self):
        return SellerCreate(
            seller_id="newseller123",
            company_name="Test Company Ltd",
            trade_name="Test Trade Name",
            cnpj="12345678901234",
            state_municipal_registration="123456789",
            commercial_address="Test Address, 123",
            contact_phone="11999999999",
            contact_email="test@example.com",
            legal_rep_full_name="John Doe1",
            legal_rep_cpf="12345678901",
            legal_rep_rg_number="123456789",
            legal_rep_rg_state=BrazilianState.SP,
            legal_rep_birth_date=date(1980, 1, 1),
            legal_rep_phone="11999999999",
            legal_rep_email="john@example.com",
            bank_name="Test Bank",
            agency_account="0001-1",
            account_type=AccountType.CURRENT,
            account_holder_name="John Doe2",
            product_categories=[ProductCategory.AUTOMOTIVE],
            business_description="Test business description"
        )

    @pytest.mark.asyncio
    async def test_create_seller_duplicate_id(self, seller_service, user_auth_info, seller_create_data, mock_repository):
        """Testa criar seller com ID duplicado"""
        # Simula que já existe um seller com esse ID
        mock_repository.find_by_id.return_value = {"seller_id": "new_seller"}
        
        with pytest.raises(BadRequestException):
            await seller_service.create(seller_create_data, user_auth_info)

    @pytest.mark.asyncio
    async def test_create_seller_duplicate_trade_name(self, seller_service, user_auth_info, seller_create_data, mock_repository):
        """Testa criar seller com trade_name duplicado"""
        # Simula que não existe seller com o ID, mas existe com trade_name
        mock_repository.find_by_id.return_value = None
        mock_repository.find_by_trade_name.return_value = {"trade_name": "Test Trade"}
        
        with pytest.raises(BadRequestException):
            await seller_service.create(seller_create_data, user_auth_info)

    @pytest.mark.asyncio 
    @patch('app.services.seller_service.publish_seller_message')
    async def test_create_seller_rabbitmq_failure(self, mock_publish, seller_service, user_auth_info, seller_create_data):
        """Testa criação de seller com falha no RabbitMQ (não deve interromper operação)"""
        # Simula falha na publicação do RabbitMQ
        mock_publish.side_effect = Exception("RabbitMQ error")
        
        # Deve criar o seller mesmo com falha no RabbitMQ
        result = await seller_service.create(seller_create_data, user_auth_info)
        assert result is not None

    @pytest.mark.asyncio
    async def test_create_seller_webhook_failure(self, seller_service, user_auth_info, seller_create_data):
        """Testa criação de seller com falha no webhook (não deve interromper operação)"""
        # Simula falha no webhook
        seller_service.webhook_service.send_update_message.side_effect = Exception("Webhook error")
        
        # Deve criar o seller mesmo com falha no webhook
        result = await seller_service.create(seller_create_data, user_auth_info)
        assert result is not None

    @pytest.mark.asyncio
    async def test_create_seller_user_already_has_seller(self, seller_service, user_auth_info, seller_create_data, mock_keycloak_client):
        """Testa criação quando usuário já tem o seller na lista"""
        # Modifica user_auth_info para já ter o seller
        user_auth_info.sellers = ["newseller123", "existing_seller"]
        
        result = await seller_service.create(seller_create_data, user_auth_info)
        assert result is not None
        # Não deve tentar atualizar Keycloak se já tem o seller
        mock_keycloak_client.update_user_attributes.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_seller_not_found(self, seller_service, user_auth_info, mock_repository):
        """Testa atualização de seller inexistente"""
        mock_repository.find_by_id.return_value = None
        
        update_data = SellerUpdate(trade_name="Updated Trade")
        
        with pytest.raises(NotFoundException):
            await seller_service.update("nonexistent_seller", update_data, user_auth_info)

    @pytest.mark.asyncio
    async def test_replace_seller_not_found(self, seller_service, user_auth_info, mock_repository):
        """Testa substituição de seller inexistente"""
        mock_repository.find_by_id.return_value = None
        
        replace_data = SellerReplace(
            company_name="Test Company Ltd",
            trade_name="Test Trade Name",
            cnpj="12345678901234",
            state_municipal_registration="123456789",
            commercial_address="Test Address, 123",
            contact_phone="11999999999",
            contact_email="test@example.com",
            legal_rep_full_name="John Doe3",
            legal_rep_cpf="12345678901",
            legal_rep_rg_number="123456789",
            legal_rep_rg_state=BrazilianState.SP,
            legal_rep_birth_date=date(1980, 1, 1),
            legal_rep_phone="11999999999",
            legal_rep_email="john@example.com",
            bank_name="Test Bank",
            agency_account="0001-1",
            account_type=AccountType.CURRENT,
            account_holder_name="John Doe4",
            product_categories=[ProductCategory.AUTOMOTIVE],
            business_description="Test business description"
        )
        
        with pytest.raises(NotFoundException):
            await seller_service.replace("nonexistent_seller", replace_data, user_auth_info)

    @pytest.mark.asyncio
    async def test_delete_seller_not_found(self, seller_service, user_auth_info, mock_repository):
        """Testa exclusão de seller inexistente"""
        mock_repository.find_by_id.return_value = None
        
        with pytest.raises(NotFoundException):
            await seller_service.delete_by_id("nonexistent_seller", user_auth_info)

    @pytest.mark.asyncio
    async def test_find_by_id_existing_seller(self, seller_service, mock_repository):
        """Testa buscar seller existente"""
        mock_seller = MagicMock()
        mock_seller.seller_id = "test_seller"
        mock_seller.trade_name = "Test"
        mock_seller.status = "Ativo"

        mock_repository.find_by_id.return_value = mock_seller

        result = await seller_service.find_by_id("test_seller")
        assert result == mock_seller

    @pytest.mark.asyncio
    async def test_find_by_id_nonexistent_seller(self, seller_service, mock_repository):
        """Testa buscar seller inexistente"""
        mock_repository.find_by_id.return_value = None
        
        # The base implementation might not raise an exception, so just test it returns None
        result = await seller_service.find_by_id("nonexistent_seller")
        assert result is None

    @pytest.mark.asyncio
    async def test_find_by_cnpj_existing_seller(self, seller_service, mock_repository):
        """Testa buscar seller por CNPJ existente"""
        mock_seller = {"seller_id": "test_seller", "cnpj": "12345678901234"}
        mock_repository.find_by_cnpj = AsyncMock(return_value=mock_seller)
        
        result = await seller_service.find_by_cnpj("12345678901234")
        assert result == mock_seller

    @pytest.mark.asyncio
    async def test_find_by_cnpj_nonexistent_seller(self, seller_service, mock_repository):
        """Testa buscar seller por CNPJ inexistente"""
        mock_repository.find_by_cnpj = AsyncMock(return_value=None)
        
        with pytest.raises(NotFoundException):
            await seller_service.find_by_cnpj("00000000000000")
