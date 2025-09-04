import hmac
import time

import jwt
from fastapi import APIRouter, HTTPException, status

from web.schemas.auth import LoginModel, TokenModel
from data import json_storage

router = APIRouter(
    prefix="/login"
)

# --- Config ---
JWT_SECRET = json_storage.get('jwtSecret')
JWT_ALG = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * (json_storage.get("accessTokenExpireMinutes") or 60)

ADMIN_USER = json_storage.get("botPanelUsername") or "admin"
ADMIN_PASS = json_storage.get("botPanelPassword") or "1234"


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


@router.post("/", response_model=TokenModel)
async def login(user_credentials: LoginModel):
    if not verify_admin_creds(user_credentials.username, user_credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(sub=user_credentials.username)
    return TokenModel(accessToken=token)
