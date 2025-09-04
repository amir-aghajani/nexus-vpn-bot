from fastapi import APIRouter

from web.routers.auth.login import router as login_router

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

router.include_router(login_router)
