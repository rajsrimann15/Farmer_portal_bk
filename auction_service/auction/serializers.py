from rest_framework import serializers
from .models import Auction, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'zone']


class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ['auction_id', 'zone', 'bidders', 'current_price', 'created_at', 'last_updated']


class PlaceBidSerializer(serializers.Serializer):
    auction_id = serializers.UUIDField()
    product_id = serializers.IntegerField()
    farmer_id = serializers.IntegerField()
    price = serializers.FloatField()