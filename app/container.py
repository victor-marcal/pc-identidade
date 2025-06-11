from app.integrations.database.mongo_client import MongoClient
from dependency_injector import containers, providers

from app.repositories import SellerRepository
from app.services import HealthCheckService, SellerService
from app.settings import AppSettings


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings = providers.Singleton(AppSettings)

    # Integração com o MongoDB
    mongo_client = providers.Singleton(MongoClient, config.app_db_url_mongo)
    # Repositórios
    seller_repository = providers.Singleton(SellerRepository, mongo_client)

    # Serviços
    health_check_service = providers.Singleton(
        HealthCheckService, checkers=config.health_check_checkers, settings=settings
    )

    seller_service = providers.Singleton(SellerService, seller_repository)
