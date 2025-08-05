from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from config import settings
from commands.start import start_command



app = ApplicationBuilder().token(settings.telegram_bot_token).build()

app.add_handler(CommandHandler("start", start_command))

app.run_polling()