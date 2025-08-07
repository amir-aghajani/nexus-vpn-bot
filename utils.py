from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from config import settings
from keyboards import get_start_keyboard


async def return_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db_data):
    is_admin = True if update.message.chat_id in settings.telegram_bot_admin_ids else False
    await update.message.reply_text(
        text=
        "🏠 شما به منو اصلی بازگشتید 🏠\n\n"
        "🌟 چه کاری می‌توانم برای شما انجام دهم؟ 🤖",
        reply_markup=get_start_keyboard(is_admin=is_admin)
    )

    return ConversationHandler.END
