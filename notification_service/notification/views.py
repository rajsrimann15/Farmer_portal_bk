from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import TransporterBooking, EcomOrderNotification
from .permissions import IsTransporter, IsFarmer
# ----------------------------------------------
# TRANSPORTER NOTIFICATIONS (TransporterBooking)    
# ----------------------------------------------    
class TransporterNotificationView(APIView):
    # GET /notifications/transport/
    
    permission_classes = [IsTransporter]
    def get(self, request):
        transporter_id = request.headers.get("X-User-Id")

        if not transporter_id:
            return Response({"error": "Transporter-ID header missing"},
                            status=status.HTTP_400_BAD_REQUEST)

        notifs = TransporterBooking.objects.filter(
            transporter_id=transporter_id,
            read=False
        ).order_by("-id")

        data = [
            {
                "id": n.id,
                "schedule_id": n.schedule_id,
                "from_place": n.from_place,
                "to_place": n.to_place,
                "weight": n.weight,
                "date": n.date,
                "total_cost": n.total_cost,
                "description": n.description,
                "read": n.read,
            }
            for n in notifs
        ]

        return Response(data)

    # POST /notifications/transport/mark-read/<id>/
    def post(self, request, id=None):
        
        try:
            notif = TransporterBooking.objects.get(id=id)
        except TransporterBooking.DoesNotExist:
            return Response({"error": "Notification not found"},
                            status=status.HTTP_404_NOT_FOUND)

        notif.read = True
        notif.save()
        return Response({"status": "marked as read"})

# ----------------------------------------------
# ECOM NOTIFICATIONS (EcomOrderNotification)
# ----------------------------------------------
class EcomNotificationView(APIView):
    permission_classes = [IsFarmer]

    # GET /notifications/ecom/unread/
    def get(self, request):
        farmer_id = request.headers.get("X-User-Id")

        if not farmer_id:
            return Response(
                {"error": "Farmer-ID header missing"},
                status=status.HTTP_400_BAD_REQUEST
            )

        notifs = EcomOrderNotification.objects.filter(
            farmer_id=farmer_id,
            read=False
        ).order_by("-id")

        data = [
            {
                "id": n.id,
                "order_id": n.order_id,
                "consumer_id": n.consumer_id,
                "farmer_id": n.farmer_id,
                "product": n.product,
                "quantity": n.quantity,
                "price": n.price,
                "date": n.date,
                "description": n.description,
                "read": n.read,
            }
            for n in notifs
        ]

        return Response(data)

    # POST /notifications/ecom/mark-read/<id>/
    def post(self, request, id=None):
        try:
            notif = EcomOrderNotification.objects.get(id=id)
        except EcomOrderNotification.DoesNotExist:
            return Response({"error": "Notification not found"},
                            status=status.HTTP_404_NOT_FOUND)

        notif.read = True
        notif.save()
        return Response({"status": "marked as read"})

