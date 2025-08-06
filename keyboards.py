from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_start_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    if is_admin:
        keyboard = [
            [InlineKeyboardButton("📉 آمار کلی ربات", callback_data='admin:showBotReports'), InlineKeyboardButton("📞 پیام خصوصی", callback_data='admin:sendPrivateMessage')],
            [InlineKeyboardButton("🔑 اطلاعات کاربر", callback_data='admin:showUserInfo')],
            [InlineKeyboardButton("💵 افزایش موجودی", callback_data='admin:increaseUserFunds'), InlineKeyboardButton("💸 کاهش موجودی", callback_data='admin:decreaseUserFunds')],
            [InlineKeyboardButton("❌ مسدود کردن کاربر", callback_data='admin:banUser'), InlineKeyboardButton("✅ آزاد کردن کاربر", callback_data='admin:unbanUser')],
            [InlineKeyboardButton("🔎 جستجو کانفیگ کاربر", callback_data='admin:findUserConfig')],
            [InlineKeyboardButton("🚦 مدیریت و تنظیمات سرورها", callback_data='admin:manageServers')],
            [InlineKeyboardButton("🗂 مدیریت دسته ها", callback_data='admin:manageCategories')],
            [InlineKeyboardButton("🪣 مدیریت پلن ها", callback_data='admin:managePlans')],
            [InlineKeyboardButton("🎯 هدیه حجم و زمان", callback_data='admin:addCompensation'), InlineKeyboardButton("🎁 مدیریت تخفیف ها", callback_data='admin:manageDiscounts')],
            [InlineKeyboardButton("💳 تنظیمات درگاه و کانال", callback_data='admin:managePaymentGateways'), InlineKeyboardButton("⚙️ تنظیمات ربات", callback_data='admin:manageBotSettings')],
            [InlineKeyboardButton("📨 ارسال پیام همگانی", callback_data='admin:sendBroadcastMessage')],
            [InlineKeyboardButton("📪 تیکت ها", callback_data='admin:manageTickets'), InlineKeyboardButton("❌ درخواست های رد شده", callback_data='admin:manageRejectedRequests')],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("📱 کانفیگ های من", callback_data='user:manageSubscriptions'), InlineKeyboardButton("🛒 خرید کانفیگ جدید", callback_data='user:buySubscription')],
            [InlineKeyboardButton("✅💳 ارسال رسید - شارژ کیف پول", callback_data='user:topUpWallet')],
            [InlineKeyboardButton("🧑‍💼 حساب کاربری", callback_data='user:manageAccount')],
            [InlineKeyboardButton("🧩 آموزش اتصال", callback_data='user:connectionGuide'), InlineKeyboardButton("📨 تیکت های من", callback_data='user:manageTickets')],
        ]

    return InlineKeyboardMarkup(keyboard)
