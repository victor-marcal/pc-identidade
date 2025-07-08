from unittest.mock import AsyncMock, MagicMock

import pytest
from dependency_injector.wiring import providers
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from app.api.api_application import create_app
from app.api.router import routes as router
from app.container import Container
from app.settings import ApiSettings, api_settings

# Constantes para testes
TEST_CONSTANTS = {
    "app_name": "TestApp",
    "openapi_path": "/openapi.json",
    "version": "0.1.0",
    "health_check_base_path": "/health",
    "test_user_id": "test-user-id",
    "test_server": "test-server",
    "test_trace_id": "test-trace-id",
    "test_sellers": "1,2,3",
}


@pytest.fixture
def mock_mongo_client():
    client = MagicMock()
    collection = MagicMock()

    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.find_one_and_update = AsyncMock()
    collection.delete_one = AsyncMock()

    class AsyncCursor:
        def __init__(self, docs):
            self.docs = docs

        def skip(self, n):
            return self

        def limit(self, n):
            return self

        def sort(self, *args, **kwargs):
            return self

        def __aiter__(self):
            async def gen():
                for doc in self.docs:
                    yield doc

            return gen()

    collection.find.return_value = AsyncCursor([])

    # Corrigido aqui: mock do database com get_database
    mock_database = MagicMock()
    mock_database.__getitem__ = lambda self, name: collection
    client.get_database.return_value = mock_database

    return client, collection


@pytest.fixture
def dummy_router():
    router = APIRouter()

    @router.get("/dummy")
    async def dummy_route():
        return {"message": "ok"}

    return router


@pytest.fixture
def dummy_settings():
    return ApiSettings(
        app_name=TEST_CONSTANTS["app_name"],
        openapi_path=TEST_CONSTANTS["openapi_path"],
        version=TEST_CONSTANTS["version"],
        health_check_base_path=TEST_CONSTANTS["health_check_base_path"],
    )


@pytest.fixture
def mock_seller_service():
    mock_service = AsyncMock()
    mock_service.find.return_value = []
    mock_service.find_by_id.return_value = None
    mock_service.find_by_cnpj.return_value = None
    mock_service.create.return_value = None
    mock_service.update.return_value = None
    mock_service.delete_by_id.return_value = None
    mock_service.replace.return_value = None
    return mock_service


@pytest.fixture
def mock_user_service():
    mock_service = AsyncMock()
    mock_service.create_user.return_value = None
    mock_service.get_user.return_value = None
    mock_service.get_users.return_value = []
    mock_service.delete_user.return_value = None
    return mock_service


@pytest.fixture
def client(mock_seller_service, mock_user_service):
    from fastapi import Request
    from app.api.common.auth_handler import UserAuthInfo, do_auth, get_current_user
    from app.api.v1.routers import seller_router, user_router
    from app.container import Container
    from app.models.base import UserModel

    app = FastAPI()

    container = Container()
    container.seller_service.override(providers.Object(mock_seller_service))
    container.user_service.override(providers.Object(mock_user_service))

    mock_keycloak_adapter = MagicMock()
    mock_keycloak_adapter.validate_token = AsyncMock(
        return_value={
            "sub": TEST_CONSTANTS["test_user_id"],
            "iss": TEST_CONSTANTS["test_server"],
            "sellers": TEST_CONSTANTS["test_sellers"],
        }
    )
    container.keycloak_adapter.override(providers.Object(mock_keycloak_adapter))

    container.wire(modules=[seller_router, user_router])

    fake_user = UserAuthInfo(
        user=UserModel(name=TEST_CONSTANTS["test_user_id"], server=TEST_CONSTANTS["test_server"]),
        trace_id=TEST_CONSTANTS["test_trace_id"],
        sellers=["1", "2", "3"],
        info_token={}
    )

    def mock_do_auth_with_state(request: Request) -> UserAuthInfo:
        request.state.user = fake_user
        return fake_user

    app.dependency_overrides[do_auth] = mock_do_auth_with_state

    app.include_router(seller_router.router, prefix="/seller/v1/sellers")
    app.include_router(user_router.router, prefix="/seller/v1")

    return TestClient(app)
