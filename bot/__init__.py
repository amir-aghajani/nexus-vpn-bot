import asyncio
import threading
from warnings import filterwarnings

from telegram.ext import ApplicationBuilder, PicklePersistence
from telegram.warnings import PTBUserWarning

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

from config import settings
from handlers import register_handlers
from .global_handlers import error_handler
from handlers.globals import (
    non_functioning_query_handler,
    return_to_main_menu_handler,
    return_to_main_menu_inline_handler,
    start_command_handler,
)

persistence = PicklePersistence(
    filepath="data/bot_data.pkl",
    update_interval=5,
)

tg_app = ApplicationBuilder().persistence(persistence).token(settings.telegram_bot_token).build()
register_handlers(tg_app)
tg_app.add_handler(start_command_handler)
tg_app.add_handler(return_to_main_menu_handler)
tg_app.add_handler(return_to_main_menu_inline_handler)
tg_app.add_handler(non_functioning_query_handler)
tg_app.add_error_handler(error_handler)


def _bot_worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _run():
        await tg_app.initialize()
        await tg_app.start()
        await tg_app.updater.start_polling()

    loop.create_task(_run())
    try:
        loop.run_forever()
    finally:
        try:
            loop.run_until_complete(tg_app.stop())
            loop.run_until_complete(tg_app.shutdown())
        except Exception:
            pass
        loop.close()


def start_bot_in_background():
    t = threading.Thread(target=_bot_worker, name="telegram-bot", daemon=True)
    t.start()
    return t
