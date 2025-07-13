# serializers.py
from rest_framework import serializers
from .models import TransportSchedule, RoutePoint, Segment, Booking

class RoutePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutePoint
        exclude = ['schedule']

class TransportScheduleSerializer(serializers.ModelSerializer):
    route_points = RoutePointSerializer(many=True)
    available_weight = serializers.SerializerMethodField()

    class Meta:
        model = TransportSchedule
        fields = '__all__'  # includes available_weight dynamically

    def get_available_weight(self, obj):
        available_map = self.context.get('available_map', {})
        return available_map.get(str(obj.id), None)

    def create(self, validated_data):
        points_data = validated_data.pop('route_points')
        schedule = TransportSchedule.objects.create(**validated_data)

        # Add starting point
        start_point = RoutePoint.objects.create(
            schedule=schedule,
            stop=0,
            to_place=validated_data['start_place'],
            date=validated_data['start_date'],
            approx_time=validated_data['start_time']
        )

        #Create all route points
        route_points = [start_point]
        for idx, point_data in enumerate(points_data, start=1):
            clean_data = point_data.copy()
            clean_data.pop('stop', None)
            point = RoutePoint.objects.create(schedule=schedule, stop=idx, **clean_data)
            route_points.append(point)

        # Create segments
        for i in range(len(route_points) - 1):
            Segment.objects.create(
                schedule=schedule,
                from_stop=route_points[i].stop,
                to_stop=route_points[i + 1].stop,
                from_place=route_points[i].to_place,
                to_place=route_points[i + 1].to_place,
                available_capacity=schedule.total_capacity
            )
        return schedule

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
