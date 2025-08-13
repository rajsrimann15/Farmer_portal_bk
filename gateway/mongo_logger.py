# mongo_logger.py
import os
import uuid
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Load MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "api_logs")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "api_requests")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]

def log_request(service, method, path, req_headers,status_code):
    try:
        doc = {
            "_id": str(uuid.uuid4()),
            "service": service,
            "method": method,
            "path": path,
            "req_headers": str(req_headers)[:5000],
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        collection.insert_one(doc)
        print(f"Logged request for {service} {method} {path}")
    except Exception as e:
        print(f"Failed to log request: {e}")
