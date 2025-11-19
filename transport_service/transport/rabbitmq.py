# transport_service/rabbitmq.py
import pika
import json

def publish_booking_event(message: dict):
    # Connect to RabbitMQ running on localhost:5672
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    # Simple queue
    channel.queue_declare(queue="booking_events")

    # Publish JSON message
    channel.basic_publish(
        exchange="",
        routing_key="booking_events",
        body=json.dumps(message),
    )

    connection.close()
