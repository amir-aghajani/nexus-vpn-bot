from .manage_user_status import manage_user_status_handler
from .send_private_message import private_message_handler


def register_admin_handlers(app):
    app.add_handler(private_message_handler)
    app.add_handler(manage_user_status_handler)
