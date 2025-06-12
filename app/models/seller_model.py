from uuid import UUID
from . import PersistableEntity


class Seller(PersistableEntity):
    seller_id: UUID
    nome_fantasia: str
    cnpj: str
