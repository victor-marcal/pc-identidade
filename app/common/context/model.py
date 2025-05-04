from enum import StrEnum

from pydantic import BaseModel


class AppContextScope(StrEnum):
    CHANNEL = "channel"
    SELLER = "seller"


class AppContext(BaseModel):
    tenant: str | None = None
    azp: str | None = None
    sub: str | None = None
    trace_id: str | None = None
    scope: AppContextScope | None = None
