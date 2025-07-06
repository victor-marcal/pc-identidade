import logging
import os
import re
from typing import Optional

from fastapi import HTTPException

from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class GeminiChatHandler:
    def __init__(self, api_key: str, pdfs_folder_path: str = "pdfs"):
        self.api_key = api_key
        self.pdfs_folder_path = pdfs_folder_path
        self._service: Optional[GeminiService] = None
        
        # Padrões regex compilados para performance
        self._html_pattern = re.compile(r"<[^>]*>")
        self._ansi_pattern = re.compile(r"\x1b\[[0-9;]*m")
        self._markdown_patterns = [
            (re.compile(r"\*\*([^*]+)\*\*"), r"\1"),  # Bold
            (re.compile(r"\*([^*]+)\*"), r"\1"),      # Italic
            (re.compile(r"\[([^\]]*)\]\([^\)]*\)"), r"\1"),  # Links
        ]

    @property
    def service(self) -> GeminiService:
        """Lazy loading do serviço Gemini."""
        if self._service is None:
            try:
                self._service = GeminiService(
                    api_key=self.api_key, 
                    pdfs_folder_path=self.pdfs_folder_path
                )
            except Exception as e:
                logger.error(f"Erro ao inicializar o serviço Gemini: {e}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Erro ao inicializar o serviço Gemini: {str(e)}"
                )
        return self._service

    def _clean_html(self, texto: str) -> str:
        """Remove tags HTML e códigos ANSI do texto."""
        texto = re.sub(self._html_pattern, "", texto)
        texto = re.sub(self._ansi_pattern, "", texto)
        return texto
    
    def _clean_markdown(self, texto: str) -> str:
        """Remove formatação markdown do texto."""
        for pattern, replacement in self._markdown_patterns:
            texto = re.sub(pattern, replacement, texto)
        return texto

    def generate_response(self, message: str) -> str:
        """Gera uma resposta usando o modelo Gemini e limpa a formatação."""
        try:
            response_text = self.service.generate_response(message)
            
            # Limpar HTML e Markdown da resposta
            response_text = self._clean_html(response_text)
            response_text = self._clean_markdown(response_text)
            
            return response_text
        except Exception as e:
            logger.error(f"Erro ao gerar resposta com Gemini: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Erro ao gerar resposta com Gemini: {str(e)}"
            )
