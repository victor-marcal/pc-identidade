from pydantic import BaseModel, Field, validator
from app.api.common.schemas import ResponseEntity, SchemaType


class SellerBase(SchemaType):
    seller_id: str
    nome_fantasia: str
    cnpj: str

    @validator("cnpj")
    def validate_cnpj(cls, value):
        if not value.isdigit() or len(value) != 14:
            raise ValueError("O CNPJ é inválido. Deve conter exatamente 14 dígitos numéricos.")
        return value

class SellerCreate(SellerBase):
    pass

class SellerUpdate(SchemaType):
    nome_fantasia: str
    cnpj: str

    @validator("cnpj")
    def validate_cnpj(cls, value):
        if not value.isdigit() or len(value) != 14:
            raise ValueError("O CNPJ é inválido. Deve conter exatamente 14 dígitos numéricos.")
        return value

class SellerResponse(SellerBase, ResponseEntity):
    pass
