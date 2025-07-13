from django.urls import path

from .views import (
    farmer_register,
    consumer_register,
    transporter_register,
    farmer_login,
    consumer_login,
    transporter_login,
    TokenRefreshView,
)

urlpatterns = [
    path('farmer/register/', farmer_register.as_view()),
    path('consumer/register/', consumer_register.as_view()),
    path('transporter/register/', transporter_register.as_view()),

    path('farmer/login/', farmer_login.as_view()),
    path('consumer/login/', consumer_login.as_view()),
    path('transporter/login/', transporter_login.as_view()),

    path('token/refresh/', TokenRefreshView.as_view())
]