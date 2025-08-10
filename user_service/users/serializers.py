from rest_framework import serializers


from .models import Farmer, Consumer, Transporter, wholesaler, admin
from django.contrib.auth.hashers import make_password



#Farmer Serializer
class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model= Farmer
        fields = '__all__'
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


# Consumer Serializer
class ConsumerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Consumer
        fields = '__all__'
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
# Transporter Serializer
class TransporterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transporter
        fields = '__all__'
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
# Wholesaler Serializer
class WholesalerSerializer(serializers.ModelSerializer):
    class Meta:
        model = wholesaler
        fields = '__all__'
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

#admin serializer
class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = admin
        fields = '__all__'
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)