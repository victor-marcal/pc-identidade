from typing import Literal

from pydantic import BaseModel, Field

ErrorLocation = Literal["query", "path", "body", "header"]


class ErrorDetail(BaseModel):
    message: str = Field(..., description="Descrição do erro")
    location: ErrorLocation | None = Field(None, description="Descrição do erro")
    slug: str | None = Field(None, description="Identificação do erro")
    field: str | None = Field(None, description="Campo que gerou o erro")
    ctx: dict | None = Field(None, description="Contexto do erro")


class ErrorResponse(BaseModel):
    slug: str = Field(..., description="Identificação do erro")
    message: str = Field(..., description="Descrição do erro")
    details: None | list[ErrorDetail] = Field(..., description="Detalhes do erro")
