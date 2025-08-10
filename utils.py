import json
from pathlib import Path

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from config import settings
from keyboards import get_start_keyboard


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


class BannedUsers:
    def __init__(self, file_path="banned_users.json"):
        self.file_path = Path(file_path)

    def load_banned_users(self):
        if not self.file_path.exists():
            return set()
        with open(self.file_path, "r", encoding="utf-8") as f:
            return set(json.load(f))  # fast lookups with set

    def save_banned_users(self, banned_users):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(list(banned_users), f, indent=2)

    def ban_user(self, user_id: int):
        banned_users = self.load_banned_users()
        banned_users.add(user_id)
        self.save_banned_users(banned_users)

    def unban_user(self, user_id: int):
        banned_users = self.load_banned_users()
        banned_users.discard(user_id)
        self.save_banned_users(banned_users)

    def is_user_banned(self, user_id: int) -> bool:
        banned_users = self.load_banned_users()
        return user_id in banned_users
