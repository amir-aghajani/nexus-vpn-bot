from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, filters, MessageHandler

from config import settings
from database import users_db
from keyboards import get_start_keyboard


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        await update.message.reply_text(
            "این ربات فقط در چت های خصوصی قابل استفاده است. لطفاً به صورت DM با ربات صحبت کنید."
        )
        return ConversationHandler.END

    user_id = update.message.chat_id
    is_admin = True if user_id in settings.telegram_bot_admin_ids else False

    if not users_db.exists(user_id):
        users_db.create(user_id)

    if is_admin:
        welcome_message = (
                "👋 سلام مدیر عزیز! به پنل مدیریتی ربات " +
                settings.telegram_bot_name +
                " خوش آمدید!\n\n"
                "🔧 لطفاً از منوی زیر برای مدیریت کاربران و تنظیمات ربات استفاده کنید."
        )
    else:
        welcome_message = (
                "🌟 به ربات " + settings.telegram_bot_name +
                " خوش آمدید!\n\n"
                "🚀 ما اینجا هستیم تا سریع‌ترین و بی‌نقص‌ترین دسترسی به شبکه جهانی را برای شما به ارمغان بیاوریم.\n\n"
                "✨ بدون هیچ محدودیت و اختلالی، تجربه‌ای بی‌نظیر در دنیای مجازی را با ما تجربه کنید\n\n"
                f"🔗 | @{settings.telegram_bot_id}"
        )

    await update.message.reply_text(
        text=welcome_message,
        reply_markup=get_start_keyboard(is_admin=is_admin),
        reply_to_message_id=update.message.message_id,
    )

    return ConversationHandler.END


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


async def return_to_main_menu_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    is_admin = True if update.effective_user.id in settings.telegram_bot_admin_ids else False

    context.user_data.pop('latestInlineConversationMessageId', None)
    context.user_data.pop('buyPhase', None)

    await query.edit_message_text(
        text=
        "🏠 شما به منو اصلی بازگشتید 🏠\n\n"
        "🌟 چه کاری می‌توانم برای شما انجام دهم؟ 🤖",
        reply_markup=get_start_keyboard(is_admin=is_admin),
    )

    return ConversationHandler.END


async def non_funcitoning_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer('این دکمه قرار نیست کاری انجام بده :)')


return_to_main_menu_filter = filters.Regex(r'^↩️ بازگشت به منوی اصلی$')
start_command_handler = CommandHandler("start", start_command)
return_to_main_menu_handler = MessageHandler(filters.TEXT & return_to_main_menu_filter, return_to_main_menu)
return_to_main_menu_inline_handler = CallbackQueryHandler(return_to_main_menu_inline, pattern=r'^returnToMainMenu')
non_functioning_query_handler = CallbackQueryHandler(non_funcitoning_button_handler, pattern=r'^noneFunctioningButton')
