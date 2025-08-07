from .send_private_message import private_message_handler

def register_admin_handlers(app):
    app.add_handler(private_message_handler)