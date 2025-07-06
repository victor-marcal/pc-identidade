from datetime import datetime
from typing import Optional
from pydantic import Field

from . import PersistableEntity


class ChatMessage(PersistableEntity):
    """Modelo simplificado para mensagens do chat com Gemini."""
    
    message_type: str = Field(..., description="Tipo da mensagem: 'user' ou 'assistant'")
    content: str = Field(..., description="Conteúdo da mensagem")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da mensagem")
