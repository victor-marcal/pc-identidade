from app.api.common.schemas import ResponseEntity, SchemaType


class SomethingSchema(SchemaType):
    identity: int
    name: str
    value: int


class SomethingResponse(SomethingSchema, ResponseEntity):
    """Resposta adicionando"""


class SomethingCreate(SomethingSchema):
    """Schema para criação Somethings"""


class SomethingUpdate(SchemaType):
    """Permite apenas a atualização do nome e do valor"""

    name: str
    value: int
