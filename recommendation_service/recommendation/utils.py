import requests
from datetime import datetime, timedelta

USER_SERVICE_URL = "https://farmer-portal-user-service.onrender.com/api/farmer/stats/"
ECOM_SERVICE_URL = "https://farmer-portal-ecom-service.onrender.com/api/products/stats/"

def fetch_new_farmers():
    """Fetch new farmer count from user_service"""
    last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    try:
        response = requests.get(f"{USER_SERVICE_URL}?from={last_week}")
        return response.json().get("new_farmers", 0)
    except:
        return 0

def fetch_products_posted():
    """Fetch products posted count from ecom_service"""
    last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    try:
        response = requests.get(f"{ECOM_SERVICE_URL}?from={last_week}")
        return response.json().get("products_posted", 0)
    except:
        return 0
