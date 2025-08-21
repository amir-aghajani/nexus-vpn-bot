from fastapi import APIRouter

from api.routers.auth.login import router as login_router

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

router.include_router(login_router)
