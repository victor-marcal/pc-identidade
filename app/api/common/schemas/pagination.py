from typing import Sequence
from urllib.parse import urlencode

from fastapi import Query
from pydantic import BaseModel, Field
from starlette.requests import Request

from app.settings import api_settings

from .navigation_links import NavigationLinks
from .response import ListResponse, PageResponse, get_list_response

PAGE_DEFAULT_LIMIT = api_settings.pagination.default_limit
PAGE_MAX_LIMIT = api_settings.pagination.max_limit


class Paginator(BaseModel):
    request_path: str = Field(...)
    limit: int = Field(
        default=PAGE_DEFAULT_LIMIT,
        ge=1,
        le=PAGE_MAX_LIMIT,
    )
    offset: int = Field(default=0, ge=0)
    sort: str | None = None

    def get_sort_order(self) -> dict[str, int] | None:
        if not self.sort:
            return None

        sort_values = list(filter(None, self.sort.split(",")))
        sort_data = {}
        for field in sort_values:
            parts = field.split(":")
            field_key = parts[0]
            order = -1 if len(parts) == 2 and parts[1] == "desc" else 1
            sort_data[field_key] = order
        return sort_data

    def paginate(
        self,
        results: Sequence[BaseModel] | None = None,
        filters: dict | None = None,
    ) -> ListResponse:
        count = len(results) if results else 0
        results = results if results else []
        has_next = count >= self.limit
        filters_str = (
            urlencode(
                {
                    attr: value
                    for attr, value in filters.items()
                    if attr not in ("limit", "offset") and value is not None
                }
            )
            if filters
            else ""
        )

        return get_list_response(
            results=results,
            page=PageResponse(
                limit=self.limit,
                offset=self.offset,
                count=count,
            ),
            links=NavigationLinks.build(
                request_path=self.request_path,
                offset=self.offset,
                limit=self.limit,
                has_next=has_next,
                filters=filters_str,
                sorting=self.sort,
            ),
        )


def get_request_pagination(
    request: Request,
    limit: int | None = Query(
        default=50,
        ge=1,
        le=PAGE_MAX_LIMIT,
        description="Determina a quantidade de registros a serem retornados.",
        alias="_limit"
    ),
    offset: int | None = Query(
        default=0,
        ge=0,
        le=PAGE_MAX_LIMIT,
        description=("Posição do registro de referência, a partir dele serão retornados os próximos N registros."),
        alias="_offset"
    ),
    sort: str | None = Query(
        default=None,
        description=(
            "Ordena pelo(s) campo(s). Use o sufixo :asc e :desc para ordenação"
            " ascendente e descendente, respectivamente."
            " Ex: name:asc,email:desc."
        ),
        alias="_sort"
    ),
):
    return Paginator(request_path=request.url.path, limit=limit, offset=offset, sort=sort)
