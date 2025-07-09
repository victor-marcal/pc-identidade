import pytest
from datetime import datetime
from app.models.gemini_model import ChatMessage


class TestChatMessage:
    """Testes para o modelo ChatMessage"""
    
    def test_chat_message_creation_required_fields(self):
        """Testa criação com campos obrigatórios"""
        message = ChatMessage(
            message_type="user",
            content="Hello, world!"
        )
        
        assert message.message_type == "user"
        assert message.content == "Hello, world!"
        assert isinstance(message.timestamp, datetime)
    
    def test_chat_message_creation_with_timestamp(self):
        """Testa criação com timestamp personalizado"""
        custom_timestamp = datetime(2024, 1, 1, 12, 0, 0)
        message = ChatMessage(
            message_type="assistant",
            content="Response message",
            timestamp=custom_timestamp
        )
        
        assert message.message_type == "assistant"
        assert message.content == "Response message"
        assert message.timestamp == custom_timestamp
    
    def test_chat_message_types(self):
        """Testa diferentes tipos de mensagem"""
        user_message = ChatMessage(message_type="user", content="User question")
        assistant_message = ChatMessage(message_type="assistant", content="Assistant response")
        
        assert user_message.message_type == "user"
        assert assistant_message.message_type == "assistant"
    
    def test_chat_message_inheritance(self):
        """Testa herança de PersistableEntity"""
        message = ChatMessage(message_type="user", content="Test")
        
        # Deve ter os campos herdados de PersistableEntity
        assert hasattr(message, 'created_at')
        assert hasattr(message, 'updated_at')
        assert hasattr(message, 'created_by')
        assert hasattr(message, 'updated_by')
    
    def test_chat_message_field_descriptions(self):
        """Testa se os campos têm descrições corretas"""
        # Verifica que os fields têm as descrições esperadas
        field_info = ChatMessage.model_fields
        assert field_info['message_type'].description == "Tipo da mensagem: 'user' ou 'assistant'"
        assert field_info['content'].description == "Conteúdo da mensagem"
        assert field_info['timestamp'].description == "Timestamp da mensagem"
    
    def test_chat_message_json_serialization(self):
        """Testa serialização JSON"""
        message = ChatMessage(message_type="user", content="Test message")
        
        # Deve serializar para dict
        message_dict = message.model_dump()
        assert message_dict['message_type'] == "user"
        assert message_dict['content'] == "Test message"
        assert 'timestamp' in message_dict
    
    def test_chat_message_from_dict(self):
        """Testa criação a partir de dict"""
        timestamp = datetime.now()
        data = {
            "message_type": "assistant",
            "content": "Hello from dict",
            "timestamp": timestamp
        }
        
        message = ChatMessage(**data)
        assert message.message_type == "assistant"
        assert message.content == "Hello from dict"
        assert message.timestamp == timestamp
