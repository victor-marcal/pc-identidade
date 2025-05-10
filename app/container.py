from dependency_injector import containers, providers

from app.repositories import SomethingRepository
from app.services import HealthCheckService, SomethingService
from app.settings import AppSettings


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings = providers.Singleton(AppSettings)

    # Repositórios
    something_repository = providers.Singleton(SomethingRepository)

    # Serviços
    health_check_service = providers.Singleton(
        HealthCheckService, checkers=config.health_check_checkers, settings=settings
    )

    something_service = providers.Singleton(SomethingService, repository=something_repository)
