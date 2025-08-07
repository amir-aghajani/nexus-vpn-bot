from telegram import Update
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from database import users_db
from keyboards import get_return_to_main_menu_keyboard
from utils import return_to_main_menu

ENTER_USER_ID, ENTER_MESSAGE = range(2)


async def private_message_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await update.message.reply_text(
        "لطفاً شناسه کاربری (User ID) کاربری که می‌خواهید پیام خصوصی ارسال کنید را وارد کنید:",
        reply_to_message_id=query.message.message_id
    )

    return ENTER_USER_ID


async def user_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text(
            "شناسه کاربری نامعتبر است. لطفاً یک شناسه کاربری معتبر وارد کنید."
        )
        return ENTER_USER_ID

    if not users_db.exists(str(user_id)):
        await update.message.reply_text(
            text="کاربری با این شناسه وجود ندارد. لطفاً شناسه کاربری معتبر وارد کنید.",
            reply_to_message_id=update.message.message_id
        )

        return ENTER_USER_ID

    context.user_data["user_id"] = user_id

    await update.message.reply_text(
        f"لطفا پیام مورد نظر خود را ارسال کنید تا به کاربر ارسال شود",
        reply_to_message_id=update.message.message_id,
        reply_markup=get_return_to_main_menu_keyboard('من کیرم تو اون هدفگ')
    )

    return ENTER_MESSAGE


async def send_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "koskesh"
    )

    return ConversationHandler.END


private_message_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(private_message_entry, pattern=r"^admin:sendPrivateMessage")
    ],
    states={
        ENTER_USER_ID: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, private_message_entry),
        ],
        ENTER_MESSAGE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, send_message_handler),
        ]
    },
    fallbacks=[
        MessageHandler(filters.TEXT & filters.Regex(r'^🔙🏠 بازگشت به منوی اصلی 🏠🔙$'), return_to_main_menu)
    ]
)
