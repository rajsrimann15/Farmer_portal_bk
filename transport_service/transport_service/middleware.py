import jwt
from django.http import JsonResponse
from django.conf import settings

def jwt_auth_middleware(get_response):
    def middleware(request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            r