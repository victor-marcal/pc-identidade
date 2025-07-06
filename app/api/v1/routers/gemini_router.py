import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.services.gemini_chat_handler import GeminiChatHandler

router = APIRouter()

logger = logging.getLogger(__name__)


class Message(BaseModel):
    text: str


class ChatResponse(BaseModel):
    response: str


@router.post("/chat/")
@inject
async def chat(
    message: Message,
    gemini_handler: GeminiChatHandler = Depends(Provide["gemini_chat_handler"])
):
    try:
        response_text = gemini_handler.generate_response(message.text)
        return ChatResponse(response=response_text)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao gerar resposta com Gemini: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao gerar resposta com Gemini: {str(e)}"
        )

