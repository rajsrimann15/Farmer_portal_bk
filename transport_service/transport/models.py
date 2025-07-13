# models.py
import uuid
from django.db import models

class TransportSchedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transporter_id = models.CharField(max_length=100)
    vehicle_name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=100)
    total_capacity = models.IntegerField()
    price_per_kg = models.FloatField()
    price_per_km = models.FloatField()
    support_loading = models.BooleanField(default=False)
    support_unloading = models.BooleanField(default=False)
    start_place = models.CharField(max_length=100)
    start_time = models.TimeField()
    start_date = models.DateField()
    destination_place = models.CharField(max_length=100)
    destination_date = models.DateField()

class RoutePoint(models.Model):
    schedule = models.ForeignKey(TransportSchedule, related_name="route_points", on_delete=models.CASCADE)
    stop = models.IntegerField()
    to_place = models.CharField(max_length=100)
    date = models.DateField()
    approx_time = models.TimeField()

class Segment(models.Model):
    schedule = models.ForeignKey(TransportSchedule, related_name="segments", on_delete=models.CASCADE)
    from_stop = models.IntegerField()
    to_stop = models.IntegerField()
    from_place = models.CharField(max_length=100)
    to_place = models.CharField(max_length=100)
    available_capacity = models.IntegerField()

class Booking(models.Model):
    schedule = models.ForeignKey(TransportSchedule, on_delete=models.CASCADE)
    from_place = models.CharField(max_length=100)
    to_place = models.CharField(max_length=100)
    weight = models.IntegerField()
    farmer_id = models.CharField(max_length=100)
    booking_time = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
