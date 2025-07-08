import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from app.services.gemini_service import GeminiService


@pytest.fixture
def mock_api_key():
    """API key mockeada para testes."""
    return "test-api-key-12345"


@pytest.fixture
def mock_pdfs_folder():
    """Pasta de PDFs mockeada."""
    return "test_pdfs"


@pytest.fixture
def mock_gemini_service(mock_api_key, mock_pdfs_folder):
    """GeminiService mockeado com dependências."""
    with patch.object(GeminiService, '_initialize'):
        service = GeminiService(mock_api_key, mock_pdfs_folder)
        service.pdf_content = "Conteúdo de teste dos PDFs"
        service.chain = Mock()
        service.chain.invoke = Mock(return_value={"output": "Resposta de teste"})
        
        # Mock memory with proper structure
        service.memory = Mock()
        service.memory.chat_memory = Mock()
        service.memory.chat_memory.add_user_message = Mock()
        service.memory.chat_memory.add_ai_message = Mock()
        service.memory.chat_memory.clear = Mock()
        
        return service


def test_gemini_service_init_success(mock_api_key, mock_pdfs_folder):
    """Testa inicialização bem-sucedida do GeminiService."""
    with patch.object(GeminiService, '_load_pdfs_from_folder', return_value="Conteúdo PDF"), \
         patch.object(GeminiService, '_create_chain') as mock_create_chain:
        
        mock_chain = Mock()
        mock_create_chain.return_value = mock_chain
        
        service = GeminiService(mock_api_key, mock_pdfs_folder)
        
        assert service.api_key == mock_api_key
        assert service.pdfs_folder_path == mock_pdfs_folder
        assert service.pdf_content == "Conteúdo PDF"
        assert service.chain == mock_chain


def test_gemini_service_init_no_pdfs():
    """Testa inicialização quando não há PDFs."""
    with patch.object(GeminiService, '_load_pdfs_from_folder', return_value=""), \
         pytest.raises(ValueError, match="Não foi possível carregar os documentos PDF"):
        
        GeminiService("test-key", "empty_folder")


def test_load_pdfs_from_folder_success():
    """Testa carregamento bem-sucedido de PDFs."""
    with patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.glob') as mock_glob, \
         patch('fitz.open') as mock_fitz:
        
        # Mock PDF files
        mock_pdf_file = Mock()
        mock_pdf_file.name = "test.pdf"
        mock_glob.return_value = [mock_pdf_file]
        
        # Mock PyMuPDF
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = "Conteúdo da página"
        mock_doc.__iter__ = Mock(return_value=iter([mock_page]))
        mock_doc.close = Mock()
        mock_fitz.return_value.__enter__ = Mock(return_value=mock_doc)
        mock_fitz.return_value.__exit__ = Mock(return_value=None)
        
        service = GeminiService.__new__(GeminiService)
        service.pdfs_folder_path = "test_pdfs"
        
        result = service._load_pdfs_from_folder()
        
        # Verificar que contém o formato esperado
        assert "test.pdf" in result
        assert "--- Conteúdo do arquivo test.pdf ---" in result


def test_load_pdfs_folder_not_exists():
    """Testa quando a pasta de PDFs não existe."""
    with patch('pathlib.Path.exists', return_value=False):
        service = GeminiService.__new__(GeminiService)
        service.pdfs_folder_path = "nonexistent_folder"
        
        result = service._load_pdfs_from_folder()
        
        assert result == ""


def test_load_pdfs_no_pdf_files():
    """Testa quando não há arquivos PDF na pasta."""
    with patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.glob', return_value=[]):
        
        service = GeminiService.__new__(GeminiService)
        service.pdfs_folder_path = "empty_folder"
        
        result = service._load_pdfs_from_folder()
        
        assert result == ""


def test_load_pdfs_file_error():
    """Testa erro ao carregar arquivo PDF específico."""
    with patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.glob') as mock_glob, \
         patch('fitz.open', side_effect=Exception("Erro ao abrir PDF")):
        
        mock_pdf_file = Mock()
        mock_pdf_file.name = "corrupted.pdf"
        mock_glob.return_value = [mock_pdf_file]
        
        service = GeminiService.__new__(GeminiService)
        service.pdfs_folder_path = "test_pdfs"
        
        result = service._load_pdfs_from_folder()
        
        # Deve retornar string vazia se não conseguir carregar nenhum PDF
        assert result == ""


