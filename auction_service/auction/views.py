from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView


from .models import Auction, Product, StagingBid
from .serializers import AuctionSerializer, PlaceBidSerializer, ProductSerializer
from rest_framework import status

# CreateAuctionView
class CreateAuctionView(generics.CreateAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer

# ProductByZoneView
class ProductByZoneView(APIView):
    def get(self, request, zone_id):
        products = Product.objects.filter(zone=zone_id)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

#  PlaceBidView
class PlaceBidView(APIView):
    def post(self, request):
        serializer = PlaceBidSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        auction_id = serializer.validated_data['auction_id']
        product_id = serializer.validated_data['product_id']
        farmer_id = serializer.validated_data['farmer_id']
        price = serializer.validated_data['price']

        auction = get_object_or_404(Auction, auction_id=auction_id)
        product = get_object_or_404(Product, id=product_id)

        if not auction.is_active:
            return Response({'error': 'Auction is not active'}, status=status.HTTP_400_BAD_REQUEST)

        if price:
            try:
                self.validate_price(price, product)
            except ValueError:
                return Response({'error': 'Enter a valid price'}, status=status.HTTP_400_BAD_REQUEST)

        # Get current price map
        current_price_map = auction.current_price or {}
        product_key = str(product.id)

        # CASE 1: No existing price for this product → Direct update
        if product_key not in current_price_map:
            auction.current_price[product_key] = price
            auction.bidders = auction.bidders or {}
            auction.bidders[str(farmer_id)] = {product_key: price}
            auction.save()
            return Response({'message': 'First bid saved directly to auction'}, status=status.HTTP_201_CREATED)

        # CASE 2: Existing price exists → Add to staging
        StagingBid.objects.create(
            auction=auction,
            product=product,
            farmer_id=farmer_id,
            price=price
        )

        bid_count = StagingBid.objects.filter(auction=auction, product=product).count()
        if bid_count >= 2:
            self.compute_and_flush_bids(auction, product)

        return Response({'message': 'Bid submitted'}, status=status.HTTP_201_CREATED)

    def compute_and_flush_bids(self, auction, product):
        staging_bids = StagingBid.objects.filter(auction=auction, product=product)
        existing_price = auction.current_price.get(str(product.id), 0)

        prices = [bid.price for bid in staging_bids] + [existing_price]

        # Smart average (slightly favors existing price to avoid loss)
        avg_price = sum(prices) / len(prices)

        # Build updated bidder map
        farmer_bid_map = {}
        for bid in staging_bids:
            fid = str(bid.farmer_id)
            if fid not in farmer_bid_map:
                farmer_bid_map[fid] = {}
            farmer_bid_map[fid][str(product.id)] = bid.price

        auction.current_price[str(product.id)] = avg_price
        auction.bidders = auction.bidders or {}

        for fid, prod_map in farmer_bid_map.items():
            if fid not in auction.bidders:
                auction.bidders[fid] = {}
            auction.bidders[fid].update(prod_map)

        auction.save()
        staging_bids.delete()


    # Validate price method
    def validate_price(self, price,product):
        if price >=1000:
            raise ValueError
        return True
    

# StopAuctionView
class StopAuctionView(APIView):
    def post(self, request, auction_id):
        auction = get_object_or_404(Auction, auction_id=auction_id)

        staging_bids = StagingBid.objects.filter(auction=auction)

        if not staging_bids.exists():
            return Response({'message': 'Auction sucessfully Stopped'}, status=status.HTTP_200_OK)

        auction.current_price = auction.current_price or {}
        auction.bidders = auction.bidders or {}

        product_to_bids = {}

        # Group bids by product
        for bid in staging_bids:
            pid = str(bid.product.id)
            if pid not in product_to_bids:
                product_to_bids[pid] = []
            product_to_bids[pid].append(bid)

        for pid, bids in product_to_bids.items():
            existing_price = auction.current_price.get(pid)
            prices = [bid.price for bid in bids]

            # Smart average:
            if existing_price is not None:
                prices.append(existing_price)
                avg_price = sum(prices) / len(prices)
            else:
                avg_price = sum(prices) / len(prices)

            auction.current_price[pid] = avg_price

            # Update bidders map
            for bid in bids:
                fid = str(bid.farmer_id)
                if fid not in auction.bidders:
                    auction.bidders[fid] = {}
                auction.bidders[fid][pid] = bid.price

        auction.is_active = False
        auction.save()
        staging_bids.delete()
        return Response({'message': 'Auction stopped and data flushed in staging bid'}, status=status.HTTP_200_OK)

# LatestAuctionByZoneView
class LatestAuctionByZoneView(APIView):
    def get(self, request, zone_id):
        # Get latest auction by zone (ordered by created_at DESC)
        latest_auction = Auction.objects.filter(zone=zone_id).order_by('-created_at').first()
        
        if not latest_auction:
            return Response({'message': 'No auctions found for this zone'}, status=status.HTTP_404_NOT_FOUND)

        # Format product prices
        product_prices = []
        for product_id, price in latest_auction.current_price.items():
            try:
                product = Product.objects.get(id=int(product_id))
                product_prices.append({
                    'product_id': product.id,
                    'name': product.name,
                    'category': product.category,
                    'price': price
                })
            except Product.DoesNotExist:
                continue

        return Response({
            'auction_id': latest_auction.auction_id,
            'zone': latest_auction.zone,
            'date': latest_auction.created_at,
            'products': product_prices
        }, status=status.HTTP_200_OK)
    
    
# Product Price Trend View   
class ProductPriceTrendView(APIView):
    def get(self, request, zone_id, product_identifier):
        # Try to fetch product by ID or name
        try:
            if product_identifier.isdigit():
                product = Product.objects.get(id=int(product_identifier), zone=zone_id)
            else:
                product = Product.objects.filter(name__iexact=product_identifier, zone=zone_id).first()
            if not product:
                return Response({'error': 'Product not found in this zone'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        product_id = str(product.id)

        # Get last 10 auctions for this zone that include this product
        auctions = Auction.objects.filter(
            zone=zone_id,
            current_price__has_key=product_id
        ).order_by('-created_at')[:10]

        # Format response
        price_trend = [
            {
                "product": product.name,
                "date": format(auction.created_at),
                "price": auction.current_price[product_id]
            }
            for auction in auctions
        ]

        return Response(price_trend, status=status.HTTP_200_OK)
    

# AuctionDetailView
class AuctionDetailView(RetrieveAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    lookup_field = 'auction_id'


#Get Farmer Acvity in auction
class FarmerActivityView(APIView):
    def get(self, request, farmer_id):
        # Get all auctions where this farmer has placed bids
        auctions = Auction.objects.filter(bidders__has_key=str(farmer_id)).order_by('-created_at')

        if not auctions.exists():
            return Response({'message': 'No activity found for this farmer'}, status=status.HTTP_404_NOT_FOUND)

        activity_data = []
        for auction in auctions:
            products = []
            for product_id, price in auction.bidders.get(str(farmer_id), {}).items():
                products.append({
                    'product_id': product_id,
                    'price': price
                })
            activity_data.append({
                'auction_id': auction.auction_id,
                'date': auction.created_at,
                'products': products
            })

        return Response(activity_data, status=status.HTTP_200_OK)
