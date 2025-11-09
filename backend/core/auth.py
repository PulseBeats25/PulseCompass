import os
from typing import Dict
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError

security = HTTPBearer()

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    token = creds.credentials
    secret = os.getenv("SUPABASE_JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="Missing SUPABASE_JWT_SECRET")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
