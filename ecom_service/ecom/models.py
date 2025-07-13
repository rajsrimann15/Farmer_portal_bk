from django.db import models
import uuid

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Generated locally
    farmer_id = models.CharField(max_length=100)  # Provided by frontend (from user_service)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} by Farmer {self.farmer_id}"


class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Generated locally
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="bookings")
    consumer_id = models.CharField(max_length=100)  # Provided by frontend (from user_service)
    quantity = models.PositiveIntegerField()
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} - Product {self.product.name} by Consumer {self.consumer_id}"
