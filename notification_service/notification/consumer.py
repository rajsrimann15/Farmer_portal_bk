import sys
from pathlib import Path
import os
import django
import json
import pika
from decouple import config

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notification_service.settings")
django.setup()

from notification.models import TransporterBooking, EcomOrderNotification

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    channel.queue_declare(queue="booking_events")       # transport queue
    channel.queue_declare(queue="ecom_order_events")    # ecom queue

    # ----- TRANSPORT CALLBACK -----
    def transport_callback(ch, method, properties, body):
        data = json.loads(body)
        print("Received transport booking event:", data)

        TransporterBooking.objects.create(
            transporter_id=data["transporter_id"],
            schedule_id=data["schedule"],
            from_place=data["from_place"],
            to_place=data["to_place"],
            weight=data["weight"],
            date=data["date"],
            total_cost=data["total_cost"],
            description=data["description"],
            read=False,
        )

        print(f"Transport notification stored for transporter: {data['transporter_id']}")

    # ----- ECOM CALLBACK -----
    def ecom_callback(ch, method, properties, body):
        data = json.loads(body)
        print("Received ecom order event:", data)

        EcomOrderNotification.objects.create(
            order_id=data["id"],
            consumer_id=data["consumer_id"],
            farmer_id=data["farmer_id"],
            name=data["name"],
            quantity=data["quantity"],
            price=data["price"],
            read=False,
        )

        print(f"Ecom notification stored for order: {data['order_id']}")

    # Listen to both queues
    channel.basic_consume(
        queue="booking_events",
        on_message_callback=transport_callback,
        auto_ack=True,
    )
    channel.basic_consume(
        queue="ecom_order_events",
        on_message_callback=ecom_callback,
        auto_ack=True,
    )

    print(" [*] Waiting for events from transport & ecom...")
    channel.start_consuming()


if __name__ == "__main__":
    main()
