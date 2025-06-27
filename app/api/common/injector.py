from fastapi import Path


def get_seller_id_from_path(seller_id: str = Path(...)) -> str:
    """Extrai o seller_id do path da URL."""
    return seller_id
