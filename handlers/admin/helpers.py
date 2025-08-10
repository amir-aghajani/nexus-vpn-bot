from telegram import Update

from database import users_db
from keyboards import get_return_to_main_menu_keyboard


async def user_id_helper(update: Update, user_id):
    try:
        int(user_id)
    except ValueError:
        await update.message.reply_text(
            'شناسه کاربری نامعتبر است. لطفاً یک شناسه کاربری معتبر وارد کنید.',
            reply_markup=get_return_to_main_menu_keyboard('شناسه عددی کاربر'),
            reply_to_message_id=update.message.message_id
        )

        return False

    if not users_db.exists(str(user_id)):
        await update.message.reply_text(
            text='کاربری با این شناسه وجود ندارد. لطفاً شناسه کاربری معتبر وارد کنید.',
            reply_markup=get_return_to_main_menu_keyboard('شناسه عددی کاربر'),
            reply_to_message_id=update.message.message_id
        )
        return False

    return True
