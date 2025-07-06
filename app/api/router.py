from fastapi import APIRouter

from app.api.v1.routers.seller_router import router as seller_router
from app.api.v1.routers.user_router import router as user_router
from app.api.v1.routers.gemini_router import router as gemini_router


routes = APIRouter()

v1_router = APIRouter(prefix="/seller/v1")

v1_router.include_router(seller_router, prefix="/sellers")
v1_router.include_router(user_router)
v1_router.include_router(gemini_router, prefix="/gemini")

routes.include_router(v1_router)
