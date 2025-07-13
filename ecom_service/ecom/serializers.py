from rest_framework import serializers
from .models import Product, Booking

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class BookingSerializer(serializers.ModelSerializer):
     
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, source='product'
    )
    
    product = ProductSerializer(read_only=True)  
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['id', 'booked_at']
