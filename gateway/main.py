import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
import httpx
from jwt_utils import verify_jwt_token
from decouple import config
from fastapi.middleware.cors import CORSMiddleware
from mongo_logger import log_request



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","*"],  # Or ["*"] for dev only
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers (Authorization, Content-Type, etc.)
)

# Service endpoints
USER_SERVICE = config('USER_SERVICE')
TRANSPORT_SERVICE = config('TRANSPORT_SERVICE')
ECOM_SERVICE = config('ECOM_SERVICE')
AUCTION_SERVICE = config('AUCTION_SERVICE')
PRICING_SERVICE = config('AUCTION_SERVICE')




# Public auction endpoints (whitelist)
PUBLIC_AUCTION_ENDPOINTS = [
    "/zone/",
    "/price-trend/",
    "/health/"
]

def is_public_auction_path(path: str) -> bool:
    return any(path.startswith(p.strip("/")) for p in PUBLIC_AUCTION_ENDPOINTS)


# ---------- USER SERVICE PROXY ----------
@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_user_service(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        try:
            # Prepare the request
            body = await request.body()
            url = f"{USER_SERVICE}/api/users/{path}"
            headers = {
                k: v for k, v in request.headers.items() 
                if k.lower() not in ["host", "content-length"]
            }
            headers.setdefault("User-Agent", "API-Gateway/1.0")

            # Forward the request
            response = await client.request(
                request.method.lower(),
                url,
                headers=headers,
                content=body,
                timeout=30.0  # Important timeout
            )

             
            #Log to Cassandra
            log_request(
                service="USER_SERVICE",
                method=request.method,
                path=path,
                req_headers=headers,
                status_code=response.status_code
            )

            # Process the response
            content_type = response.headers.get("content-type", "").lower()
            
            # Debug logging (optional)
            print(f"Proxied to {url} | Status: {response.status_code} | Type: {content_type}")

            # Handle JSON responses
            if "application/json" in content_type:
                try:
                    return JSONResponse(
                        content=response.json(),
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    print(f"JSON parse error: {e} | Response: {response.text[:200]}...")
                    # Fallback to raw response if JSON parsing fails
                    return Response(
                        content=response.content,
                        status_code=response.status_code,
                        media_type=content_type,
                        headers=dict(response.headers)
                    )

            # Handle all other response types
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=content_type or "application/octet-stream",
                headers=dict(response.headers)
            )

        except httpx.TimeoutException:
            return JSONResponse(
                content={"error": "Upstream service timeout"},
                status_code=504
            )
        except httpx.RequestError as e:
            print(f"Request error: {str(e)}")
            return JSONResponse(
                content={"error": f"Upstream connection error: {str(e)}"},
                status_code=502
            )
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JSONResponse(
                content={"error": "Internal gateway error"},
                status_code=500
            )


# ---------- TRANSPORT SERVICE PROXY (JWT Required) ----------
@app.api_route("/api/transport/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_transport_service(path: str, request: Request):
    # 1. Get token from Authorization header
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ")[1]

    # 2. Validate and decode token
    payload = verify_jwt_token(token)
    user_id = payload.get("user_id")
    role = payload.get("role")

    if not user_id or not role:
        raise HTTPException(status_code=401, detail="Invalid token claims")

    # 3. Forward request
    async with httpx.AsyncClient() as client:
        try:
            body = await request.body()
            url = f"{TRANSPORT_SERVICE}/api/transport/{path}"

            # Copy headers except problematic ones
            headers = {
                k: v for k, v in request.headers.items()
                if k.lower() not in ["host", "content-length", "authorization"]
            }
            headers.setdefault("User-Agent", "API-Gateway/1.0")

            # 4. Add user claims to forwarded headers
            headers["X-User-Id"] = str(user_id)
            headers["X-User-Role"] = role

            if request.url.query:
                url += f"?{request.url.query}"

            # Forward request to transport service
            response = await client.request(
                request.method.lower(),
                url,
                headers=headers,
                content=body,
                timeout=30.0
            )

            #Logs
            log_request(
                service="USER_SERVICE",
                method=request.method,
                path=path,
                req_headers=headers,
                status_code=response.status_code
            )

            content_type = response.headers.get("content-type", "").lower()
            if "application/json" in content_type:
                try:
                    return JSONResponse(
                        content=response.json(),
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return Response(
                        content=response.content,
                        status_code=response.status_code,
                        media_type=content_type,
                        headers=dict(response.headers)
                    )
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=content_type or "application/octet-stream",
                headers=dict(response.headers)
            )

        except httpx.TimeoutException:
            return JSONResponse({"error": "Upstream service timeout"}, status_code=504)
        except httpx.RequestError as e:
            return JSONResponse({"error": f"Upstream connection error: {str(e)}"}, status_code=502)
        except Exception:
            return JSONResponse({"error": "Internal gateway error"}, status_code=500)



# ---------- ECOM SERVICE PROXY (JWT Required) ----------
@app.api_route("/api/ecom/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_ecom_service(path: str, request: Request):
    # 1. Get token from Authorization header
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ")[1]

    # 2. Validate and decode token
    payload = verify_jwt_token(token)
    user_id = payload.get("user_id")
    role = payload.get("role")

    if not user_id or not role:
        raise HTTPException(status_code=401, detail="Invalid token claims")

    # 3. Forward request
    async with httpx.AsyncClient() as client:
        try:
            body = await request.body()
            url = f"{ECOM_SERVICE}/api/ecom/{path}"

            # Copy headers except problematic ones
            headers = {
                k: v for k, v in request.headers.items()
                if k.lower() not in ["host", "content-length", "authorization"]
            }
            headers.setdefault("User-Agent", "API-Gateway/1.0")

            # 4. Add user claims to forwarded headers
            headers["X-User-Id"] = str(user_id)
            headers["X-User-Role"] = role

            if request.url.query:
                url += f"?{request.url.query}"

            # Forward request to ecom service
            response = await client.request(
                request.method.lower(),
                url,
                headers=headers,
                content=body,
                timeout=30.0
            )

            #Logs
            log_request(
                service="USER_SERVICE",
                method=request.method,
                path=path,
                req_headers=headers,
                status_code=response.status_code
            )

            content_type = response.headers.get("content-type", "").lower()
            if "application/json" in content_type:
                try:
                    return JSONResponse(
                        content=response.json(),
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return Response(
                        content=response.content,
                        status_code=response.status_code,
                        media_type=content_type,
                        headers=dict(response.headers)
                    )
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=content_type or "application/octet-stream",
                headers=dict(response.headers)
            )

        except httpx.TimeoutException:
            return JSONResponse({"error": "Upstream service timeout"}, status_code=504)
        except httpx.RequestError as e:
            return JSONResponse({"error": f"Upstream connection error: {str(e)}"}, status_code=502)
        except Exception:
            return JSONResponse({"error": "Internal gateway error"}, status_code=500)


# ---------- AUCTION SERVICE PROXY ------------
@app.api_route("/api/auction/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_auction_service(path: str, request: Request):
    user_id = None
    role = None

    # Only check token if path is not public
    if not is_public_auction_path(path):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing token")
        token = auth.split(" ")[1]

        # Validate and decode token
        payload = verify_jwt_token(token)
        user_id = payload.get("user_id")
        role = payload.get("role")

        if not user_id or not role:
            raise HTTPException(status_code=401, detail="Invalid token claims")

    # Forward request to auction service
    async with httpx.AsyncClient() as client:
        try:
            body = await request.body()
            url = f"{AUCTION_SERVICE}/api/auction/{path}"

            # Copy headers except problematic ones
            headers = {
                k: v for k, v in request.headers.items()
                if k.lower() not in ["host", "content-length", "authorization"]
            }
            headers.setdefault("User-Agent", "API-Gateway/1.0")

            # If authenticated, add user claims
            if user_id and role:
                headers["X-User-Id"] = str(user_id)
                headers["X-User-Role"] = role

            if request.url.query:
                url += f"?{request.url.query}"

            response = await client.request(
                request.method.lower(),
                url,
                headers=headers,
                content=body,
                timeout=30.0
            )

            #Logs
            log_request(
                service="USER_SERVICE",
                method=request.method,
                path=path,
                req_headers=headers,
                status_code=response.status_code
            )

            content_type = response.headers.get("content-type", "").lower()
            if "application/json" in content_type:
                try:
                    return JSONResponse(
                        content=response.json(),
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return Response(
                        content=response.content,
                        status_code=response.status_code,
                        media_type=content_type,
                        headers=dict(response.headers)
                    )
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=content_type or "application/octet-stream",
                headers=dict(response.headers)
            )

        except httpx.TimeoutException:
            return JSONResponse({"error": "Upstream service timeout"}, status_code=504)
        except httpx.RequestError as e:
            return JSONResponse({"error": f"Upstream connection error: {str(e)}"}, status_code=502)
        except Exception:
            return JSONResponse({"error": "Internal gateway error"}, status_code=500)


# ---------- PRICING SERVICE PROXY ------------
@app.api_route("/api/pricing/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_pricing_service(path: str, request: Request):
    user_id = None
    role = None

    # Only check token if path is not public
    if not is_public_auction_path(path):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing token")
        token = auth.split(" ")[1]

        # Validate and decode token
        payload = verify_jwt_token(token)
        user_id = payload.get("user_id")
        role = payload.get("role")

        if not user_id or not role:
            raise HTTPException(status_code=401, detail="Invalid token claims")

    # Forward request to pricing service
    async with httpx.AsyncClient() as client:
        try:
            body = await request.body()
            url = f"{PRICING_SERVICE}/api/pricing/{path}"

            # Copy headers except problematic ones
            headers = {
                k: v for k, v in request.headers.items()
                if k.lower() not in ["host", "content-length", "authorization"]
            }
            headers.setdefault("User-Agent", "API-Gateway/1.0")

            # If authenticated, add user claims
            if user_id and role:
                headers["X-User-Id"] = str(user_id)
                headers["X-User-Role"] = role

            # Preserve query params if present
            if request.url.query:
                url += f"?{request.url.query}"

            response = await client.request(
                request.method.lower(),
                url,
                headers=headers,
                content=body,
                timeout=30.0
            )

            # Logs
            log_request(
                service="PRICING_SERVICE",
                method=request.method,
                path=path,
                req_headers=headers,
                status_code=response.status_code
            )

            # Handle JSON and non-JSON responses
            content_type = response.headers.get("content-type", "").lower()
            if "application/json" in content_type:
                try:
                    return JSONResponse(
                        content=response.json(),
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return Response(
                        content=response.content,
                        status_code=response.status_code,
                        media_type=content_type,
                        headers=dict(response.headers)
                    )
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type=content_type or "application/octet-stream",
                headers=dict(response.headers)
            )

        except httpx.TimeoutException:
            return JSONResponse({"error": "Upstream service timeout"}, status_code=504)
        except httpx.RequestError as e:
            return JSONResponse({"error": f"Upstream connection error: {str(e)}"}, status_code=502)
        except Exception:
            return JSONResponse({"error": "Internal gateway error"}, status_code=500)
