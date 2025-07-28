from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from .models import FarmerLog, ConsumerLog, TransporterLog

@api_view(['POST'])
def log_request(request):
    data = request.data
    user_type = data.get('user_type')  # farmer, consumer, transporter
    log_data = {
        'user_id': data.get('user_id'),
        'method': data.get('method'),
        'route': data.get('route'),
        'timestamp': datetime.now()
    }

    if user_type == 'farmer':
        FarmerLog.create(**log_data)
    elif user_type == 'consumer':
        ConsumerLog.create(**log_data)
    elif user_type == 'transporter':
        TransporterLog.create(**log_data)

    return Response({"status": "logged"})
