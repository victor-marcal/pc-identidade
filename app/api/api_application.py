from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app.settings import ApiSettings

from .common.error_handlers import add_error_handlers
from .common.routers.health_check_routers import add_health_check_router
from .middlewares.configure_middlewares import configure_middlewares


def create_app(settings: ApiSettings, router: APIRouter) -> FastAPI:
    @asynccontextmanager
    async def _lifespan(_app: FastAPI):
        yield

        ...

    app = FastAPI(
        lifespan=_lifespan,
        title=settings.app_name,
        openapi_url=settings.openapi_path,
        version=settings.version,
        docs_url="/api/docs",
    )
    app.openapi_version = "3.0.2"

    configure_middlewares(app, settings)

    add_error_handlers(app)

    app.include_router(router)
    add_health_check_router(app, prefix=settings.health_check_base_path)

    return app
