from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from bot.normal_user.keyboards import channels_keyboard
from data import json_storage
from database import db_client
from errors import BotError


def parse_callback(query_data: str):
    if ":" in query_data:
        return query_data.split(":", 1)
    return query_data, None


def user_check(handler):
    @wraps(handler)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        not_joined_channels = []

        for channel_id in json_storage.get('channels'):
            try:
                member = await context.bot.get_chat_member(chat_id=channel_id, user_id=user_id)

                if member.status in ['left', 'kicked']:
                    not_joined_channels.append(channel_id)
            except Exception as e:
                raise BotError(
                    "Unable to verify channel membership. (Check Bot's Permissions)\n\n" +
                    f"Error: {e}"
                )

        if len(not_joined_channels) > 0:
            await context.bot.send_message(
                text=
                "🔖 برای استفاده از ربات و همچنین دریافت اطلاعیه های ربات و همچنین حمایت از ما وارد کانال شوید :\n\n"
                "سپس روی دکمه عضو شدم کلیک کنید.",
                reply_markup=channels_keyboard(not_joined_channels),
                chat_id=update.effective_chat.id,
            )
            if update.callback_query.data:
                await update.callback_query.answer()

        user_db_data = db_client.fetch('users', user_id)
        return await handler(update, context, user_db_data, *args, **kwargs)

    return wrapped
