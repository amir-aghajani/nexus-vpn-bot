from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from config import settings
from keyboards import get_start_keyboard


async def return_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = True if update.message.chat_id in settings.telegram_bot_admin_ids else False

    delete_keyboard_message = await update.message.reply_text(
        text="لطفا صبر کنید...",
        reply_markup=ReplyKeyboardRemove(),
    )
    await delete_keyboard_message.delete()
    await update.message.reply_text(
        text=
        "🏠 شما به منو اصلی بازگشتید 🏠\n\n"
        "🌟 چه کاری می‌توانم برای شما انجام دهم؟ 🤖",
        reply_markup=get_start_keyboard(is_admin=is_admin),
        reply_to_message_id=update.message.message_id
    )

    return ConversationHandler.END
