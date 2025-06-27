from app.api.router import routes as router
from app.api.api_application import create_app
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import APIRouter, FastAPI
from app.settings import ApiSettings, api_settings
from app.container import Container
from dependency_injector.wiring import providers
from fastapi.testclient import TestClient

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
        app_name="TestApp",
        openapi_path="/openapi.json",
        version="0.1.0",
        health_check_base_path="/health"
    )

@pytest.fixture
def mock_seller_service():
    return AsyncMock()


@pytest.fixture
def client(mock_seller_service):
    from app.container import Container
    from app.api.v1.routers import seller_router
    from app.api.common.auth_handler import do_auth, UserAuthInfo
    from app.models.base import UserModel
    from unittest.mock import MagicMock

    app = FastAPI()

    container = Container()
    container.seller_service.override(providers.Object(mock_seller_service))

    # Mock KeycloakAdapter para evitar conexões HTTP reais
    mock_keycloak_adapter = MagicMock()
    mock_keycloak_adapter.validate_token = AsyncMock(return_value={
        "sub": "test-user-id",
        "iss": "test-server",
        "sellers": "1,2,3"
    })
    container.keycloak_adapter.override(providers.Object(mock_keycloak_adapter))

    container.wire(modules=[seller_router])
    app.container = container

    # Override auth dependency for tests
    def mock_do_auth():
        return UserAuthInfo(
            user=UserModel(
                name="test-user-id",
                server="test-server"
            ),
            trace_id="test-trace-id",
            sellers=["1", "2", "3"]  # Mock seller permissions
        )
    
    app.dependency_overrides[do_auth] = mock_do_auth

    app.include_router(seller_router.router, prefix="/seller/v1")

    return TestClient(app)