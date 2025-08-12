from telegram.ext import ApplicationBuilder

from config import settings
from handlers import register_handlers
from handlers.globals import non_functioning_query_handler, return_to_main_menu_handler, return_to_main_menu_inline_handler, start_command_handler

app = ApplicationBuilder().token(settings.telegram_bot_token).build()

register_handlers(app)
app.add_handler(start_command_handler)
app.add_handler(return_to_main_menu_handler)
app.add_handler(return_to_main_menu_inline_handler)
app.add_handler(non_functioning_query_handler)

app.run_polling()
