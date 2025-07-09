import os
import sys
import logging
import time
import dotenv
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.container import Container
from app.settings import api_settings
from pclogging import LoggingBuilder

ENV = os.getenv("ENV", "production")
is_dev = ENV == "dev"

dotenv.load_dotenv(override=is_dev)

LoggingBuilder.init()

logger = logging.getLogger(__name__)

if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

if hasattr(LoggingBuilder, '_log_level'):
    logger.setLevel(LoggingBuilder._log_level)
else:
    logger.setLevel(logging.INFO)


async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    safe_path = request.url.path.replace('\n', '').replace('\r', '')
    logger.info(f"Requisição recebida: {request.method} {safe_path}")
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = f"{process_time:.2f}ms"
    logger.info(
        f"Requisição finalizada: {request.method} {safe_path} - Status: {response.status_code} - Duração: {formatted_process_time}"
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
    container.wire(modules=[
        "app.api.common.routers.health_check_routers",
        "app.api.v1.routers.seller_router",
        "app.api.v1.routers.user_router",
        "app.api.v1.routers.gemini_router",
    ])
    return app_api


app = init()