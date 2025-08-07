from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from commands.start import start_command
from config import settings
from handlers import register_handlers
from utils import return_to_main_menu

app = ApplicationBuilder().token(settings.telegram_bot_token).build()

app.add_handler(CommandHandler("start", start_command))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^↩️ بازگشت به منوی اصلی$'), return_to_main_menu))
register_handlers(app)

app.run_polling()
