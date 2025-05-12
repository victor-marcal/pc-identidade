from pydantic import BaseModel, Field, validator
from app.api.common.schemas import ResponseEntity, SchemaType


class SellerBase(SchemaType):
    seller_id: str
    nome_fantasia: str
    cnpj: str

class SellerCreate(SellerBase):
    pass

class SellerUpdate(SchemaType):
    nome_fantasia: str
    cnpj: str

class SellerResponse(SellerBase, ResponseEntity):
    pass
