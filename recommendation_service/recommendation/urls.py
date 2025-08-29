from django.urls import path
from .views import FarmerRecommendationView

urlpatterns = [
    path("recommendations/", FarmerRecommendationView.as_view(), name="recommendations"),
]
