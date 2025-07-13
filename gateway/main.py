from fastapi import FastAPI, HTTPException, Request
import httpx
from jwt_utils import verify_jwt_token

app = FastAPI()

# Service endpoints
USER_SERVICE = "http://localhost:8000"
TRANSPORT_SERVICE = "http://localhost:8002"
ECOM_SERVICE = "http://localhost:8004"
AUCTION_SERVICE = "http://localhost:8006"

# Public auction endpoints (whitelist)
PUBLIC_AUCTION_ENDPOINTS = [
    "/zone/",
    "/price-trend/"
]

def is_public_auction_path(path: str) -> bool:
    return any(path.startswith(p.strip("/")) for p in PUBLIC_AUCTION_ENDPOINTS)


# ---------- USER SERVICE PROXY ----------
@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_user_service(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        body = await request.body()
        url = f"{USER_SERVICE}/api/users/{path}"
        headers = dict(request.headers)
        method = request.method.lower()
        response = await client.request(method, url, headers=headers, content=body)
        return response.json()


# ---------- TRANSPORT SERVICE PROXY (JWT Required) ----------
@app.api_route("/api/transport/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_transport_service(path: str, request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ")[1]
    verify_jwt_token(token)

    async with httpx.AsyncClient() as client:
        body = await request.body()
        headers = dict(request.headers)
        query_string = request.url.query
        url = f"{TRANSPORT_SERVICE}/api/transport/{path}"
        if query_string:
            url += f"?{query_string}"

        method = request.method.lower()
        response = await client.request(method, url, headers=headers, content=body)
        return response.json()


# ---------- AUCTION SERVICE PROXY (Some Routes Open) ----------
@app.api_route("/api/auction/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_auction_service(path: str, request: Request):
    # Only protect routes that are NOT public
    if not is_public_auction_path(path):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing token")
        token = auth.split(" ")[1]
        verify_jwt_token(token)

    async with httpx.AsyncClient() as client:
        body = await request.body()
        headers = dict(request.headers)
        query_string = request.url.query
        url = f"{AUCTION_SERVICE}/api/auction/{path}"
        if query_string:
            url += f"?{query_string}"

        method = request.method.lower()
        response = await client.request(method, url, headers=headers, content=body)
        return response.json()


# ---------- ECOM SERVICE PROXY (JWT Required) ----------
@app.api_route("/api/ecom/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_ecom_service(path: str, request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ")[1]
    verify_jwt_token(token)

    async with httpx.AsyncClient() as client:
        body = await request.body()
        headers = dict(request.headers)
        query_string = request.url.query
        url = f"{ECOM_SERVICE}/api/ecom/{path}"
        if query_string:
            url += f"?{query_string}"

        method = request.method.lower()
        response = await client.request(method, url, headers=headers, content=body)
        return response.json()
