from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import farmer_pricing  , MSP
from .serializers import farmerPricingSerializer, MSPSerializer
from  .permissions import IsConsumer, IsFarmer, IsAdmin
import statistics

#HealthCheckView
class HealthCheckView(APIView):
    #permission_classes = [IsAdmin]
    def get(self, request):
        return Response({'status': 'self_pricing_service is live'}, status=status.HTTP_200_OK)
    
#FarmerPricingView
class AddBidderView(APIView):
    permission_classes = [IsFarmer]
    def post(self, request, pk):
        try:
            farmer_price = farmer_pricing.objects.get(id=pk)
        except farmer_pricing.DoesNotExist:
            return Response({"error": "FarmerPricing not found"}, status=status.HTTP_404_NOT_FOUND)

        farmer_id = request.headers.get("X-User-Id")
        product_name = request.data.get("product_name")
        price = request.data.get("price")

        if not (farmer_id and product_name and price):
            return Response(
                {"error": "farmer_id, product_name, and price are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        bidders = farmer_price.bidders
        current_price = farmer_price.current_price

        # 1) Prevent duplicate bidding for same product
        if farmer_id in bidders and product_name in bidders[farmer_id]:
            return Response(
                {"error": f"Farmer {farmer_id} already placed a bid for {product_name}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2) Update bidders
        if farmer_id not in bidders:
            bidders[farmer_id] = {}

        bidders[farmer_id][product_name] = price

        # 3) Update current_price (list of prices for each product)
        if product_name not in current_price:
            current_price[product_name] = []

        current_price[product_name].append(price)

        # Save changes
        farmer_price.bidders = bidders
        farmer_price.current_price = current_price
        farmer_price.save()

        return Response(farmerPricingSerializer(farmer_price).data, status=status.HTTP_200_OK)

# UpdateAveragePriceView
class UpdateAveragePriceView(APIView):

    def put(self, request):
        """
        PUT API:
        1. Fetch last 10 farmer_pricing records.
        2. For each product, fetch latest MSP price of the same zone.
        3. Use custom algorithm to calculate new price.
        4. Update farmer_pricing.current_price accordingly.
        """
        try:
            # Get last 10 records
            last_records = farmer_pricing.objects.order_by("-created_at")[:10]

            if not last_records:
                return Response(
                    {"error": "No farmer pricing records found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            for record in last_records:
                current_data = record.current_price
                zone = record.zone

                for product_name, price_list in current_data.items():

                    # If current_data has list of prices, else convert single price into list
                    if not isinstance(price_list, list):
                        price_list = [price_list]

                    # Fetch the latest MSP record for the same zone
                    latest_msp_record = MSP.objects.filter(zone=zone).order_by("-created_at").first()
                    if not latest_msp_record:
                        # If MSP not available, fallback to farmer price average
                        final_price = statistics.mean(price_list)
                    else:
                        # Get MSP price for the product (default 0 if not present)
                        msp_price = latest_msp_record.current_price.get(product_name, 0)
                        final_price = self.calculate_price(price_list, msp_price)

                    # Update final price in farmer pricing
                    current_data[product_name] = final_price

                # Save updated record
                record.current_price = current_data
                record.save()

            return Response(
                {"message": "Prices updated successfully"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # -------------------------
    # NEW CUSTOM PRICING ALGORITHM
    # -------------------------
    def calculate_price(self, farmer_prices, msp_price):
        """
        Algorithm for price calculation:
        - If MSP price exists, give it 60% weight.
        - Give farmer average price 40% weight.
        - If farmer avg < MSP * 0.7 → push price towards MSP minimum.
        - If farmer avg > MSP * 1.5 → restrict max price to MSP * 1.5 cap.
        """
        farmer_avg = statistics.mean(farmer_prices)

        # Case 1: No MSP available → use farmer average
        if msp_price == 0:
            return round(farmer_avg, 2)

        # Weighted average (60% MSP + 40% farmer avg)
        weighted_price = (0.6 * msp_price) + (0.4 * farmer_avg)

        # Add lower bound: if farmer prices are much lower than MSP, keep at least 70% of MSP
        if weighted_price < 0.7 * msp_price:
            weighted_price = 0.7 * msp_price

        # Add upper bound: if farmer prices are too high, cap at 1.5x MSP
        if weighted_price > 1.5 * msp_price:
            weighted_price = 1.5 * msp_price

        return round(weighted_price, 2)

#GetSessionView
class GetSessionView(APIView):
    def get(self, request):
        # Get zone from query params
        zone = request.query_params.get("zone")
        if not zone:
            return Response({"error": "zone is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            zone = int(zone)
        except ValueError:
            return Response({"error": "zone must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch latest 10 active sessions for the given zone
        sessions = (
            farmer_pricing.objects.filter(zone=zone, is_active=True)
            .order_by("-created_at")[:10]
            .values("id", "zone", "created_at", "is_active")  # Fetch only required fields
        )
        return Response(list(sessions), status=status.HTTP_200_OK)

class GetLastClosedSessionView(APIView):
    def get(self, request):
        # Get zone from query params
        zone = request.query_params.get("zone")
        if not zone:
            return Response({"error": "zone is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            zone = int(zone)
        except ValueError:
            return Response({"error": "zone must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the latest session where is_active=False
        session = (
            farmer_pricing.objects.filter(zone=zone, is_active=False)
            .order_by("-created_at")
            .values("id", "zone","current_price", "created_at", "is_active")
            .first()  # Get only one latest session
        )

        # If no session found
        if not session:
            return Response({"message": "No closed session found for this zone"}, status=status.HTTP_404_NOT_FOUND)

        return Response(session, status=status.HTTP_200_OK)
        

