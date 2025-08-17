import hmac
import os
import time

import jwt
from fastapi import APIRouter, HTTPException, status

from api.schemas.auth import LoginModel, TokenModel
from data import json_storage

router = APIRouter(
    prefix="/auth"
)

# --- Config ---
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALG = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * (json_storage.get("accessTokenExpireMinutes") or 60)

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "changeme")


# --- Helpers ---
def verify_admin_creds(username: str, password: str) -> bool:
    return (
            hmac.compare_digest(username, ADMIN_USER)
            and hmac.compare_digest(password, ADMIN_PASS)
    )


def create_access_token(sub: str, expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS) -> str:
    now = int(time.time())
    payload = {"sub": sub, "iat": now, "exp": now + expires_in}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


@router.post("/login", response_model=TokenModel)
async def login(user_credentials: LoginModel):
    if not verify_admin_creds(user_credentials.username, user_credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(sub=user_credentials.username)
    return TokenModel(accessToken=token)
