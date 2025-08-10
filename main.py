from telegram.ext import ApplicationBuilder

from config import settings
from handlers import register_handlers
from handlers.globals import start_command_handler

app = ApplicationBuilder().token(settings.telegram_bot_token).build()

register_handlers(app)
app.add_handler(start_command_handler)

app.run_polling()
