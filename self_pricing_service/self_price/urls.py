from django.urls import path
from .views import HealthCheckView, AddBidderView, UpdateAveragePriceView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('add_bidder/<uuid:pk>/', AddBidderView.as_view(), name='add-bidder'),
    path('update-price/', UpdateAveragePriceView.as_view(), name='update-average-price'),
]