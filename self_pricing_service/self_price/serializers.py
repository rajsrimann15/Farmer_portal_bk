from rest_framework import serializers
from .models import farmer_pricing, MSP

class farmerPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = farmer_pricing
        fields = '__all__'  # Include all fields from the model

class MSPSerializer(serializers.ModelSerializer):
    class Meta:
        model = MSP
        fields = '__all__'  # Include all fields from the model
