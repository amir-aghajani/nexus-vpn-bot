from telegram import Update
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from database import users_db
from keyboards import get_return_to_main_menu_keyboard
from utils import return_to_main_menu

ENTER_USER_ID, ENTER_MESSAGE = range(2)


async def private_message_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.delete_message()
    await context.bot.send_message(
        text='📞 لطفاً شناسه عددی (Numeric ID) کاربری که می‌خواهید پیام خصوصی ارسال کنید را وارد کنید',
        chat_id=query.message.chat.id,
        reply_markup=get_return_to_main_menu_keyboard('شناسه عددی کاربر')
    )
    await query.answer()

    return ENTER_USER_ID


async def user_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text(
            "شناسه کاربری نامعتبر است. لطفاً یک شناسه کاربری معتبر وارد کنید.",
            reply_markup=get_return_to_main_menu_keyboard('شناسه عددی کاربر'),
            reply_to_message_id=update.message.message_id
        )

        return ENTER_USER_ID

    if not users_db.exists(str(user_id)):
        await update.message.reply_text(
            text="کاربری با این شناسه وجود ندارد. لطفاً شناسه کاربری معتبر وارد کنید.",
            reply_markup=get_return_to_main_menu_keyboard('شناسه عددی کاربر'),
            reply_to_message_id=update.message.message_id
        )

        return ENTER_USER_ID

    context.user_data["user_id"] = user_id

    await update.message.reply_text(
        f"لطفا پیام مورد نظر خود را ارسال کنید تا به کاربر ارسال شود",
        reply_to_message_id=update.message.message_id,
        reply_markup=get_return_to_main_menu_keyboard('متن پیام مورد نظر')
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
            MessageHandler(filters.TEXT & ~filters.COMMAND, user_id_handler),
        ],
        ENTER_MESSAGE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, send_message_handler),
        ]
    },
    fallbacks=[],
    per_message=False,
    allow_reentry=True,
)
