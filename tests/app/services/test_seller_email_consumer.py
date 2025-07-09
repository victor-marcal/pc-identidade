import secrets
import string
import pytest
from unittest.mock import MagicMock, patch, call
import json
import os
from unittest.mock import ANY
from app.services.seller_email_consumer import SellerEmailConsumer, main

def generate_test_password(length: int = 12) -> str:
    """Gera uma senha segura para testes"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

EMPRESA_TESTE = 'Empresa Teste'
GUEST = "GUEST"

class TestSellerEmailConsumer:
    """Testes para o consumidor de email de seller"""
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': GUEST,
        'RABBITMQ_PASSWORD': GUEST,
        'RABBITMQ_QUEUE': 'test_queue'
    })
    def test_init(self):
        """Testa inicialização do consumidor"""
        consumer = SellerEmailConsumer()
        
        assert consumer._SellerEmailConsumer__host == 'localhost'
        assert consumer._SellerEmailConsumer__port == '5672'
        assert consumer._SellerEmailConsumer__username == GUEST
        assert consumer._SellerEmailConsumer__password == GUEST
        assert consumer._SellerEmailConsumer__queue == 'test_queue'
        assert consumer.logger is not None
        assert consumer.email_service is not None
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': GUEST,
        'RABBITMQ_PASSWORD': os.getenv("RABBITMQ_PASSWORD"),
        'RABBITMQ_QUEUE': 'test_queue'
    })
    @patch('app.services.seller_email_consumer.pika.BlockingConnection')
    @patch('app.services.seller_email_consumer.pika.ConnectionParameters')
    @patch('app.services.seller_email_consumer.pika.PlainCredentials')
    def test_create_channel(self, mock_credentials, mock_params, mock_connection):
        """Testa criação do canal"""
        mock_connection_instance = MagicMock()
        mock_channel = MagicMock()
        mock_connection_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_connection_instance
        
        consumer = SellerEmailConsumer()
        connection, channel = consumer._SellerEmailConsumer__create_channel()
        
        mock_credentials.assert_called_once_with(username=GUEST, password=ANY)
        
        mock_params.assert_called_once()
        
        mock_connection.assert_called_once()
        
        mock_connection_instance.channel.assert_called_once()
        mock_channel.queue_declare.assert_called_once_with(queue='test_queue', durable=True)
        mock_channel.basic_consume.assert_called_once_with(
            queue='test_queue',
            auto_ack=False,
            on_message_callback=consumer._SellerEmailConsumer__process_seller_message
        )
        
        assert connection == mock_connection_instance
        assert channel == mock_channel
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': GUEST,
        'RABBITMQ_PASSWORD': os.getenv("RABBITMQ_PASSWORD"),
        'RABBITMQ_QUEUE': 'test_queue'
    })
    def test_process_seller_message_valid(self):
        """Testa processamento de mensagem válida"""
        consumer = SellerEmailConsumer()
        consumer.email_service = MagicMock()
        consumer.email_service.send_welcome_email.return_value = True
        
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        
        seller_data = {
            'seller_id': '001',
            'company_name': EMPRESA_TESTE,
            'contact_email': 'contato6@teste.com',
            'trade_name': 'Loja Teste',
            'business_description': 'Venda de produtos',
            'product_categories': ['AUDIO']
        }
        
        body = json.dumps(seller_data).encode('utf-8')
        
        consumer._SellerEmailConsumer__process_seller_message(ch, method, properties, body)
        
        consumer.email_service.send_welcome_email.assert_called_once_with(seller_data)
        
        ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': GUEST,
        'RABBITMQ_PASSWORD': os.getenv("RABBITMQ_PASSWORD"),
        'RABBITMQ_QUEUE': 'test_queue'
    })
    def test_process_seller_message_invalid_json(self):
        """Testa processamento de mensagem com JSON inválido"""
        consumer = SellerEmailConsumer()
        consumer.email_service = MagicMock()
        
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        
        body = b'{"invalid": json}'
        
        consumer._SellerEmailConsumer__process_seller_message(ch, method, properties, body)
        
        consumer.email_service.send_welcome_email.assert_not_called()
        
        ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': GUEST,
        'RABBITMQ_PASSWORD': os.getenv("RABBITMQ_PASSWORD"),
        'RABBITMQ_QUEUE': 'test_queue'
    })
    def test_process_seller_message_invalid_data(self):
        """Testa processamento de mensagem com dados inválidos"""
        consumer = SellerEmailConsumer()
        consumer.email_service = MagicMock()
        
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        
        seller_data = {
            'seller_id': '001',
        }
        
        body = json.dumps(seller_data).encode('utf-8')
        
        consumer._SellerEmailConsumer__process_seller_message(ch, method, properties, body)
        
        consumer.email_service.send_welcome_email.assert_not_called()
        
        ch.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': GUEST,
        'RABBITMQ_PASSWORD': os.getenv("RABBITMQ_PASSWORD"),
        'RABBITMQ_QUEUE': 'test_queue'
    })
    def test_process_seller_message_email_service_error(self):
        """Testa tratamento de erro no serviço de email"""
        consumer = SellerEmailConsumer()
        consumer.email_service = MagicMock()
        consumer.email_service.send_welcome_email.side_effect = Exception("Falha no envio")
        
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        
        seller_data = {
            'seller_id': '001',
            'company_name': EMPRESA_TESTE,
            'contact_email': 'contato1@teste.com'
        }
        
        body = json.dumps(seller_data).encode('utf-8')
        
        consumer._SellerEmailConsumer__process_seller_message(ch, method, properties, body)
        
        consumer.email_service.send_welcome_email.assert_called_once_with(seller_data)
        
        ch.basic_nack.assert_called_once_with(delivery_tag=method.delivery_tag, requeue=True)
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': GUEST,
        'RABBITMQ_PASSWORD': os.getenv("RABBITMQ_PASSWORD"),
        'RABBITMQ_QUEUE': 'test_queue'
    })
    def test_process_seller_message_email_service_false(self):
        """Testa quando serviço de email retorna False"""
        consumer = SellerEmailConsumer()
        consumer.email_service = MagicMock()
        consumer.email_service.send_welcome_email.return_value = False
        
        ch = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        
        seller_data = {
            'seller_id': '001',
            'company_name': EMPRESA_TESTE,
            'contact_email': 'contato5@teste.com'
        }
        
        body = json.dumps(seller_data).encode('utf-8')
        
        consumer._SellerEmailConsumer__process_seller_message(ch, method, properties, body)
        
        consumer.email_service.send_welcome_email.assert_called_once_with(seller_data)
        
        ch.basic_nack.assert_called_once_with(delivery_tag=method.delivery_tag, requeue=True)
    
    def test_is_valid_seller_message_valid(self):
        """Testa validação de mensagem válida"""
        consumer = SellerEmailConsumer()
        
        data = {
            'seller_id': '001',
            'company_name': EMPRESA_TESTE,
            'contact_email': 'contato4@teste.com'
        }
        
        result = consumer._SellerEmailConsumer__is_valid_seller_message(data)
        assert result is True
    
    def test_is_valid_seller_message_missing_fields(self):
        """Testa validação de mensagem com campos faltando"""
        consumer = SellerEmailConsumer()
        
        data1 = {
            'company_name': EMPRESA_TESTE,
            'contact_email': 'contato2@teste.com'
        }
        
        data2 = {
            'seller_id': '001',
            'contact_email': 'contato@teste.com'
        }
        
        data3 = {
            'seller_id': '001',
            'company_name': EMPRESA_TESTE
        }
        
        assert consumer._SellerEmailConsumer__is_valid_seller_message(data1) is False
        assert consumer._SellerEmailConsumer__is_valid_seller_message(data2) is False
        assert consumer._SellerEmailConsumer__is_valid_seller_message(data3) is False
    
    def test_is_valid_seller_message_empty_fields(self):
        """Testa validação de mensagem com campos vazios"""
        consumer = SellerEmailConsumer()
        
        data = {
            'seller_id': '',
            'company_name': EMPRESA_TESTE,
            'contact_email': 'contato3@teste.com'
        }
        
        result = consumer._SellerEmailConsumer__is_valid_seller_message(data)
        assert result is False
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': GUEST,
        'RABBITMQ_PASSWORD': os.getenv("RABBITMQ_PASSWORD"),
        'RABBITMQ_QUEUE': 'test_queue'
    })
    @patch('app.services.seller_email_consumer.pika.BlockingConnection')
    def test_start_consuming_success(self, mock_connection):
        """Testa início do consumo com sucesso"""
        mock_connection_instance = MagicMock()
        mock_channel = MagicMock()
        mock_connection_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_connection_instance
        
        consumer = SellerEmailConsumer()
        
        mock_channel.start_consuming.side_effect = KeyboardInterrupt("Interrompido pelo usuário")
        
        consumer.start_consuming()
        
        mock_channel.start_consuming.assert_called_once()
        
        mock_connection_instance.close.assert_called_once()
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': GUEST,
        'RABBITMQ_PASSWORD': os.getenv("RABBITMQ_PASSWORD"),
        'RABBITMQ_QUEUE': 'test_queue'
    })
    @patch('app.services.seller_email_consumer.pika.BlockingConnection')
    def test_start_consuming_connection_error(self, mock_connection):
        """Testa tratamento de erro de conexão"""
        mock_connection.side_effect = Exception("Falha na conexão")
        
        consumer = SellerEmailConsumer()
        
        with pytest.raises(Exception, match="Falha na conexão"):
            consumer.start_consuming()
        
        mock_connection.assert_called()


class TestMainFunction:
    """Testes para a função main"""
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': 'localhost',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': GUEST,
        'RABBITMQ_PASSWORD': os.getenv("RABBITMQ_PASSWORD"),
        'RABBITMQ_QUEUE': 'test_queue',
        'SMTP_SERVER': 'smtp.test.com',
        'SMTP_PORT': '587',
        'SENDER_EMAIL': 'test@company.com',
        'SENDER_PASSWORD': 'test_password'
    })
    @patch('app.services.seller_email_consumer.SellerEmailConsumer')
    def test_main_success(self, mock_consumer_class):
        """Testa função main com sucesso"""
        mock_consumer = MagicMock()
        mock_consumer_class.return_value = mock_consumer
        
        main()
        
        mock_consumer_class.assert_called_once()
        mock_consumer.start_consuming.assert_called_once()
    
    @patch.dict(os.environ, {
        'RABBITMQ_HOST': '',
        'RABBITMQ_PORT': '5672',
        'RABBITMQ_USERNAME': GUEST,
        'RABBITMQ_PASSWORD': os.getenv("RABBITMQ_PASSWORD"),
        'RABBITMQ_QUEUE': 'test_queue',
        'SMTP_SERVER': 'smtp.test.com',
        'SMTP_PORT': '587',
        'SENDER_EMAIL': 'test@company.com',
        'SENDER_PASSWORD': 'test_password'
    })
    @patch('app.services.seller_email_consumer.SellerEmailConsumer')
    def test_main_missing_env_vars(self, mock_consumer_class):
        """Testa função main com variáveis de ambiente faltando"""
        main()
        
        mock_consumer_class.assert_not_called()
    
    def test_main_missing_multiple_env_vars(self):
        """Testa função main com múltiplas variáveis faltando"""

        with patch.dict(os.environ, {}, clear=True):
            main()
