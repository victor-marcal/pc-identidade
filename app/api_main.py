import os

import dotenv
from fastapi import FastAPI, Request

from app.container import Container
from app.settings import api_settings

from starlette.middleware.base import BaseHTTPMiddleware

import logging
import time
from pclogging import LoggingBuilder

ENV = os.getenv("ENV", "production")
is_dev = ENV == "dev"

dotenv.load_dotenv(override=is_dev)

# Inicializando a biblioteca de logs
LoggingBuilder.init()

logging.basicConfig(level=LoggingBuilder._log_level)

logger = logging.getLogger(__name__)


async def log_requests_middleware(request: Request, call_next):
    """
    Este middleware registra cada requisição recebida, seu status de resposta
    e o tempo de processamento.
    """
    start_time = time.time()
    logger.info(f"Requisição recebida: {request.method} {request.url.path}")

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = f"{process_time:.2f}ms"

    logger.info(
        f"Requisição finalizada: {request.method} {request.url.path} - Status: {response.status_code} - Duração: {formatted_process_time}"
    )
    return response


def init() -> FastAPI:
    from app.api.api_application import create_app
    from app.api.router import routes as api_routes

    container = Container()

    container.config.from_pydantic(api_settings)

    app_api = create_app(api_settings, api_routes)
    app_api.container = container  # type: ignore[attr-defined]

    app_api.add_middleware(BaseHTTPMiddleware, dispatch=log_requests_middleware)

    # Autowiring
    container.wire(modules=["app.api.common.routers.health_check_routers"])
    container.wire(modules=["app.api.v1.routers.seller_router"])
    container.wire(modules=["app.api.v1.routers.user_router"])

    # Outros middlewares podem ser adicionados aqui se necessário

    return app_api


app = init()
