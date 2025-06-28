from typing import TYPE_CHECKING

from fastapi import HTTPException

from app.api.common.schemas.response import ErrorResponse
from app.common.error_codes import ErrorInfo

if TYPE_CHECKING:
    from app.api.common.schemas.response import ErrorDetail


class ApplicationException(HTTPException):
    def __init__(self, error_info: ErrorInfo, details: list["ErrorDetail"] | None = None, message: str | None = None):
        self.slug = error_info.slug
        self.message = message or error_info.message
        self.details = details
        # Call parent constructor properly
        super().__init__(status_code=error_info.http_code, detail=self.message, headers=None)

    @property
    def error_response(self):
        return ErrorResponse(slug=self.slug, message=self.message, details=self.details)
