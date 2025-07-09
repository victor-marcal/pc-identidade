import secrets
import string
import pytest
from unittest.mock import MagicMock, patch, call
import os
from app.services.consumer import RabbitmqConsumer, minha_callback



def generate_test_password(length: int = 12) -> str:
    """Gera uma senha segura para testes"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

class TestRabbitmqConsumer:
    """Testes para o consumidor RabbitMQ"""
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': 'guest',
        'RABBITMQ_PASSWORD': generate_test_password(),
        'RABBITMQ_QUEUE': 'test_queue'
    })
    @patch('app.services.consumer.pika.BlockingConnection')
    @patch('app.services.consumer.pika.ConnectionParameters')
    @patch('app.services.consumer.pika.PlainCredentials')
    def test_init(self, mock_credentials, mock_params, mock_connection):
        """Testa inicialização do consumidor"""
        mock_callback = MagicMock()
        mock_channel = MagicMock()
        mock_connection_instance = MagicMock()
        mock_connection_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_connection_instance
        
        # Gera senha de teste
        test_password = generate_test_password()
        
        with patch.dict(os.environ, {'RABBITMQ_PASSWORD': test_password}):
            consumer = RabbitmqConsumer(mock_callback)
            
            # Verifica se as variáveis de ambiente foram lidas
            assert consumer._RabbitmqConsumer__host == 'localhost'
            assert consumer._RabbitmqConsumer__port == '5672'
            assert consumer._RabbitmqConsumer__username == 'guest'
            assert consumer._RabbitmqConsumer__password == test_password
            assert consumer._RabbitmqConsumer__queue == 'test_queue'
            assert consumer._RabbitmqConsumer__callback == mock_callback
            
            # Verifica se as credenciais foram criadas corretamente
            mock_credentials.assert_called_once_with(username='guest', password=test_password)
        
        # Verifica se os parâmetros de conexão foram criados
        mock_params.assert_called_once()
        
        # Verifica se a conexão foi estabelecida
        mock_connection.assert_called_once()
        
        # Verifica se o canal foi criado e configurado
        mock_connection_instance.channel.assert_called_once()
        mock_channel.queue_declare.assert_called_once_with(queue='test_queue', durable=True)
        mock_channel.basic_consume.assert_called_once_with(
            queue='test_queue',
            auto_ack=True,
            on_message_callback=mock_callback
        )
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'test-host',
        'RABBITMQ_PORT': '5673',
        'RABBITMQ_USERNAME': 'test-user',
        'RABBITMQ_PASSWORD': generate_test_password(),
        'RABBITMQ_QUEUE': 'test-queue'
    })
    @patch('app.services.consumer.pika.BlockingConnection')
    @patch('app.services.consumer.pika.ConnectionParameters')
    @patch('app.services.consumer.pika.PlainCredentials')
    def test_create_channel(self, mock_credentials, mock_params, mock_connection):
        """Testa criação do canal"""
        mock_callback = MagicMock()
        mock_channel = MagicMock()
        mock_connection_instance = MagicMock()
        mock_connection_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_connection_instance
        mock_credentials_instance = MagicMock()
        mock_credentials.return_value = mock_credentials_instance
        mock_params_instance = MagicMock()
        mock_params.return_value = mock_params_instance
        
        # Gera senha de teste para usar na verificação
        test_password = generate_test_password()
        
        # Patch temporário para usar a mesma senha
        with patch.dict(os.environ, {'RABBITMQ_PASSWORD': test_password}):
            consumer = RabbitmqConsumer(mock_callback)
            
            # Verifica se as credenciais foram criadas com os valores corretos
            mock_credentials.assert_called_once_with(username='test-user', password=test_password)
        
        # Verifica se os parâmetros foram criados com os valores corretos
        mock_params.assert_called_once_with(
            host='test-host',
            port='5673',
            credentials=mock_credentials_instance
        )
        
        # Verifica se a conexão foi criada
        mock_connection.assert_called_once_with(mock_params_instance)
        
        # Verifica se o canal foi configurado corretamente
        mock_channel.queue_declare.assert_called_once_with(queue='test-queue', durable=True)
        mock_channel.basic_consume.assert_called_once_with(
            queue='test-queue',
            auto_ack=True,
            on_message_callback=mock_callback
        )
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': 'guest',
        'RABBITMQ_PASSWORD': generate_test_password(),
        'RABBITMQ_QUEUE': 'test_queue'
    })
    @patch('app.services.consumer.pika.BlockingConnection')
    @patch('app.services.consumer.pika.ConnectionParameters')
    @patch('app.services.consumer.pika.PlainCredentials')
    def test_start(self, mock_credentials, mock_params, mock_connection):
        """Testa início do consumo"""
        mock_callback = MagicMock()
        mock_channel = MagicMock()
        mock_connection_instance = MagicMock()
        mock_connection_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_connection_instance
        
        consumer = RabbitmqConsumer(mock_callback)
        consumer.start()
        
        # Verifica se start_consuming foi chamado
        mock_channel.start_consuming.assert_called_once()
    
    def test_minha_callback(self, capsys):
        """Testa a função callback de exemplo"""
        # Simula parâmetros da callback do RabbitMQ
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        body = b"Test message"
        
        minha_callback(ch, method, properties, body)
        
        # Verifica se a mensagem foi impressa
        captured = capsys.readouterr()
        assert "b'Test message'" in captured.out
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': '',
        'RABBITMQ_PORT': '',
        'RABBITMQ_USERNAME': '',
        'RABBITMQ_PASSWORD': '',
        'RABBITMQ_QUEUE': ''
    })
    @patch('app.services.consumer.pika.BlockingConnection')
    @patch('app.services.consumer.pika.ConnectionParameters')
    @patch('app.services.consumer.pika.PlainCredentials')
    def test_init_with_empty_env_vars(self, mock_credentials, mock_params, mock_connection):
        """Testa inicialização com variáveis de ambiente vazias"""
        mock_callback = MagicMock()
        mock_channel = MagicMock()
        mock_connection_instance = MagicMock()
        mock_connection_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_connection_instance
        
        consumer = RabbitmqConsumer(mock_callback)
        
        # Verifica se as variáveis vazias foram lidas
        assert consumer._RabbitmqConsumer__host == ''
        assert consumer._RabbitmqConsumer__port == ''
        assert consumer._RabbitmqConsumer__username == ''
        assert consumer._RabbitmqConsumer__password == ''
        assert consumer._RabbitmqConsumer__queue == ''
    
    @patch('app.services.consumer.RabbitmqConsumer')
    def test_main_execution_block(self, mock_consumer_class):
        """Testa se o bloco principal funciona"""
        mock_consumer_instance = MagicMock()
        mock_consumer_class.return_value = mock_consumer_instance
        
        # Simula a execução do código principal
        # (Como está no nível do módulo, precisa ser testado de forma diferente)
        from app.services import consumer
        
        # Verifica se a classe existe e pode ser instanciada
        assert hasattr(consumer, 'RabbitmqConsumer')
        assert hasattr(consumer, 'minha_callback')
        assert callable(consumer.RabbitmqConsumer)
        assert callable(consumer.minha_callback)
    
    def test_callback_with_different_message_types(self, capsys):
        """Testa callback com diferentes tipos de mensagem"""
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        
        # Testa com string
        body_str = b"String message"
        minha_callback(ch, method, properties, body_str)
        
        # Testa com JSON
        body_json = b'{"key": "value"}'
        minha_callback(ch, method, properties, body_json)
        
        captured = capsys.readouterr()
        assert "b'String message'" in captured.out
        assert 'b\'{"key": "value"}\'' in captured.out
