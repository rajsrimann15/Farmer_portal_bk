from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from users.models import Farmer, Consumer, Transporter, admin, wholesaler
from users.serializers import AdminSerializer, FarmerSerializer, ConsumerSerializer, TransporterSerializer, WholesalerSerializer
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone

from .permissions import IsAdmin

#HealthCheckView
class HealthCheckView(APIView):
    #permission_classes = [IsAdmin]
    def get(self, request):
        return Response({'status': 'user_service is live'}, status=status.HTTP_200_OK)

# Function to generate JWT tokens 
def get_token(user):
    # Determine role & role-specific ID
    if hasattr(user, 'farmer_id'):
        role = 'farmer'
        uid = user.farmer_id
    elif hasattr(user, 'transporter_id'):
        role = 'transporter'
        uid = user.transporter_id
    elif hasattr(user, 'consumer_id'):
        role = 'consumer'
        uid = user.consumer_id
    elif hasattr(user, 'wholesaler_id'):
        role = 'wholesaler'
        uid = user.wholesaler_id
    elif hasattr(user, 'admin_id'):
        role = 'admin'
        uid = user.admin_id

    # Create refresh token without for_user()
    refresh = RefreshToken()
    refresh['user_id'] = str(uid)
    refresh['role'] = role
    refresh['iss'] = 'raj-key'

    # Create access token
    access_token = refresh.access_token
    access_token['user_id'] = str(uid)
    access_token['role'] = role
    access_token['iss'] = 'raj-key'

    return {
        'refresh': str(refresh),
        'refresh_expires_at': datetime.fromtimestamp(refresh['exp']).isoformat(),
        'access': str(access_token),
        'access_expires_at': datetime.fromtimestamp(access_token['exp']).isoformat(),
    }

#Registration views for different user types
class farmer_register(generics.CreateAPIView):
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer

class consumer_register(generics.CreateAPIView):
    queryset = Consumer.objects.all()
    serializer_class = ConsumerSerializer

class transporter_register(generics.CreateAPIView):
    queryset = Transporter.objects.all()
    serializer_class = TransporterSerializer

class wholesaler_register(generics.CreateAPIView):
    queryset = wholesaler.objects.all()
    serializer_class = WholesalerSerializer

class admin_register(generics.CreateAPIView):
    queryset = admin.objects.all()
    serializer_class = AdminSerializer

#Login  for different user types
class farmer_login(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        
        farmer= get_object_or_404(Farmer, phone_number=phone_number)
        
        #exception handling
        if not check_password(password,farmer.password):
            return Response({"error": "Invalid credentials"}, status=400)
        
        token=get_token(farmer)
        return Response(token, status=200)

class consumer_login(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        consumer = get_object_or_404(Consumer, email=email)
        
        # exception handling
        if not check_password(password, consumer.password):
            return Response({"error": "Invalid credentials"}, status=400)
        
        token = get_token(consumer)
        return Response(token,status=200)

class transporter_login(APIView):
    def post(self, request):
        email= request.data.get('email')
        password = request.data.get('password')
        transporter = get_object_or_404(Transporter, email=email)
        
        # exception handling
        if not check_password(password, transporter.password):
            return Response({"error": "Invalid credentials"}, status=400)
        
        token = get_token(transporter)
        return Response(token,status=200)

class wholesaler_login(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        wholesaler_user = get_object_or_404(wholesaler, email=email)
        
        # exception handling
        if not check_password(password, wholesaler_user.password):
            return Response({"error": "Invalid credentials"}, status=400)
        
        token = get_token(wholesaler_user)
        return Response(token,status=200)
    
class admin_login(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        admin_user = get_object_or_404(admin, email=email)
        
        # exception handling
        if not check_password(password, admin_user.password):
            return Response({"error": "Invalid credentials"}, status=400)
        
        token = get_token(admin_user)
        return Response(token,status=200)
    
#Refresh token view 
class TokenRefreshView(APIView):
    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response({"error": "Refresh token is required"}, status=400)

        try:
            token = RefreshToken(refresh)
        except TokenError:
            return Response({"error": "Invalid refresh token"}, status=400)
        
        role = token.get('role')
        user_id = token.get('user_id')

        if not role or not user_id:
            return Response({"error": "Missing role or user_id in token"}, status=400)

        # Generate new tokens
        if role == 'farmer':
            user = Farmer.objects.get(farmer_id=user_id)
        elif role == 'transporter':
            user = Transporter.objects.get(transporter_id=user_id)
        elif role == 'consumer':
            user = Consumer.objects.get(consumer_id=user_id)
        elif role == 'wholesaler':
            user = wholesaler.objects.get(wholesaler_id=user_id)
        elif role == 'admin':
            user = admin.objects.get(admin_id=user_id)

        new_tokens = get_token(user)
        return Response(new_tokens, status=200)
    
#get_zone_id
class GetZoneIdView(APIView):
    def get(self, request, user_id):
        try:
            farmer = Farmer.objects.get(id=user_id)
            zone_id = farmer.zone
            return Response({'zone_id': zone_id}, status=status.HTTP_200_OK)
        except Farmer.DoesNotExist:
            return Response({'error': 'Farmer not found'}, status=status.HTTP_404_NOT_FOUND)

#Stats view
class FarmerStatsView(APIView):
    #permission_classes = [IsAdmin]
    def get(self, request):
        today = timezone.now()
        last_week = today - timedelta(days=7)

        new_farmers = Farmer.objects.filter(created_at__gte=last_week).count()
        total_farmers = Farmer.objects.count()

        return Response({
            "new_farmers_last_week": new_farmers,
            "total_farmers": total_farmers
        })      
    
        