from telegram.ext import ApplicationBuilder, CommandHandler

from commands.start import start_command
from config import settings
from handlers import register_handlers

app = ApplicationBuilder().token(settings.telegram_bot_token).build()

app.add_handler(CommandHandler("start", start_command))
register_handlers(app)

app.run_polling()
