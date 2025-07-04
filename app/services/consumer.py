import pika
import os

class RabbitmqConsumer:
    def __init__(self, callback) -> None:
        self.__host = os.getenv("RABBITMQ_HOST")
        self.__port =os.getenv("RABBITMQ_PORT")
        self.__username = os.getenv("RABBITMQ_USERNAME")
        self.__password = os.getenv("RABBITMQ_PASSWORD")
        self.__queue = os.getenv("RABBITMQ_QUEUE")
        self.__callback = callback
        self.__channel = self.__create_channel()

    def __create_channel(self):
        connection_parameters = pika.ConnectionParameters(
            host=self.__host,
            port=self.__port,
            credentials=pika.PlainCredentials(
                username=self.__username,
                password=self.__password
            )
        )

        channel = pika.BlockingConnection(connection_parameters).channel()
        channel.queue_declare(
            queue=self.__queue,
            durable=True
        )
        channel.basic_consume(
            queue=self.__queue,
            auto_ack=True,
            on_message_callback=self.__callback
        )

        return channel
    
    def start(self):
        self.__channel.start_consuming()

def minha_callback(ch, method, properties, body):
    print(body)

rabitmq_consumer = RabbitmqConsumer(minha_callback)
rabitmq_consumer.start()