def test_create_chain():
    """Testa criação da chain."""
    with patch('app.services.gemini_service.ChatGoogleGenerativeAI') as mock_llm, \
         patch('app.services.gemini_service.ChatPromptTemplate') as mock_prompt:
        
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance
        
        mock_prompt_instance = Mock()
        # Mock the pipe operator (__or__) to return a chain
        mock_chain = Mock()
        mock_prompt_instance.__or__ = Mock(return_value=mock_chain)
        mock_prompt.from_messages.return_value = mock_prompt_instance
        
        service = GeminiService.__new__(GeminiService)
        service.api_key = "test-key"
        service.pdf_content = "Conteúdo teste"
        service.memory = Mock()
        
        chain = service._create_chain()
        
        assert chain is not None
        assert chain == mock_chain
        mock_llm.assert_called_once()
        mock_prompt_instance.__or__.assert_called_once_with(mock_llm_instance)


def test_generate_response_success(mock_gemini_service):
    """Testa geração de resposta bem-sucedida."""
    # Mock response com atributo content
    mock_response = Mock()
    mock_response.content = "Resposta do Gemini"
    mock_gemini_service.chain.invoke.return_value = mock_response
    
    result = mock_gemini_service.generate_response("Olá, como você está?")
    
    assert result == "Resposta do Gemini"
    mock_gemini_service.chain.invoke.assert_called_once()


def test_generate_response_error(mock_gemini_service):
    """Testa erro na geração de resposta."""
    mock_gemini_service.chain.invoke.side_effect = Exception("Erro na chain")
    
    result = mock_gemini_service.generate_response("Mensagem de teste")
    
    assert result == "Desculpe, ocorreu um erro ao processar sua mensagem."


def test_generate_response_no_output(mock_gemini_service):
    """Testa quando a chain não retorna output."""
    # Mock response sem content
    mock_response = Mock()
    mock_response.content = None
    mock_gemini_service.chain.invoke.return_value = mock_response
    
    result = mock_gemini_service.generate_response("Teste")
    
    assert result == "Desculpe, não consegui gerar uma resposta."
    # Verificar que não tenta adicionar mensagem vazia ao histórico
    mock_gemini_service.memory.chat_memory.add_user_message.assert_called_once_with("Teste")
    mock_gemini_service.memory.chat_memory.add_ai_message.assert_not_called()


def test_chat_method(mock_gemini_service):
    """Testa o método chat (compatibilidade com router)."""
    with patch.object(mock_gemini_service, 'generate_response', return_value="Resposta via chat") as mock_generate:
        
        result = mock_gemini_service.chat("Mensagem de teste")
        
        assert result == "Resposta via chat"
        mock_generate.assert_called_once_with("Mensagem de teste")


def test_reset_memory(mock_gemini_service):
    """Testa reset da memória."""
    # Mock do método clear corretamente
    mock_gemini_service.memory.chat_memory.clear = Mock()
    
    mock_gemini_service.reset_memory()
    
    mock_gemini_service.memory.chat_memory.clear.assert_called_once()


def test_gemini_service_with_default_pdfs_folder():
    """Testa inicialização com pasta padrão de PDFs."""
    with patch.object(GeminiService, '_initialize'):
        service = GeminiService("test-key")
        
        assert service.pdfs_folder_path == "pdfs"


def test_gemini_service_memory_configuration():
    """Testa configuração da memória."""
    with patch.object(GeminiService, '_initialize'):
        service = GeminiService("test-key")
        
        assert service.memory.k == 5
        assert service.memory.return_messages is True
        assert service.memory.memory_key == "chat_history"
        assert service.memory.output_key == "output"


@pytest.mark.parametrize("message,expected_call_count", [
    ("Primeira mensagem", 1),
    ("", 1),
    ("Mensagem com caracteres especiais: áéíóú çñü", 1),
])
def test_chat_different_inputs(mock_gemini_service, message, expected_call_count):
    """Testa chat com diferentes tipos de entrada."""
    with patch.object(mock_gemini_service, 'generate_response', return_value="Resposta") as mock_generate:
        
        result = mock_gemini_service.chat(message)
        
        assert result == "Resposta"
        assert mock_generate.call_count == expected_call_count
        mock_generate.assert_called_with(message)
