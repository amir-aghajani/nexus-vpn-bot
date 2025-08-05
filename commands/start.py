from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from keyboards.start import get_keyboard
from config import settings


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    is_admin = True if update.message.chat_id in settings.telegram_bot_admin_ids else False
    print(is_admin)
    reply_markup = get_keyboard()
    await update.message.reply_text(
        "🌟 به عرصه ارتقای تجربه اینترنتی خود با سرویس‌های V2RAY و کاهش پینگ خوش آمدید!\n\n"
        "🚀 ما اینجا هستیم تا سریع‌ترین و بی‌نقص‌ترین دسترسی به شبکه جهانی را برای شما به ارمغان بیاوریم.\n\n"
        "✨ بدون هیچ محدودیت و اختلالی، تجربه‌ای بی‌نظیر در دنیای مجازی را با ما تجربه کنید\n\n"
        "🔗 | @AbSardKonBot",
        reply_markup=reply_markup
    )

    return ConversationHandler.END
