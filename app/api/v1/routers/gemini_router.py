import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, Depends

from app.api.v1.schemas.gemini_schema import ChatRequest, ChatResponse
from app.common.datetime import utcnow
from app.services import GeminiService

router = APIRouter(prefix="/gemini", tags=["Gemini"])

logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
@inject
async def chat(
    request: ChatRequest,
    gemini_service: GeminiService = Depends(Provide["gemini_service"])
):
    """Endpoint principal para chat com o Gemini."""
    try:
        response_text = gemini_service.chat(request.text)
        return ChatResponse(
            response=response_text,
            timestamp=utcnow()
        )
    except Exception as e:
        logger.error(f"Erro ao processar chat: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao processar chat: {str(e)}"
        )

