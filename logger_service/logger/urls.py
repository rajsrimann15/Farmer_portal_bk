from django.urls import include, path
from .views import log_request

urlpatterns = [
     path('api/logger/', include('logger.urls')),
]
