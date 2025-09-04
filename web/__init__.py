from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from web.routers import register_routers

web_app = FastAPI(
    title="Nexus Admin API",
    description="API for Nexus administration and management",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")
web_app.mount("/static/", StaticFiles(directory="web/static"), name="static")

web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_routers(web_app)
