from django.db import models


class Farmer(models.Model):
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

    def __str__(self):
        return f"{self.name} ({self.farmer_id})"


class Consumer(models.Model):
    name=models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    email=models.EmailField(unique=True, null=True)
    password=models.CharField(max_length=100)
    address=models.CharField(null=True,max_length=255)
    district = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    

    def __str__(self):
        return f"Consumer({self.name}, {self.phone_number})"


class Transporter(models.Model):
    gst_id = models.CharField(max_length=100, unique=True)
    owner_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, null=True)
    password=models.CharField(max_length=100)
    address=models.CharField(max_length=255,null=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"Transporter({self.owner_name}, {self.gst_id})"
        
        
        
