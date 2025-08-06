from telegram.ext import ApplicationBuilder, CommandHandler

from commands.start import start_command
from config import settings

app = ApplicationBuilder().token(settings.telegram_bot_token).build()

app.add_handler(CommandHandler("start", start_command))

app.run_polling()
