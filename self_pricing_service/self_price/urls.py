from django.urls import path
from .views import HealthCheckView, AddBidderView, UpdateAveragePriceView , GetSessionView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('add_bidder/<uuid:pk>/', AddBidderView.as_view(), name='add-bidder'),
    path('update-price/', UpdateAveragePriceView.as_view(), name='update-average-price'),
    path('session/<int:zone>/', GetSessionView.as_view(), name='get-session'),
]