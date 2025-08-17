from fastapi import FastAPI

from api.routers.auth import router as auth_router


def register_routers(app: FastAPI):
    app.include_router(auth_router)
