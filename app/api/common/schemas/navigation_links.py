from pydantic import BaseModel, ConfigDict, Field


class NavigationLinks(BaseModel):
    previous: str = Field(..., description="Link para página anterior", examples=["?_offset=0&_limit=10"])

    current: str = Field(
        ...,
        alias="self",
        description="Link para página atual",
        examples=["?_offset=10&_limit=10"],
    )

    next: str | None = Field(..., description="Link para próxima página", examples=["?_offset=20&_limit=10"])

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def build(
        cls,
        request_path: str | None,
        offset: int,
        limit: int,
        has_next: bool = False,
        filters: str | None = None,
        sorting: str | None = None,
    ):
        filters = f"&{filters}" if filters else ""
        sorting = f"&_sort={sorting}" if sorting else ""
        query_params = f"{filters}{sorting}"
        request_path = request_path or ""
        prev_offset = offset - limit if offset - limit >= 0 else 0
        return cls(
            previous=(f"{request_path}?_offset={prev_offset}&_limit={limit}{query_params}"),
            next=(f"{request_path}?_offset={offset + limit}&_limit={limit}{query_params}" if has_next else None),
            current=f"{request_path}?_offset={offset}&_limit={limit}{query_params}",
        )


__all__ = [
    "NavigationLinks",
]
