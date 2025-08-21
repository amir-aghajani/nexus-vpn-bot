from fastapi import FastAPI

from api.routers.auth import router as auth_router
from api.routers.categories import router as categories_router
from api.routers.servers import router as servers_router


def register_routers(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(servers_router)
    app.include_router(categories_router)
