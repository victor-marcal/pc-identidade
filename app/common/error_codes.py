from dataclasses import dataclass
from enum import Enum
from http import HTTPStatus


@dataclass(frozen=True)
class ErrorInfo:
    __slots__ = ("slug", "message", "http_code")
    slug: str
    message: str
    http_code: int


class ErrorCodes(Enum):
    # fmt: off
    # ============================================================
    # Erros HTTP
    # ============================================================
    BAD_REQUEST = ErrorInfo("BAD_REQUEST", "Bad Request", HTTPStatus.BAD_REQUEST)
    UNAUTHORIZED = ErrorInfo("UNAUTHORIZED", "Unauthorized", HTTPStatus.UNAUTHORIZED)
    FORBIDDEN = ErrorInfo("FORBIDDEN", "Forbidden", HTTPStatus.FORBIDDEN)
    NOT_FOUND = ErrorInfo("NOT_FOUND", "Not found", HTTPStatus.NOT_FOUND)
    CONFLICT = ErrorInfo("CONFLICT", "Conflict", HTTPStatus.CONFLICT)
    UNPROCESSABLE_ENTITY = ErrorInfo("UNPROCESSABLE_ENTITY", "Unprocessable Entity", HTTPStatus.UNPROCESSABLE_ENTITY)
    SERVER_ERROR = ErrorInfo("INTERNAL_SERVER_ERROR", "Internal Server Error", HTTPStatus.INTERNAL_SERVER_ERROR)

    # ============================================================
    # Erros Aplicação
    # ============================================================
    OPERATION_DENIED = ErrorInfo("OPERATION_DENIED", "Operação não permitida", HTTPStatus.BAD_REQUEST)

    # fmt: on

    @property
    def slug(self):
        return self.value.slug

    @property
    def message(self):
        return self.value.message

    @property
    def http_code(self):
        return self.value.http_code
