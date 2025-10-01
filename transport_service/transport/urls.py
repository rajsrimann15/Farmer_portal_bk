# urls.py
from django.urls import path
from .views import CreateScheduleView, ListAvailableSchedules, BookScheduleView , ListTransporterBookings, ListFarmerBookings, HealthCheckView,ListTransporterSchedules


urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('schedule/create/', CreateScheduleView.as_view()),
    path('schedule/available/', ListAvailableSchedules.as_view()),
    path('schedule/book/', BookScheduleView.as_view()),
    path("bookings/transporter/", ListTransporterBookings.as_view()),
    path("bookings/farmer/", ListFarmerBookings.as_view(), name='farmer_bookings'),
    path("schedules/transporter/", ListTransporterSchedules.as_view(), name='transporter_schedules')

]
