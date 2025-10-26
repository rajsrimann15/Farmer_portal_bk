import io
import uuid
from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from decouple import config
from .permissions import IsConsumer, IsFarmer
from .models import Product, Booking
from .serializers import ProductSerializer, BookingSerializer
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from imagekitio import ImageKit
from datetime import timedelta
from django.utils import timezone
from .permissions import IsAdmin
from .utils.imagekit_helper import imagekit
from PIL import Image


SECRET_API_KEY = config('SECRET_API_KEY')


#HealthCheckView
class HealthCheckView(APIView):
    #permission_classes = [IsAdmin]
    def get(self, request):
        return Response({'status': 'ecom_service is live'}, status=status.HTTP_200_OK)

# Farmer - Create Product
class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsFarmer]
    queryset = Product.objects.all()

    def perform_create(self, serializer):
        farmer_id = self.request.headers.get("X-User-Id")
        if not farmer_id:
            raise ValidationError({"error": "X-User-Id header is required"})

        image_file = self.request.FILES.get("image")
        image_url = None

        if image_file:
            try:
                # Open the uploaded image
                img = Image.open(image_file)

                # Convert to RGB (necessary for JPG)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                # Save to a BytesIO buffer as JPG
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=90)
                buffer.seek(0)

                # Generate unique filename
                file_name = f"{uuid.uuid4()}.jpg"

                # Upload to ImageKit
                upload = imagekit.upload_file(
                    file=buffer,  # Can pass BytesIO directly
                    file_name=file_name,
                    options={"folder": "/products", "is_private_file": False}
                )

                image_url = upload.get("url")
                if not image_url:
                    raise ValidationError({"image_upload_error": "ImageKit did not return a URL."})

            except Exception as e:
                raise ValidationError({"image_upload_error": str(e)})

        serializer.save(farmer_id=farmer_id, image_id=image_url)


#  Consumer - List/Search Products
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsConsumer]
    queryset = Product.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'farmer_id']  # Search by product name or farmer_id


#  Consumer - Book a Product
class BookProductView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsConsumer]
    queryset = Booking.objects.all()

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        product = validated_data.get('product')
        quantity = validated_data.get('quantity')

        if not product or not quantity:
            raise ValidationError("Both 'product' and 'quantity' are required.")
        
        if quantity > product.quantity_available:
            raise ValidationError("Not enough stock available.")
        
        # Get the X-User-Id header from request
        consumer_id = self.request.headers.get("X-User-Id")
        if not consumer_id:
            raise ValidationError({"error": "X-User-Id header is required"})

        # Reduce product stock
        product.quantity_available -= quantity
        product.save()
        serializer.save(consumer_id=consumer_id)


#  Farmer - Get All Bookings for Their Products
class FarmerBookingsView(APIView):
    permission_classes = [IsFarmer]
    def get(self, request):
        farmer_id = request.headers.get('X-User-Id')
        if not farmer_id:
            return Response({"error": "farmer_id query param is required"}, status=400)

        bookings = Booking.objects.filter(product__farmer_id=farmer_id)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    

# Farmer - Get All posted Products
class FarmerProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsFarmer]
    def get_queryset(self):
        farmer_id = self.request.headers.get('X-User-Id')
        if not farmer_id:
            return Product.objects.none()  # Return empty queryset if no farmer_id provided
        return Product.objects.filter(farmer_id=farmer_id)
    
#Consumer - Get All Booking histroy
class ConsumerBookingsView(APIView):
    permission_classes = [IsConsumer]
    def get(self, request):
        consumer_id = request.headers.get('X-User-Id')
        if not consumer_id:
            return Response({"error": "consumer_id query param is required"}, status=400)

        bookings = Booking.objects.filter(consumer_id=consumer_id)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
#Consumer - Get All latest products
class LatestProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsConsumer]
    def get_queryset(self):
        return Product.objects.order_by('-created_at')[:10]

#stats
class StatsView(APIView):
        def get(self, request):
        # Verify secret key
            secret_key = request.headers.get("X-SECRET-KEY")
            if secret_key != SECRET_API_KEY:
                return Response(
                    {"detail": "Unauthorized - Invalid Secret Key"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            today = timezone.now()
            last_week = today - timedelta(days=7)

            # Count farmers created in the last week
            new_farmers = Product.objects.filter(created_at=last_week).count()
            total_farmers = Product.objects.count()

            return Response({
                "new_products_last_week": new_farmers,
                "total_products": total_farmers
            })



  
    