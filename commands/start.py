from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from config import settings
from database import users_db
from keyboards import get_start_keyboard


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.chat.type != "private":
        await update.message.reply_text(
            "این ربات فقط در چت های خصوصی قابل استفاده است. لطفاً به صورت DM با ربات صحبت کنید."
        )
        return ConversationHandler.END

    user_id = update.message.chat_id
    is_admin = True if update.message.chat_id in settings.telegram_bot_admin_ids else False

    if not users_db.exists(user_id):
        users_db.create(user_id)

    await update.message.reply_text(
        text=
        "🌟 به عرصه ارتقای تجربه اینترنتی خود با سرویس‌های V2RAY و کاهش پینگ خوش آمدید!\n\n"
        "🚀 ما اینجا هستیم تا سریع‌ترین و بی‌نقص‌ترین دسترسی به شبکه جهانی را برای شما به ارمغان بیاوریم.\n\n"
        "✨ بدون هیچ محدودیت و اختلالی، تجربه‌ای بی‌نظیر در دنیای مجازی را با ما تجربه کنید\n\n"
        f"🔗 | @{settings.telegram_bot_id}",
        reply_markup=get_start_keyboard(is_admin=is_admin),
    )

    return ConversationHandler.END
