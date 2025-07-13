from rest_framework import serializers
from ..models import RouteSegment, RoutePoint

def check_segment_capacity(schedule_id,from_place,to_place,goods_weight):
    segments = RoutePoint.objects.filter(schedule_id=schedule_id)
    pass_through= False

    for seg in segments:
        if seg.place_name == from_place:
            pass_through = True
        if pass_through and seg.place_name == to_place:
            if seg.current_capacity + goods_weight > seg.max_capacity:
                return False
            else:
                seg.current_capacity += goods_weight
                seg.save()
                return True
            
def update_segment_load(schedule_id, from_place, to_place, goods_weight):
    segments = RouteSegment.objects.filter(schedule_id=schedule_id)
    pass_through = False
    for seg in segments:
        if seg.from_place == from_place:
            pass_through = True
        if pass_through:
            seg.current_load += goods_weight
            seg.save()
        if seg.to_place == to_place:
            break
            
    