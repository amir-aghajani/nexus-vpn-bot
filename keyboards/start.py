from telegram import KeyboardButton, ReplyKeyboardMarkup


def get_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    custom_keyboard = [
        [KeyboardButton("🌴 سرویس های من"), KeyboardButton("🛒 خرید سرویس")],
        [KeyboardButton("💷 کیف پول")],
        [KeyboardButton("🎓 آموزشات"), KeyboardButton("📮 پشتیبانی")],
    ]
    return ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
