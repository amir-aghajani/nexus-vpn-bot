from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, filters, MessageHandler

from handlers.globals import return_to_main_menu_filter
from keyboards import get_return_to_main_menu_keyboard

ENTER_SERVER_NAME, ENTER_SERVER_LIMIT, ENTER_SERVER_EMOJI, ENTER_PANEL_URL, ENTER_PANEL_USERNAME, ENTER_PANEL_PASSWORD = range(6)


async def handler_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.delete_message()
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='📦 افزودن سرور ' +
             '3x-ui\n\n\n'
             '▪️ مرحله اول:\n\n'
             '👤 لطفاً نام سرور را وارد کنید\n\n'
             '❗ توجه کنید ایموجی سرور در مراحل بعد از شما پرسیده خواهد شد!',
        reply_markup=get_return_to_main_menu_keyboard('نام سرور')
    )
    await query.answer()

    return ENTER_SERVER_NAME


async def server_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    context.user_data['user_id'] = message.text

    await message.reply_text(
        text='✅ نام سرور با موفقیت ثبت شد.\n\n'
             '▪️ظرفیت تعداد ساخت کانفیگ رو برای سرورت مشخص کن ( عدد باشه )',
        reply_to_message_id=message.message_id,
        reply_markup=get_return_to_main_menu_keyboard('محدودیت سرور')
    )

    return ENTER_SERVER_LIMIT


async def server_limit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


new_sanaei_3x_ui_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(handler_entry, pattern=r'^admin:addServer:3X-UI')
    ],
    states={
        ENTER_SERVER_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND & ~return_to_main_menu_filter, server_name_handler),
        ],
        ENTER_SERVER_LIMIT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND & ~return_to_main_menu_filter, server_limit_handler)
        ]
    },
    fallbacks=[],
    allow_reentry=True,
)
