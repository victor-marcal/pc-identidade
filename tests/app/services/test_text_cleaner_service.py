import pytest
from app.services.text_cleaner_service import TextCleanerService


PLAIN_TEXT = "Just plain text"

class TestTextCleanerService:
    """Testes para o serviço de limpeza de texto"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.service = TextCleanerService()
    
    def test_init(self):
        """Testa inicialização do serviço"""
        service = TextCleanerService()
        assert hasattr(service, '_html_pattern')
        assert hasattr(service, '_ansi_pattern')
        assert hasattr(service, '_markdown_patterns')
    
    def test_remove_html_basic(self):
        """Testa remoção básica de HTML"""
        html_text = "<p>Hello <b>world</b>!</p>"
        result = self.service.remove_html(html_text)
        assert result == "Hello world!"
    
    def test_remove_html_complex(self):
        """Testa remoção de HTML complexo"""
        html_text = '<div class="test"><h1>Title</h1><p>Text with <a href="#">link</a></p></div>'
        result = self.service.remove_html(html_text)
        assert result == "TitleText with link"
    
    def test_remove_html_with_ansi(self):
        """Testa remoção de HTML com códigos ANSI"""
        text_with_ansi = "<p>Hello \x1b[31mred\x1b[0m world</p>"
        result = self.service.remove_html(text_with_ansi)
        assert result == "Hello red world"
    
    def test_remove_html_empty_string(self):
        """Testa remoção de HTML com string vazia"""
        result = self.service.remove_html("")
        assert result == ""
    
    def test_remove_html_no_tags(self):
        """Testa texto sem tags HTML"""
        plain_text = PLAIN_TEXT
        result = self.service.remove_html(plain_text)
        assert result == plain_text
    
    def test_remove_markdown_bold(self):
        """Testa remoção de markdown bold"""
        markdown_text = "This is **bold** text"
        result = self.service.remove_markdown(markdown_text)
        assert result == "This is bold text"
    
    def test_remove_markdown_italic(self):
        """Testa remoção de markdown italic"""
        markdown_text = "This is *italic* text"
        result = self.service.remove_markdown(markdown_text)
        assert result == "This is italic text"
    
    def test_remove_markdown_links(self):
        """Testa remoção de links markdown"""
        markdown_text = "Check [this link](https://example.com) out"
        result = self.service.remove_markdown(markdown_text)
        assert result == "Check this link out"
    
    def test_remove_markdown_complex(self):
        """Testa remoção de markdown complexo"""
        markdown_text = "**Bold** and *italic* with [link](http://test.com)"
        result = self.service.remove_markdown(markdown_text)
        assert result == "Bold and italic with link"
    
    def test_remove_markdown_empty_string(self):
        """Testa remoção de markdown com string vazia"""
        result = self.service.remove_markdown("")
        assert result == ""
    
    def test_remove_markdown_no_formatting(self):
        """Testa texto sem formatação markdown"""
        plain_text = PLAIN_TEXT
        result = self.service.remove_markdown(plain_text)
        assert result == plain_text
    
    def test_clean_text_html_and_markdown(self):
        """Testa limpeza completa com HTML e Markdown"""
        mixed_text = "<p>**Bold** text with <em>*italic*</em> and [link](http://test.com)</p>"
        result = self.service.clean_text(mixed_text)
        assert result == "Bold text with italic and link"
    
    def test_clean_text_with_ansi_codes(self):
        """Testa limpeza com códigos ANSI"""
        text_with_ansi = "\x1b[31m**Red bold**\x1b[0m text"
        result = self.service.clean_text(text_with_ansi)
        assert result == "Red bold text"
    
    def test_clean_text_empty_string(self):
        """Testa limpeza com string vazia"""
        result = self.service.clean_text("")
        assert result == ""
    
    def test_clean_text_plain_text(self):
        """Testa limpeza com texto simples"""
        plain_text = PLAIN_TEXT
        result = self.service.clean_text(plain_text)
        assert result == plain_text
    
    def test_clean_text_complex_scenario(self):
        """Testa cenário complexo com múltiplas formatações"""
        complex_text = '<div>\x1b[32m**Green bold**\x1b[0m with <strong>*nested*</strong> [formatting](link)</div>'
        result = self.service.clean_text(complex_text)
        assert result == "Green bold with nested formatting"
    
    def test_markdown_patterns_initialization(self):
        """Testa se os padrões markdown foram inicializados corretamente"""
        patterns = self.service._markdown_patterns
        assert len(patterns) == 3  # Bold, italic, links
        
        # Verifica se todos os padrões são tuplas com regex e replacement
        for pattern, replacement in patterns:
            assert hasattr(pattern, 'sub')  # É um objeto regex
            assert isinstance(replacement, str)
    
    def test_ansi_pattern_removal(self):
        """Testa especificamente a remoção de códigos ANSI"""
        ansi_text = "\x1b[31mRed\x1b[0m \x1b[32mGreen\x1b[0m \x1b[34mBlue\x1b[0m"
        result = self.service.remove_html(ansi_text)  # remove_html também remove ANSI
        assert result == "Red Green Blue"
