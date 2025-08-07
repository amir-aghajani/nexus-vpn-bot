from .admin import register_admin_handlers


def register_handlers(app):
    register_admin_handlers(app)
