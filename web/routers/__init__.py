from fastapi import FastAPI

from web.routers.auth import router as auth_router
from web.routers.backup import router as backups_router
from web.routers.categories import router as categories_router
from web.routers.payment_methods import router as payment_methods_router
from web.routers.plans import router as plans_router
from web.routers.servers import router as servers_router
from web.routers.main import router as index_router


def register_routers(app: FastAPI):
    app.include_router(index_router)
    app.include_router(auth_router)
    app.include_router(backups_router)
    app.include_router(servers_router)
    app.include_router(categories_router)
    app.include_router(plans_router)
    app.include_router(payment_methods_router)
