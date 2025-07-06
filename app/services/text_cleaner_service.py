import re
from typing import List


class TextCleanerService:
    """Serviço para limpeza e formatação de texto."""
    
    def __init__(self):
        self._html_pattern = re.compile(r"<[^>]*>")
        self._ansi_pattern = re.compile(r"\x1b\[[0-9;]*m")
        self._markdown_patterns = [
            (re.compile(r"\*\*([^*]+)\*\*"), r"\1"),  # Bold
            (re.compile(r"\*([^*]+)\*"), r"\1"),      # Italic
            (re.compile(r"\[([^\]]*)\]\([^\)]*\)"), r"\1"),  # Links
        ]
    
    def remove_html(self, texto: str) -> str:
        """Remove tags HTML e códigos ANSI do texto."""
        texto = re.sub(self._html_pattern, "", texto)
        texto = re.sub(self._ansi_pattern, "", texto)
        return texto
    
    def remove_markdown(self, texto: str) -> str:
        """Remove formatação markdown do texto."""
        for pattern, replacement in self._markdown_patterns:
            texto = re.sub(pattern, replacement, texto)
        return texto
    
    def clean_text(self, texto: str) -> str:
        """Remove tanto HTML quanto Markdown do texto."""
        texto = self.remove_html(texto)
        texto = self.remove_markdown(texto)
        return texto
