from django.db import models

class TransporterBooking(models.Model):
    transporter_id = models.UUIDField()
    schedule_id = models.UUIDField()
    from_place = models.CharField(max_length=255)
    to_place = models.CharField(max_length=255)
    weight = models.FloatField()
    date = models.CharField(max_length=255)
    total_cost = models.FloatField()
    description = models.TextField()
    read = models.BooleanField(default=False)

    class Meta:
        db_table = "transporter_booking"


class EcomOrderNotification(models.Model):
    order_id = models.UUIDField()
    consumer_id = models.UUIDField()
    farmer_id = models.UUIDField()
    name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    price = models.FloatField()
    read = models.BooleanField(default=False)

    class Meta:
        db_table = "ecom_order_notification"
