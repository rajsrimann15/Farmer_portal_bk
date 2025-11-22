# notification_service/urls.py (project level)
from django.urls import path
from .views import TransporterNotificationView, EcomNotificationView

urlpatterns = [
    path('notifications/transport/', TransporterNotificationView.as_view(), name='transporter-notifications'),
    path('notifications/transport/mark-read/<int:id>/', TransporterNotificationView.as_view(), name='mark-transport-notification-read'),
    path('notifications/ecom/unread/', EcomNotificationView.as_view(), name='ecom-unread-notifications'),
    path('notifications/ecom/mark-read/<int:id>/', EcomNotificationView.as_view(), name='mark-ecom-notification-read'),
]