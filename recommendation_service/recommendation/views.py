from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import fetch_new_farmers, fetch_products_posted
from .ai_utils import generate_recommendation

class FarmerRecommendationView(APIView):
    def get(self, request):
        new_farmers = fetch_new_farmers()
        products_posted = fetch_products_posted()
        ai_suggestion = generate_recommendation(new_farmers, products_posted)

        data = {
            "new_farmers": new_farmers,
            "products_posted": products_posted,
            "ai_suggestion": ai_suggestion
        }
        return Response(data)
