from bot.normal_user import register_user_handlers
from .admin import register_admin_handlers


def register_handlers(app):
    register_user_handlers(app)
    register_admin_handlers(app)
