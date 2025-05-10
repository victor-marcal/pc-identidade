from fastapi import APIRouter

from app.api.v1 import router_selller as v1_router_seller

routes = APIRouter()

routes.include_router(v1_router_seller)
