from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from errors import BotError


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err = context.error

    if isinstance(err, BotError):
        if isinstance(update, Update) and update.effective_chat:
            for uid in settings.telegram_bot_admin_ids:
                try:
                    await context.bot.send_message(
                        chat_id=uid,
                        text=
                        '❌ Error in the bot process ❌\n'
                        f'```ErrorMessage\n{str(err)}```',
                        parse_mode='MarkDownV2'
                    )
                except Exception as e:
                    print(f"Failed to send error message to admin {id}: {e}")
    else:
        print(f"Unhandled error: {err}")
