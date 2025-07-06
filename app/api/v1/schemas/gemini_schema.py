from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


# Request Schemas
class ChatRequest(BaseModel):
    """Schema para requisição de mensagem no chat."""
    text: str = Field(..., min_length=1, max_length=2000, description="Texto da mensagem")


# Response Schemas  
class ChatResponse(BaseModel):
    """Schema para resposta de mensagem do chat."""
    response: str = Field(..., description="Resposta do assistente")
    timestamp: datetime = Field(..., description="Timestamp da resposta")


class MessageItem(BaseModel):
    """Schema para item individual do histórico."""
    message_type: str = Field(..., description="Tipo: 'user' ou 'assistant'")
    content: str = Field(..., description="Conteúdo da mensagem")
    timestamp: datetime = Field(..., description="Timestamp da mensagem")


class ChatHistoryResponse(BaseModel):
    """Schema para histórico de mensagens."""
    messages: List[MessageItem] = Field(..., description="Lista de mensagens")
    total: int = Field(..., description="Total de mensagens")
