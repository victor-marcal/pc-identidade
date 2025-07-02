from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.common.error_codes import ErrorCodes
from app.common.exceptions import ApplicationException

from .schemas.response import ErrorDetail, get_error_response

import logging
import traceback
import json

VALID_LOCATIONS = {"query", "path", "body", "header"}

logger = logging.getLogger(__name__)


async def _get_request_details(request: Request) -> dict:
    """
    Helper para extrair informações úteis da requisição para os logs.
    """
    body = None
    try:
        body_bytes = await request.body()
        if body_bytes:
            body = json.loads(body_bytes)
    except json.JSONDecodeError:
        body = {"error": "Corpo da requisição não é um JSON válido."}
    except Exception:
        body = {"error": "Não foi possível ler o corpo da requisição."}

    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "body": body
    }


def extract_error_detail(error):
    ctx = error.get("ctx", {}) or {}  # Handle None ctx
    if isinstance(ctx.get("error", {}), ValueError):
        ctx["error"] = str(ctx["error"])
    raw_location = error["loc"][0] if error["loc"] else "body"
    location = raw_location if raw_location in VALID_LOCATIONS else "body"
    return ErrorDetail(
        message=error["msg"],
        location=location,
        slug=error["type"],
        field=", ".join(map(str, error["loc"][1:])) if len(error["loc"]) > 1 else "",
        ctx=ctx,
    )


def extract_error_detail_body(error):
    ctx = error.get("ctx", {})
    if isinstance(ctx.get("error", {}), ValueError):
        ctx["error"] = str(ctx["error"])
    return ErrorDetail(
        message=error["msg"],
        location="body",
        slug=error["type"],
        field=", ".join(map(str, error["loc"][1:])) if error["loc"] else "",
        ctx=ctx,
    )


def add_error_handlers(app: FastAPI):
    @app.exception_handler(ApplicationException)
    async def http_exception_handler(request: Request, exc: ApplicationException):
        """
        Captura nossas exceções de negócio (NotFound, Forbidden, etc.)
        e as formata usando a propriedade 'error_response' da exceção.
        """
        logger.warning(
            f"Falha de negócio controlada: {exc.slug}",
            extra={
                "error_message": exc.message,
                "request_info": await _get_request_details(request)
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.error_response.model_dump(exclude_none=True),
            headers=getattr(exc, 'headers', None),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """
        Captura qualquer exceção não tratada (erros 500),
        registra um log crítico e retorna uma mensagem de erro genérica.
        """
        logger.error(
            "Erro inesperado não tratado na aplicação!",
            exc_info=True,
            extra={"request_info": await _get_request_details(request)}
        )

        error_response = get_error_response(ErrorCodes.SERVER_ERROR.value)
        return JSONResponse(
            status_code=ErrorCodes.SERVER_ERROR.http_code,
            content=error_response.model_dump(exclude_none=True),
        )

    @app.exception_handler(ValidationError)
    async def request_pydantic_validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        logger.warning(
            "Falha na validação dos dados de entrada (Pydantic).",
            extra={
                "errors": exc.errors(),
                "request_info": await _get_request_details(request)
            }
        )

        errors = exc.errors()
        details = [extract_error_detail(error) for error in errors]
        response = get_error_response(ErrorCodes.UNPROCESSABLE_ENTITY.value, details=details)

        return JSONResponse(
            status_code=ErrorCodes.UNPROCESSABLE_ENTITY.http_code,
            content=response.model_dump(mode="json", exclude_none=True, exclude_unset=True),
        )
