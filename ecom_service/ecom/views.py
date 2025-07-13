from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .models import Product, Booking
from .serializers import ProductSerializer, BookingSerializer

# Farmer - Create Product
class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


#  Consumer - List/Search Products
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'farmer_id']  # Search by product name or farmer_id


#  Consumer - Book a Product
class BookProductView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        product = validated_data.get('product')
        quantity = validated_data.get('quantity')

        if not product or not quantity:
            raise ValidationError("Both 'product' and 'quantity' are required.")
        
        if quantity > product.quantity_available:
            raise ValidationError("Not enough stock available.")

        # Reduce product stock
        product.quantity_available -= quantity
        product.save()

        serializer.save()


#  Farmer - Get All Bookings for Their Products
class FarmerBookingsView(APIView):
    def get(self, request):
        farmer_id = request.query_params.get('farmer_id')
        if not farmer_id:
            return Response({"error": "farmer_id query param is required"}, status=400)

        bookings = Booking.objects.filter(product__farmer_id=farmer_id)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    

# Farmer - Get All posted Products
class FarmerProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        farmer_id = self.request.query_params.get('farmer_id')
        if not farmer_id:
            return Product.objects.none()  # Return empty queryset if no farmer_id provided
        return Product.objects.filter(farmer_id=farmer_id)
    
#Consumer - Get All Bookings for Their Products
class ConsumerBookingsView(APIView):
    def get(self, request):
        consumer_id = request.query_params.get('consumer_id')
        if not consumer_id:
            return Response({"error": "consumer_id query param is required"}, status=400)

        bookings = Booking.objects.filter(consumer_id=consumer_id)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
#Consumer - Get All latest products
class LatestProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.order_by('-created_at')[:10]  
    