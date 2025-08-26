import uuid
from django.utils import timezone
from .models import Auction

ZONES = [1,2,3,4,5,6,7,8,9,10]

def create_weekly_auctions():
    """Creates 10 auctions for 10 zones"""
    for zone in ZONES:
        Auction.objects.create(
            auction_id=uuid.uuid4(),
            zone=zone,
            created_at=timezone.now()
        )
    print("10 auctions created")



def deactivate_all_auctions():
    """Sets isActive=False for all active auctions."""
    updated = Auction.objects.filter(is_active=True).update(is_active=False)
    print(f"{updated} auctions deactivated")



