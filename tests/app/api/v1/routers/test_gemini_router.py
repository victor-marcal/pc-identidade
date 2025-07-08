import pytest
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from dependency_injector import containers, providers

from app.api.v1.routers.gemini_router import router
from app.api.v1.schemas.gemini_schema import ChatRequest, ChatResponse


@pytest.fixture
def mock_gemini_service():
    """Mock do serviço Gemini"""
    mock = Mock()
    mock.chat = Mock(return_value="Resposta do Gemini")
    return mock


@pytest.fixture
def client(mock_gemini_service):
    """Cliente de teste com dependências mockadas"""
    from app.container import Container
    
    app = FastAPI()
    
    # Container para dependency injection
    container = Container()
    container.gemini_service.override(providers.Object(mock_gemini_service))
    
    # Wire the container to the router module
    container.wire(modules=["app.api.v1.routers.gemini_router"])
    
    app.container = container
    app.include_router(router)
    
    return TestClient(app)


def test_chat_success(client, mock_gemini_service):
    """Testa chat com sucesso."""
    mock_gemini_service.chat.return_value = "Resposta do Gemini"
    
    response = client.post("/chat", json={"text": "Olá"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Resposta do Gemini"
    assert "timestamp" in data
    mock_gemini_service.chat.assert_called_once_with("Olá")


def test_chat_service_error(client, mock_gemini_service):
    """Testa erro no serviço."""
    mock_gemini_service.chat.side_effect = Exception("Erro do serviço")
    
    response = client.post("/chat", json={"text": "Olá"})
    
    assert response.status_code == 500
    data = response.json()
    assert "Erro ao processar chat" in data["detail"]
    assert "Erro do serviço" in data["detail"]


def test_chat_invalid_input(client):
    """Testa entrada inválida."""
    response = client.post("/chat", json={})
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_chat_empty_text(client):
    """Testa chat com texto vazio - deve retornar 422."""
    response = client.post("/chat", json={"text": ""})
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_chat_long_text(client, mock_gemini_service):
    """Testa chat com texto longo."""
    long_text = "a" * 1000
    mock_gemini_service.chat.return_value = "Resposta para texto longo"
    
    response = client.post("/chat", json={"text": long_text})
    
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Resposta para texto longo"
    mock_gemini_service.chat.assert_called_once_with(long_text)


def test_chat_special_characters(client, mock_gemini_service):
    """Testa chat com caracteres especiais."""
    special_text = "Olá! Como está? 😊 #hashtag @mention"
    mock_gemini_service.chat.return_value = "Resposta especial"
    
    response = client.post("/chat", json={"text": special_text})
    
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Resposta especial"
    mock_gemini_service.chat.assert_called_once_with(special_text)


def test_chat_response_schema_validation():
    """Testa validação do schema de resposta."""
    from datetime import datetime
    
    # Teste direto do schema
    response = ChatResponse(
        response="Teste",
        timestamp=datetime.now()
    )
    
    assert response.response == "Teste"
    assert isinstance(response.timestamp, datetime)


def test_chat_request_schema_validation():
    """Testa validação do schema de requisição."""
    # Teste direto do schema
    request = ChatRequest(text="Teste")
    assert request.text == "Teste"
    
    # Teste com texto que atende ao mínimo (1 caractere)
    request_min = ChatRequest(text="a")
    assert request_min.text == "a"
    
    # Teste que texto vazio deve falhar
    with pytest.raises(Exception):  # ValidationError
        ChatRequest(text="")


# Teste para cobrir a linha 24 (linha do try)
def test_chat_with_different_exception_types(client, mock_gemini_service):
    """Testa diferentes tipos de exceções."""
    # Teste com ValueError
    mock_gemini_service.chat.side_effect = ValueError("Valor inválido")
    response = client.post("/chat", json={"text": "teste"})
    assert response.status_code == 500
    assert "Valor inválido" in response.json()["detail"]
    
    # Reset mock
    mock_gemini_service.reset_mock()
    
    # Teste com TypeError
    mock_gemini_service.chat.side_effect = TypeError("Tipo inválido")
    response = client.post("/chat", json={"text": "teste"})
    assert response.status_code == 500
    assert "Tipo inválido" in response.json()["detail"]


def test_chat_none_response(client, mock_gemini_service):
    """Testa quando o serviço retorna None."""
    mock_gemini_service.chat.return_value = None
    
    response = client.post("/chat", json={"text": "Olá"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["response"] is None
    assert "timestamp" in data