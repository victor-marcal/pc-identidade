import pika
import json
import os
from typing import Dict

class RabbitMQPublisher:
    def __init__(self) -> None:
        self.__host = os.getenv("RABBITMQ_HOST")
        self.__port = os.getenv("RABBITMQ_PORT")
        self.__username = os.getenv("RABBITMQ_USERNAME")
        self.__password = os.getenv("RABBITMQ_PASSWORD")
        self.__exchange = os.getenv("RABBITMQ_EXCHANGE")
        self.__routing_key = os.getenv("RABBITMQ_ROUTING_KEY")

    def __create_channel(self):
        connection_parameters = pika.ConnectionParameters(
            host=self.__host,
            port=self.__port,
            credentials=pika.PlainCredentials(
                username=self.__username, 
                password=self.__password
            )
        )

        connection = pika.BlockingConnection(connection_parameters)
        channel = connection.channel()
        return connection, channel

    def send_message(self, body: Dict):
        connection = None
        try:
            connection, channel = self.__create_channel()
            
            # Serializar com cuidado especial para tipos datetime e enum
            message_body = json.dumps(body, default=self._json_serializer, ensure_ascii=False, indent=None)
            
            channel.basic_publish(
                exchange=self.__exchange,
                routing_key=self.__routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem: {str(e)}")
            raise
        finally:
            if connection and not connection.is_closed:
                connection.close()

    def _json_serializer(self, obj):
        """Serializer customizado para tipos especiais"""
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif hasattr(obj, 'value'):
            return obj.value
        elif hasattr(obj, '__dict__'): 
            return obj.__dict__
        return str(obj)


def publish_seller_message(seller_data: Dict):
    """
    Função para publicar mensagem do seller no RabbitMQ
    """
    publisher = RabbitMQPublisher()
    publisher.send_message(seller_data)
