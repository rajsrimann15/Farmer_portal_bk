import json
import os
import django
from datetime import datetime

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transport_service.settings")  # Replace with your settings module
django.setup()

from transport.models import TransportSchedule, RoutePoint  # Update app/model names

with open("bulk_transport_schedules.json", "r") as file:
    data_list = json.load(file)

# Load JSON
for data in data_list:
    schedule = TransportSchedule.objects.create(
        transporter_id=data["transporter_id"],
        vehicle_name=data["vehicle_name"],
        vehicle_type=data["vehicle_type"],
        vehicle_number=data["vehicle_number"],
        total_capacity=data["total_capacity"],
        price_per_kg=data["price_per_kg"],
        price_per_km=data["price_per_km"],
        support_loading=data["support_loading"],
        support_unloading=data["support_unloading"],
        start_place=data["start_place"],
        start_time=data["start_time"],
        start_date=data["start_date"],
        destination_place=data["destination_place"],
        destination_date=data["destination_date"],
    )

    for route in data["route_points"]:
        RoutePoint.objects.create(
            schedule=schedule,
            stop=route["stop"],
            to_place=route["to_place"],
            date=route["date"],
            approx_time=route["approx_time"]
        )

print("Schedule and route points inserted successfully.")
