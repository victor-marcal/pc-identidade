import pytest
from unittest.mock import MagicMock, patch, call
import json
import os
from datetime import datetime, date
from app.services.publisher import RabbitMQPublisher, publish_seller_message
from app.models.enums import BrazilianState, AccountType, ProductCategory


class TestRabbitMQPublisher:
    """Testes para o publisher RabbitMQ"""
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': 'guest',
        'RABBITMQ_PASSWORD': 'guest',
        'RABBITMQ_EXCHANGE': 'test_exchange',
        'RABBITMQ_ROUTING_KEY': 'test.routing.key'
    })
    def test_init(self):
        """Testa inicialização do publisher"""
        publisher = RabbitMQPublisher()
        
        assert publisher._RabbitMQPublisher__host == 'localhost'
        assert publisher._RabbitMQPublisher__port == '5672'
        assert publisher._RabbitMQPublisher__username == 'guest'
        assert publisher._RabbitMQPublisher__password == 'guest'
        assert publisher._RabbitMQPublisher__exchange == 'test_exchange'
        assert publisher._RabbitMQPublisher__routing_key == 'test.routing.key'
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': 'guest',
        'RABBITMQ_PASSWORD': 'guest',
        'RABBITMQ_EXCHANGE': 'test_exchange',
        'RABBITMQ_ROUTING_KEY': 'test.routing.key'
    })
    @patch('app.services.publisher.pika.BlockingConnection')
    @patch('app.services.publisher.pika.ConnectionParameters')
    @patch('app.services.publisher.pika.PlainCredentials')
    def test_create_channel(self, mock_credentials, mock_params, mock_connection):
        """Testa criação do canal"""
        mock_connection_instance = MagicMock()
        mock_channel = MagicMock()
        mock_connection_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_connection_instance
        
        publisher = RabbitMQPublisher()
        connection, channel = publisher._RabbitMQPublisher__create_channel()
        
        # Verifica se as credenciais foram criadas corretamente
        mock_credentials.assert_called_once_with(username='guest', password='guest')
        
        # Verifica se os parâmetros de conexão foram criados
        mock_params.assert_called_once()
        
        # Verifica se a conexão foi estabelecida
        mock_connection.assert_called_once()
        
        # Verifica se o canal foi criado
        mock_connection_instance.channel.assert_called_once()
        
        assert connection == mock_connection_instance
        assert channel == mock_channel
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': 'guest',
        'RABBITMQ_PASSWORD': 'guest',
        'RABBITMQ_EXCHANGE': 'test_exchange',
        'RABBITMQ_ROUTING_KEY': 'test.routing.key'
    })
    @patch('app.services.publisher.pika.BlockingConnection')
    @patch('app.services.publisher.pika.ConnectionParameters')
    @patch('app.services.publisher.pika.PlainCredentials')
    def test_send_message_success(self, mock_credentials, mock_params, mock_connection):
        """Testa envio de mensagem com sucesso"""
        mock_connection_instance = MagicMock()
        mock_channel = MagicMock()
        mock_connection_instance.channel.return_value = mock_channel
        mock_connection_instance.is_closed = False
        mock_connection.return_value = mock_connection_instance
        
        publisher = RabbitMQPublisher()
        
        message_data = {
            'seller_id': '001',
            'company_name': 'Empresa Teste',
            'created_at': datetime(2024, 1, 1, 12, 0, 0)
        }
        
        publisher.send_message(message_data)
        
        # Verifica se a mensagem foi publicada
        mock_channel.basic_publish.assert_called_once()
        
        # Verifica os argumentos da publicação
        call_args = mock_channel.basic_publish.call_args
        assert call_args[1]['exchange'] == 'test_exchange'
        assert call_args[1]['routing_key'] == 'test.routing.key'
        
        # Verifica se o JSON contém os dados corretos
        published_body = call_args[1]['body']
        parsed_data = json.loads(published_body)
        assert parsed_data['seller_id'] == '001'
        assert parsed_data['company_name'] == 'Empresa Teste'
        
        # Verifica se a conexão foi fechada
        mock_connection_instance.close.assert_called_once()
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': 'guest',
        'RABBITMQ_PASSWORD': 'guest',
        'RABBITMQ_EXCHANGE': 'test_exchange',
        'RABBITMQ_ROUTING_KEY': 'test.routing.key'
    })
    def test_json_serializer_datetime(self):
        """Testa serialização de datetime"""
        publisher = RabbitMQPublisher()
        
        test_datetime = datetime(2024, 1, 1, 12, 30, 45)
        result = publisher._json_serializer(test_datetime)
        
        assert result == test_datetime.isoformat()
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': 'guest',
        'RABBITMQ_PASSWORD': 'guest',
        'RABBITMQ_EXCHANGE': 'test_exchange',
        'RABBITMQ_ROUTING_KEY': 'test.routing.key'
    })
    def test_json_serializer_date(self):
        """Testa serialização de date"""
        publisher = RabbitMQPublisher()
        
        test_date = date(2024, 1, 1)
        result = publisher._json_serializer(test_date)
        
        assert result == test_date.isoformat()
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': 'guest',
        'RABBITMQ_PASSWORD': 'guest',
        'RABBITMQ_EXCHANGE': 'test_exchange',
        'RABBITMQ_ROUTING_KEY': 'test.routing.key'
    })
    def test_json_serializer_enum(self):
        """Testa serialização de enum"""
        publisher = RabbitMQPublisher()
        
        test_enum = BrazilianState.SP
        result = publisher._json_serializer(test_enum)
        
        assert result == test_enum.value
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': 'guest',
        'RABBITMQ_PASSWORD': 'guest',
        'RABBITMQ_EXCHANGE': 'test_exchange',
        'RABBITMQ_ROUTING_KEY': 'test.routing.key'
    })
    def test_json_serializer_object_with_dict(self):
        """Testa serialização de objeto com __dict__"""
        publisher = RabbitMQPublisher()
        
        class TestObject:
            def __init__(self):
                self.name = "test"
                # Não incluir 'value' porque o serializer verifica hasattr('value') primeiro
        
        test_obj = TestObject()
        result = publisher._json_serializer(test_obj)
        
        assert result == {'name': 'test'}
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': 'guest',
        'RABBITMQ_PASSWORD': 'guest',
        'RABBITMQ_EXCHANGE': 'test_exchange',
        'RABBITMQ_ROUTING_KEY': 'test.routing.key'
    })
    def test_json_serializer_fallback(self):
        """Testa serialização fallback para str"""
        publisher = RabbitMQPublisher()
        
        # Objeto que não tem isoformat, value nem __dict__
        test_obj = 42  # Número inteiro
        result = publisher._json_serializer(test_obj)
        
        assert result == '42'
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': 'guest',
        'RABBITMQ_PASSWORD': 'guest',
        'RABBITMQ_EXCHANGE': 'test_exchange',
        'RABBITMQ_ROUTING_KEY': 'test.routing.key'
    })
    @patch('app.services.publisher.pika.BlockingConnection')
    def test_send_message_connection_error(self, mock_connection):
        """Testa tratamento de erro de conexão"""
        mock_connection.side_effect = Exception("Falha na conexão")
        
        publisher = RabbitMQPublisher()
        
        message_data = {'test': 'data'}
        
        with pytest.raises(Exception):
            publisher.send_message(message_data)
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': 'guest',
        'RABBITMQ_PASSWORD': 'guest',
        'RABBITMQ_EXCHANGE': 'test_exchange',
        'RABBITMQ_ROUTING_KEY': 'test.routing.key'
    })
    @patch('app.services.publisher.pika.BlockingConnection')
    @patch('app.services.publisher.pika.ConnectionParameters')
    @patch('app.services.publisher.pika.PlainCredentials')
    def test_send_message_connection_already_closed(self, mock_credentials, mock_params, mock_connection):
        """Testa envio quando conexão já está fechada"""
        mock_connection_instance = MagicMock()
        mock_channel = MagicMock()
        mock_connection_instance.channel.return_value = mock_channel
        mock_connection_instance.is_closed = True  # Conexão já fechada
        mock_connection.return_value = mock_connection_instance
        
        publisher = RabbitMQPublisher()
        
        message_data = {'test': 'data'}
        publisher.send_message(message_data)
        
        # Verifica se basic_publish foi chamado mesmo com conexão fechada
        mock_channel.basic_publish.assert_called_once()
        
        # close() não deve ser chamado porque a conexão já está fechada
        mock_connection_instance.close.assert_not_called()
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': 'guest',
        'RABBITMQ_PASSWORD': 'guest',
        'RABBITMQ_EXCHANGE': 'test_exchange',
        'RABBITMQ_ROUTING_KEY': 'test.routing.key'
    })
    @patch('app.services.publisher.pika.BlockingConnection')
    @patch('app.services.publisher.pika.ConnectionParameters')
    @patch('app.services.publisher.pika.PlainCredentials')
    def test_send_message_complex_data(self, mock_credentials, mock_params, mock_connection):
        """Testa envio de mensagem com dados complexos"""
        mock_connection_instance = MagicMock()
        mock_channel = MagicMock()
        mock_connection_instance.channel.return_value = mock_channel
        mock_connection_instance.is_closed = False
        mock_connection.return_value = mock_connection_instance
        
        publisher = RabbitMQPublisher()
        
        # Dados complexos com diferentes tipos
        message_data = {
            'seller_id': '001',
            'company_name': 'Empresa Teste',
            'legal_rep_birth_date': date(1990, 1, 1),
            'created_at': datetime(2024, 1, 1, 12, 0, 0),
            'legal_rep_rg_state': BrazilianState.SP,
            'account_type': AccountType.CURRENT,
            'product_categories': [ProductCategory.AUDIO, ProductCategory.FLOWERS_GARDEN]
        }
        
        publisher.send_message(message_data)
        
        # Verifica se a mensagem foi publicada
        mock_channel.basic_publish.assert_called_once()
        
        # Verifica o conteúdo da mensagem
        call_args = mock_channel.basic_publish.call_args
        published_body = call_args[1]['body']
        parsed_data = json.loads(published_body)
        
        assert parsed_data['seller_id'] == '001'
        assert parsed_data['company_name'] == 'Empresa Teste'
        assert parsed_data['legal_rep_birth_date'] == '1990-01-01'
        assert parsed_data['created_at'] == '2024-01-01T12:00:00'
        assert parsed_data['legal_rep_rg_state'] == 'SP'
        assert parsed_data['account_type'] == 'Corrente'


class TestPublishSellerMessage:
    """Testes para a função publish_seller_message"""
    
    @patch('app.services.publisher.RabbitMQPublisher')
    def test_publish_seller_message(self, mock_publisher_class):
        """Testa a função publish_seller_message"""
        mock_publisher = MagicMock()
        mock_publisher_class.return_value = mock_publisher
        
        seller_data = {
            'seller_id': '001',
            'company_name': 'Empresa Teste'
        }
        
        publish_seller_message(seller_data)
        
        # Verifica se o publisher foi criado
        mock_publisher_class.assert_called_once()
        
        # Verifica se send_message foi chamado com os dados corretos
        mock_publisher.send_message.assert_called_once_with(seller_data)
