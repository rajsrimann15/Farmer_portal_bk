from django.urls import path

from .views import (
    admin_login,
    admin_register,
    farmer_register,
    consumer_register,
    transporter_register,
    farmer_login,
    consumer_login,
    transporter_login,
    TokenRefreshView,
    HealthCheckView,
    GetZoneIdView,
    wholesaler_login,
    wholesaler_register,
)

urlpatterns = [

    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('farmer/register/', farmer_register.as_view()),
    path('consumer/register/', consumer_register.as_view()),
    path('transporter/register/', transporter_register.as_view()),
    path('wholesaler/register/', wholesaler_register.as_view()),
    path('admin/register/', admin_register.as_view()),

    path('farmer/login/', farmer_login.as_view()),
    path('consumer/login/', consumer_login.as_view()),
    path('transporter/login/', transporter_login.as_view()),
    path('wholesaler/login/', wholesaler_login.as_view()),
    path('admin/login/', admin_login.as_view()),

    path('token/refresh/', TokenRefreshView.as_view()),
    path('get_zone_id/<int:user_id>/', GetZoneIdView.as_view(), name='get-zone-id')
]