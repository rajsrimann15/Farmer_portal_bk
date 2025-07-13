# urls.py
from django.urls import path
from .views import CreateScheduleView, ListAvailableSchedules, BookScheduleView , ListTransporterBookings, ListFarmerBookings

urlpatterns = [
    path('schedule/create/', CreateScheduleView.as_view()),
    path('schedule/available/', ListAvailableSchedules.as_view()),
    path('schedule/book/', BookScheduleView.as_view()),
    path("bookings/transporter/", ListTransporterBookings.as_view()),
    path("bookings/farmer/", ListFarmerBookings.as_view(), name='farmer_bookings'),
]
