import uuid
from django.db import models


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('millet', 'Millet'),
        ('vegetable', 'Vegetable'),
        ('fruit', 'Fruit'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    zone = models.IntegerField()  
    def __str__(self):
        return f"{self.name} ({self.category}) - Zone {self.zone}"


class Auction(models.Model):
    auction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    zone = models.IntegerField()  
    bidders = models.JSONField(default=dict)  # {farmer_id: {product_id: price}}
    current_price = models.JSONField(default=dict)  # {product_id: avg_price}
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Auction {self.auction_id} (Zone {self.zone})"

class StagingBid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    farmer_id = models.IntegerField()
    price = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
