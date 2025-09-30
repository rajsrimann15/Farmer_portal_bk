from jose import jwt, JWTError
from fastapi import HTTPException
from pathlib import Path

# Load the public key once
PUBLIC_KEY_PATH = Path("public.pem")
PUBLIC_KEY = PUBLIC_KEY_PATH.read_text()

ALGORITHM = "RS256"

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
        return payload  # You can return claims if needed (like user_id, role)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
