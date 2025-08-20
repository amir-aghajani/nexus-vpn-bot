from .buy_subscription import buy_subscription_callback_handler


def register_user_handlers(app):
    app.add_handler(buy_subscription_callback_handler)
