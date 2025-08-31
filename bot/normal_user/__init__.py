from .buy_subscription import buy_subscription_callback_handler
from .wallet import top_up_wallet_handler


def register_user_handlers(app):
    app.add_handler(top_up_wallet_handler)
    app.add_handler(buy_subscription_callback_handler)
