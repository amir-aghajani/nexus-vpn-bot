from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def get_start_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    if is_admin:
        keyboard = [
            [InlineKeyboardButton('📉 آمار کلی ربات', callback_data='admin:showBotReports'), InlineKeyboardButton('📞 پیام خصوصی', callback_data='admin:sendPrivateMessage')],
            [InlineKeyboardButton('🔑 اطلاعات کاربر', callback_data='admin:showUserInfo')],
            [InlineKeyboardButton('💵 افزایش موجودی', callback_data='admin:increaseUserFunds'), InlineKeyboardButton('💸 کاهش موجودی', callback_data='admin:decreaseUserFunds')],
            [InlineKeyboardButton('❌ مسدود کردن کاربر', callback_data='admin:banUser'), InlineKeyboardButton('✅ آزاد کردن کاربر', callback_data='admin:unbanUser')],
            [InlineKeyboardButton('🔎 جستجو کانفیگ کاربر', callback_data='admin:findUserConfig')],
            [InlineKeyboardButton('🚦 مدیریت و تنظیمات سرورها', callback_data='admin:manageServers')],
            [InlineKeyboardButton('🗂 مدیریت دسته ها', callback_data='admin:manageCategories')],
            [InlineKeyboardButton('🪣 مدیریت پلن ها', callback_data='admin:managePlans')],
            [InlineKeyboardButton('🎯 هدیه حجم و زمان', callback_data='admin:addCompensation'), InlineKeyboardButton('🎁 مدیریت تخفیف ها', callback_data='admin:manageDiscounts')],
            [InlineKeyboardButton('💳 تنظیمات درگاه و کانال', callback_data='admin:managePaymentGateways'), InlineKeyboardButton('⚙️ تنظیمات ربات', callback_data='admin:manageBotSettings')],
            [InlineKeyboardButton('📨 ارسال پیام همگانی', callback_data='admin:sendBroadcastMessage')],
            [InlineKeyboardButton('📪 تیکت ها', callback_data='admin:manageTickets'), InlineKeyboardButton('❌ درخواست های رد شده', callback_data='admin:manageRejectedRequests')],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton('📱 کانفیگ های من', callback_data='user:manageSubscriptions'), InlineKeyboardButton('🛒 خرید کانفیگ جدید', callback_data='user:buySubscription')],
            [InlineKeyboardButton('✅💳 ارسال رسید - شارژ کیف پول', callback_data='user:topUpWallet')],
            [InlineKeyboardButton('🧑‍💼 حساب کاربری', callback_data='user:manageAccount')],
            [InlineKeyboardButton('🧩 آموزش اتصال', callback_data='user:connectionGuide'), InlineKeyboardButton('📨 تیکت های من', callback_data='user:manageTickets')],
        ]

    return InlineKeyboardMarkup(keyboard)


def get_return_to_main_menu_keyboard(placerholder: str = None):
    keyboard = [
        [KeyboardButton('↩️ بازگشت به منوی اصلی')]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder=placerholder)


def get_manage_servers_keyboard(servers: list = None) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton('وضعیت', callback_data='noneFunctioningButton'),
            InlineKeyboardButton('تنظیمات', callback_data='noneFunctioningButton'),
            InlineKeyboardButton('نوع پنل', callback_data='noneFunctioningButton'),
            InlineKeyboardButton('نام سرور', callback_data='noneFunctioningButton'),
        ]
    ]
    if type(servers) == list and len(servers) > 0:
        for server in servers:
            keyboard.append([
                InlineKeyboardButton(server['status'], callback_data=f'noneFunctioningButton'),
                InlineKeyboardButton('⚙️', callback_data=f'admin:manageServers:settings:{server["id"]}'),
                InlineKeyboardButton(server['panelType'], callback_data=f'noneFunctioningButton'),
                InlineKeyboardButton(f'{server['flag']} {server['name']}', callback_data=f'noneFunctioningButton')
            ])
    else:
        keyboard.append([InlineKeyboardButton('❌ هیچ سروری وجود ندارد', callback_data='noneFunctioningButton')])

    keyboard.append([
        InlineKeyboardButton('➕ افزودن سرور مرزبان', callback_data='admin:addServer:Marzban'),
        InlineKeyboardButton('➕ افزودن سرور 3X-UI', callback_data='admin:addServer:3X-UI'),
    ])
    keyboard.append([InlineKeyboardButton('↩️ بازگشت به منوی اصلی', callback_data='returnToMainMenu')])

    return InlineKeyboardMarkup(keyboard)
