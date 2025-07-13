from django.urls import path
from .views import (
    ProductCreateView,
    ProductListView,
    BookProductView,
    FarmerBookingsView,
    FarmerProductsView,
    ConsumerBookingsView,
    LatestProductsView,
)

urlpatterns = [
    path('products/', ProductListView.as_view()),
    path('products/book/', BookProductView.as_view()),
    path('products/view-bookings/', ConsumerBookingsView.as_view()),
    path('products/latest/', LatestProductsView.as_view()),
   
    path('farmer/post-product/', ProductCreateView.as_view()),
    path('farmer/bookings/', FarmerBookingsView.as_view()),
    path('farmer/my-products/', FarmerProductsView.as_view()),
]
