from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from users.models import Farmer, Consumer, Transporter
from users.serializers import FarmerSerializer, ConsumerSerializer, TransporterSerializer
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password

# Function to generate JWT tokens 
def get_token(user):
    refresh = RefreshToken.for_user(user)

    # Add required claims
    refresh['iss'] = 'raj-key'         
    refresh['user_id'] = user.id       

    # Role-based fields
    if hasattr(user, 'farmer_id'):
        refresh['farmer_id'] = user.farmer_id
    elif hasattr(user, 'gst_id'):
        refresh['gst_id'] = user.gst_id
    elif hasattr(user, 'email'):
        refresh['email'] = user.email

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
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


#Login  for different user types
class farmer_login(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        farmer= get_object_or_404(Farmer, phone_number=phone_number)
        
        #exception handling
        if not check_password(password,farmer.password):
            return Response({"error": "Invalid credentials"}, status=400)
        
        token= get_token(farmer)
        return Response(token, status= 200)

class consumer_login(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        consumer = get_object_or_404(Consumer, email=email)
        
        # exception handling
        if not check_password(password, consumer.password):
            return Response({"error": "Invalid credentials"}, status=400)
        
        token = get_token(consumer)
        return Response(token, status=200)

class transporter_login(APIView):
    def post(self, request):
        email= request.data.get('email')
        password = request.data.get('password')
        transporter = get_object_or_404(Transporter, email=email)
        
        # exception handling
        if not check_password(password, transporter.password):
            return Response({"error": "Invalid credentials"}, status=400)
        
        token = get_token(transporter)
        return Response(token, status=200)
    

#Refresh token view 
class TokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=400)

        try:
            refresh = RefreshToken(refresh_token)

             #identifying the user based on role-specific
            user = None
            if 'farmer_id' in refresh:
                user = Farmer.objects.get(farmer_id=refresh['farmer_id'])
            elif 'gst_id' in refresh:
                user = Transporter.objects.get(gst_id=refresh['gst_id'])
            elif 'email' in refresh:
                user = Consumer.objects.get(email=refresh['email'])

            if not user:
                return Response({"error": "User not found"}, status=404)

            # Generate new refresh and access token
            new_refresh = RefreshToken.for_user(user)
            new_access = new_refresh.access_token

            #Add custom claims again
            new_access['user_id'] = user.id
            new_access['role'] = user.__class__.__name__.lower()
            new_access['name'] = user.name

            if hasattr(user, 'farmer_id'):
                new_access['farmer_id'] = user.farmer_id
            elif hasattr(user, 'gst_id'):
                new_access['gst_id'] = user.gst_id
            elif hasattr(user, 'email'):
                new_access['email'] = user.email

            return Response({
                'access': str(new_access),
                'refresh': str(new_refresh),
            }, status=200)

        except TokenError:
            return Response({"error": "Invalid or expired refresh token"}, status=401)
        except (Farmer.DoesNotExist, Transporter.DoesNotExist, Consumer.DoesNotExist):
            return Response({"error": "User not found"}, status=404)

        
    
        