# views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .models import TransportSchedule, RoutePoint, Segment, Booking
from .serializers import TransportScheduleSerializer, BookingSerializer
from datetime import datetime
from django.shortcuts import get_object_or_404

# Create a schedule  
class CreateScheduleView(generics.CreateAPIView):
    queryset = TransportSchedule.objects.all()
    serializer_class = TransportScheduleSerializer
    
# List all available schedules
class ListAvailableSchedules(generics.ListAPIView):
    serializer_class = TransportScheduleSerializer

    def get_queryset(self):
        from_place = self.request.query_params.get('from_place')
        to_place = self.request.query_params.get('to_place')
        weight = int(self.request.query_params.get('weight', 1))
        date_str = self.request.query_params.get('date')

        # Parse date from query
        filter_date = None
        if date_str:
            try:
                filter_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return TransportSchedule.objects.none()  # Invalid date

        self.available_map = {}
        matching_ids = []

        for schedule in TransportSchedule.objects.prefetch_related('route_points', 'segments'):
            #Construct full route including start_place
            full_route = [
                RoutePoint(
                    schedule=schedule,
                    stop=0,
                    to_place=schedule.start_place,
                    date=schedule.start_date,
                    approx_time=schedule.start_time
                )
            ] + list(schedule.route_points.order_by('stop'))

            stops = [p.to_place for p in full_route]

            try:
                from_idx = stops.index(from_place)
                to_idx = stops.index(to_place)
            except ValueError:
                continue

            if from_idx >= to_idx:
                continue

            #Date filter (based on from_point)
            if filter_date:
                from_point_date = full_route[from_idx].date
                if from_point_date != filter_date:
                    continue

            from_stop = full_route[from_idx].stop
            to_stop = full_route[to_idx].stop

            segments = Segment.objects.filter(
                schedule=schedule,
                from_stop__gte=from_stop,
                to_stop__lte=to_stop
            )

            min_capacity = min((seg.available_capacity for seg in segments), default=0)

            if min_capacity >= weight:
                matching_ids.append(schedule.id)
                self.available_map[str(schedule.id)] = min_capacity

        return TransportSchedule.objects.filter(id__in=matching_ids)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['available_map'] = getattr(self, 'available_map', {})
        return context

# Book a schedule
class BookScheduleView(generics.CreateAPIView):
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        schedule_id = data.get("schedule")
        from_place = data.get("from_place")
        to_place = data.get("to_place")
        weight = int(data.get("weight", 1))
        date_str = data.get("date")

        # Parse and validate date
        if not date_str:
            return Response({"error": "Booking date is required"}, status=400)

        try:
            booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # Fetch schedule and construct full route (including start place as stop 0)
        try:
            schedule = TransportSchedule.objects.get(id=schedule_id)
        except TransportSchedule.DoesNotExist:
            return Response({"error": "Schedule not found"}, status=404)

        full_route = [
            RoutePoint(
                schedule=schedule,
                stop=0,
                to_place=schedule.start_place,
                date=schedule.start_date,
                approx_time=schedule.start_time
            )
        ] + list(schedule.route_points.order_by("stop"))

        try:
            from_idx = [p.to_place for p in full_route].index(from_place)
            to_idx = [p.to_place for p in full_route].index(to_place)
        except ValueError:
            return Response({"error": "Invalid from_place or to_place"}, status=400)

        if from_idx >= to_idx:
            return Response({"error": "Invalid route order"}, status=400)

        # Date filter based on from_place date
        from_point_date = full_route[from_idx].date
        if from_point_date != booking_date:
            return Response({"error": "No service available on given date"}, status=400)

        from_stop = full_route[from_idx].stop
        to_stop = full_route[to_idx].stop

        segments = Segment.objects.filter(
            schedule=schedule,
            from_stop__gte=from_stop,
            to_stop__lte=to_stop
        )

        if not all(seg.available_capacity >= weight for seg in segments):
            return Response({"error": "Not enough capacity"}, status=400)

        # Deduct capacity
        for seg in segments:
            seg.available_capacity -= weight
            seg.save()

        # Create booking
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# List bookings for a transporter
class ListTransporterBookings(generics.ListAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        transporter_id = self.request.query_params.get("transporter_id")
        if not transporter_id:
            return Booking.objects.none()

        schedule_id = self.request.query_params.get("schedule")
        from_place = self.request.query_params.get("from_place")
        date = self.request.query_params.get("date")

        # Get all schedules for the transporter
        schedules = TransportSchedule.objects.filter(transporter_id=transporter_id)

        # Start with all bookings linked to those schedules
        bookings = Booking.objects.filter(schedule__in=schedules)

        if schedule_id:
            bookings = bookings.filter(schedule__id=schedule_id)

        if from_place:
            bookings = bookings.filter(from_place=from_place)

        if date:
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%d").date()

                # Get all schedules with route points on this date
                matching_schedule_ids = RoutePoint.objects.filter(
                    date=date_obj,
                    schedule__in=schedules
                ).values_list("schedule_id", flat=True)

                # Filter bookings by those schedules
                bookings = bookings.filter(schedule__id__in=matching_schedule_ids)

            except ValueError:
                pass  # Optionally raise a 400 error for bad date

        return bookings.order_by("-booking_time")

#List bookings for the farmer
class ListFarmerBookings(generics.ListAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        farmer_id = self.request.query_params.get("farmer_id")
        if not farmer_id:
            return Booking.objects.none()

        # Get all bookings for the farmer
        return Booking.objects.filter(farmer_id=farmer_id).order_by("-booking_time")
    