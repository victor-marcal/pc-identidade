from dependency_injector import containers, providers

from app.clients.keycloak_admin_client import KeycloakAdminClient
from app.integrations.auth.keycloak_adapter import KeycloakAdapter
from app.integrations.database.mongo_client import MongoClient
from app.repositories import SellerRepository
from app.services import HealthCheckService, SellerService, UserService
from app.settings.app import AppSettings
from app.settings.app import settings as settings_instance


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.from_pydantic(settings_instance)
    settings = providers.Singleton(AppSettings.model_validate, config)

    mongo_client = providers.Singleton(
        MongoClient,
        mongo_url=config.app_db_url_mongo,
    )

    seller_repository = providers.Singleton(
        SellerRepository,
        client=mongo_client,
        db_name=config.MONGO_DB,
    )

    keycloak_admin_client = providers.Singleton(
        KeycloakAdminClient,
    )

    keycloak_adapter = providers.Singleton(
        KeycloakAdapter,
        well_known_url=config.KEYCLOAK_WELL_KNOWN_URL,
    )

    # Serviços
    health_check_service = providers.Singleton(
        HealthCheckService, checkers=config.health_check_checkers, settings=settings
    )

    seller_service = providers.Singleton(
        SellerService,
        repository=seller_repository,
        keycloak_client=keycloak_admin_client,
    )

    user_service = providers.Singleton(
        UserService,
        keycloak_client=keycloak_admin_client,
    )
