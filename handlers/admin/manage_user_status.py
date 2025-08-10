from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, filters, MessageHandler

from data import banned_users
from database import users_db
from keyboards import get_return_to_main_menu_keyboard
from .helpers import user_id_helper

ENTER_USER_ID = range(1)


async def manage_user_status_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split(':')
    context.user_data['action'] = data[1]

    if data[1] == 'banUser':
        text = '❌ مسدود کردن کابر'
    elif data[1] == 'unbanUser':
        text = '✅ آزاد کردن کاربر'

    await query.delete_message()
    await context.bot.send_message(
        text=f'{text}\n\n'
             '👤 لطفاً شناسه عددی (Numeric ID) کاربر را وارد کنید',
        chat_id=query.message.chat.id,
        reply_markup=get_return_to_main_menu_keyboard('شناسه عددی کاربر')
    )
    await query.answer()

    return ENTER_USER_ID


async def change_user_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.text
    if not await user_id_helper(update, user_id):
        return ENTER_USER_ID

    if context.user_data['action'] == 'banUser':
        text = f'❌ کاربر با شناسه {user_id} مسدود شد.'
    elif context.user_data['action'] == 'unbanUser':
        text = f'✅ کاربر با شناسه {user_id} آزاد شد.'

    confirmation = await update.message.reply_text(
        text='در حال تغییر وضعیت کاربر ...',
        reply_to_message_id=update.message.message_id
    )

    try:
        users_db.change_status(user_id, context.user_data['action'])
        banned_users.modify_user_status(user_id, context.user_data['action'])
        await confirmation.edit_text(text=text)
    except Exception as e:
        await confirmation.edit_text(
            text=
            '❌ مشکلی پیش آمده است ❌\n'
            f'```ErrorMessage\n{str(e)}```',
            parse_mode='MarkDownV2'
        )

    return ConversationHandler.END


manage_user_status_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(manage_user_status_entry, pattern=r'^admin:banUser|admin:unbanUser'),
    ],
    states={
        ENTER_USER_ID: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, change_user_status_handler)
        ],
    },
    fallbacks=[],
    allow_reentry=True,
)
