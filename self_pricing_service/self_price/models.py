import uuid
from django.db import models


class farmer_pricing(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False, unique=True)
    zone = models.IntegerField()  
    bidders = models.JSONField(default=dict)  #{farmer_id: {product_name: price}}
    current_price = models.JSONField(default=dict) #{product_name:price}
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Farmer Pricing {self.id} (Zone {self.zone})"

class MSP(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False, unique=True)
    zone= models.IntegerField()
    current_price = models.JSONField(default=dict)  # {product_name: price}
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MSP {self.id} (Zone {self.zone})"



