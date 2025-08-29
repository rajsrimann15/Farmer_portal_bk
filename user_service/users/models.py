import uuid
from django.db import models


class Farmer(models.Model):
    farmer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Generated locally
    farmer_govt_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    age = models.PositiveIntegerField()
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    zone = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now_add=True,null=True)


    def __str__(self):
        return f"{self.name} ({self.farmer_id})"


class Consumer(models.Model):
    consumer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Generated locally
    name=models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    email=models.EmailField(unique=True, null=True)
    password=models.CharField(max_length=100)
    address=models.CharField(null=True,max_length=255)
    district = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now_add=True,null=True)

    

    def __str__(self):
        return f"Consumer({self.name}, {self.phone_number})"


class Transporter(models.Model):
    transporter_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Generated locally
    gst_id = models.CharField(max_length=100, unique=True)
    owner_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, null=True)
    password=models.CharField(max_length=100)
    address=models.CharField(max_length=255,null=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now_add=True,null=True)

    
    def __str__(self):
        return f"Transporter({self.owner_name}, {self.gst_id})"
    

class wholesaler(models.Model):
    wholesaler_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Generated locally
    gst_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, null=True)
    password=models.CharField(max_length=100)
    address=models.CharField(max_length=255,null=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now_add=True,null=True)


    def __str__(self):
        return f"Wholesaler({self.name}, {self.gst_id})"


class admin(models.Model):
    admin_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Generated locally
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f"Admin({self.name})"
        
        
        
