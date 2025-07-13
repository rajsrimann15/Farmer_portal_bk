from django.urls import path
from . import views
from .views import AuctionDetailView, CreateAuctionView, LatestAuctionByZoneView, PlaceBidView, ProductByZoneView, ProductPriceTrendView, StopAuctionView, FarmerActivityView

urlpatterns = [
   path('create/', CreateAuctionView.as_view(), name='create-auction'),
   path('products/<int:zone_id>/', ProductByZoneView.as_view(), name='products-by-zone'),
   path('place-bid/', PlaceBidView.as_view()),
   path('<uuid:auction_id>/', AuctionDetailView.as_view(), name='auction-detail'),

   path('<uuid:auction_id>/stop/', StopAuctionView.as_view(), name='auction-stop'),
   path('zone/<int:zone_id>/latest/', LatestAuctionByZoneView.as_view()),
   path('price-trend/<int:zone_id>/<str:product_identifier>/', ProductPriceTrendView.as_view()),

   path('farmer-activity/<int:farmer_id>/', FarmerActivityView.as_view(), name='farmer-activity'),
   
]

