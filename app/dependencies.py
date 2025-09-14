import os
from fastapi import Header, HTTPException

API_KEY = os.getenv("API_KEY", "secret")


def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
