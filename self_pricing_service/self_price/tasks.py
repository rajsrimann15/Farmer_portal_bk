import uuid
from django.utils import timezone
from .models import farmer_pricing

ZONES = [1,2,3,4,5,6,7,8,9,10]

def create_weekly_pricing_sessions():
    """Creates 10 sesssions for 10 zones"""
    for zone in ZONES:
        farmer_pricing.objects.create(
            id=uuid.uuid4(),
            zone=zone,
            created_at=timezone.now()
        )
    print("10 sessions created")



def deactivate_all_sessions():
    """Sets isActive=False for all active auctions."""
    updated = farmer_pricing.objects.filter(is_active=True).update(is_active=False)
    print(f"{updated} auctions deactivated")



