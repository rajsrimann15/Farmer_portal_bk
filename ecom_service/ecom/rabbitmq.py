# ecom_service/rabbitmq.py
import pika
import json

def publish_order_event(message: dict):
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    # Declare ecom queue
    channel.queue_declare(queue="ecom_order_events")

    # Publish JSON message
    channel.basic_publish(
        exchange="",
        routing_key="ecom_order_events",
        body=json.dumps(message),
    )

    connection.close()
