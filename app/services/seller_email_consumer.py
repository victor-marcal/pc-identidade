import pika
import json
import os
import logging
from app.services.email_service import EmailService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SellerEmailConsumer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.__host = os.getenv("RABBITMQ_HOST")
        self.__port = os.getenv("RABBITMQ_PORT")
        self.__username = os.getenv("RABBITMQ_USERNAME")
        self.__password = os.getenv("RABBITMQ_PASSWORD")
        self.__queue = os.getenv("RABBITMQ_QUEUE")
        self.email_service = EmailService()

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
        
        # Declarar a fila
        channel.queue_declare(
            queue=self.__queue,
            durable=True
        )
        
        # Configurar consumer
        channel.basic_consume(
            queue=self.__queue,
            auto_ack=False,  # Mudado para False para controle manual
            on_message_callback=self.__process_seller_message
        )

        return connection, channel

    def __process_seller_message(self, ch, method, properties, body):
        """
        Processa mensagem recebida do RabbitMQ e envia email de boas-vindas
        """
        try:
            # Decodificar mensagem JSON
            message_str = body.decode('utf-8')
            self.logger.info(f"Mensagem recebida: {message_str}")
            
            seller_data = json.loads(message_str)
            
            # Verificar se é uma mensagem de seller válida
            if not self.__is_valid_seller_message(seller_data):
                self.logger.warning("Mensagem recebida não contém dados válidos de seller")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # Enviar email de boas-vindas
            self.logger.info(f"Enviando email de boas-vindas para {seller_data.get('company_name', 'N/A')}")
            
            success = self.email_service.send_welcome_email(seller_data)
            
            if success:
                self.logger.info(f"Email enviado com sucesso para {seller_data.get('contact_email', 'N/A')}")
                # Confirmar processamento da mensagem
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                self.logger.error("Falha ao enviar email. Rejeitando mensagem.")
                # Rejeitar mensagem (volta para a fila)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON: {str(e)}")
            ch.basic_ack(delivery_tag=method.delivery_tag)  # Descartar mensagem inválida
            
        except Exception as e:
            self.logger.error(f"Erro inesperado ao processar mensagem: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def __is_valid_seller_message(self, data):
        """
        Verifica se a mensagem contém dados válidos de seller
        """
        required_fields = ['seller_id', 'company_name', 'contact_email']
        return all(field in data and data[field] for field in required_fields)

    def start_consuming(self):
        """
        Inicia o consumo de mensagens
        """
        try:
            self.logger.info("Iniciando consumer de email para sellers...")
            self.logger.info(f"Conectando em {self.__host}:{self.__port}")
            self.logger.info(f"Fila: {self.__queue}")
            
            connection, channel = self.__create_channel()
            
            self.logger.info("Aguardando mensagens. Para sair, pressione CTRL+C")
            channel.start_consuming()
            
        except KeyboardInterrupt:
            self.logger.info("Interrompido pelo usuário")
            channel.stop_consuming()
            connection.close()
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar consumer: {str(e)}")
            raise


def main():
    """
    Função principal para executar o consumer
    """
    # Verificar variáveis de ambiente necessárias
    required_env_vars = [
        'RABBITMQ_HOST', 'RABBITMQ_PORT', 'RABBITMQ_USERNAME', 
        'RABBITMQ_PASSWORD', 'RABBITMQ_QUEUE',
        'SMTP_SERVER', 'SMTP_PORT', 'SENDER_EMAIL', 'SENDER_PASSWORD'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Variáveis de ambiente faltando: {', '.join(missing_vars)}")
        return

    # Iniciar consumer
    consumer = SellerEmailConsumer()
    consumer.start_consuming()


if __name__ == "__main__":
    main()
