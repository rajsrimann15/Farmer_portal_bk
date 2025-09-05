import requests
from datetime import datetime, timedelta
from decouple import config

SECRET_API_KEY = config('SECRET_API_KEY')
USER_SERVICE=config('USER_SERVICE')
ECOM_SERVICE=config('ECOM_SERVICE')

USER_SERVICE_URL = f"https://{USER_SERVICE}/api/users/farmer/stats/"
ECOM_SERVICE_URL = f"https://{ECOM_SERVICE}/api/ecom/products/stats/"

def fetch_new_farmers():
    """Fetch new farmer count from user_service"""
    last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    headers = {
        "X-SECRET-KEY": SECRET_API_KEY
    }
    try:
        response = requests.get(
            f"{USER_SERVICE_URL}?from={last_week}",
            headers=headers
        )
        return response.json().get("new_farmers_last_week", 0)
    except:
        return 0

def fetch_products_posted():
    """Fetch products posted count from ecom_service"""
    last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    headers = {
        "X-SECRET-KEY": SECRET_API_KEY
    }
    try:
        response = requests.get(
            f"{ECOM_SERVICE_URL}?from={last_week}",
            headers=headers
        )
        return response.json().get("products_posted_last_week", 0)
    except:
        return 0
