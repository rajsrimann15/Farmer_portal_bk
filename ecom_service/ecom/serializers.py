from rest_framework import serializers
from .models import Product, Booking

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False)
    image_id = serializers.URLField(read_only=True)

    class Meta:
        model = Product
        exclude = ['farmer_id']


class BookingSerializer(serializers.ModelSerializer):
     
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, source='product'
    )
    
    product = ProductSerializer(read_only=True)  
    class Meta:
        model = Booking
        exclude = ['consumer_id']
