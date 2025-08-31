from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from data import json_storage


def channels_keyboard(channels) -> InlineKeyboardMarkup:
    keyboard = []
    for channel in channels:
        keyboard.append([InlineKeyboardButton(f'🔗 چنل', url=f'https://t.me/{channel.lstrip('@')}')])

    return InlineKeyboardMarkup(keyboard)


# --- BEGIN Purchase Keyboards ---#
def categories_keyboard() -> InlineKeyboardMarkup:
    categories = json_storage.get('categories') or []
    keyboard = [[InlineKeyboardButton(f'{category['name']}', callback_data=f'category:{category['id']}')] for category in categories]
    keyboard.append([InlineKeyboardButton('↩️ بازگشت به منوی اصلی', callback_data='returnToMainMenu')])
    return InlineKeyboardMarkup(keyboard)


def plans_keyboard(category_id: str) -> InlineKeyboardMarkup:
    plans = json_storage.get('plans')
    plans = [plan for plan in plans if plan['categoryId'] == category_id]
    keyboard = []
    if not plans:
        keyboard.append([InlineKeyboardButton('❌ هیچ پلانی وجود ندارد', callback_data='noneFunctioningButton')])

    else:
        for plan in plans:
            keyboard.append([InlineKeyboardButton(f'{plan['name']} - {plan['price']:,} تومان', callback_data=f'plan:{plan['id']}')])

    keyboard.append([InlineKeyboardButton('↩️ بازگشت به دسته بندی‌ها', callback_data='returnToCategories')])
    return InlineKeyboardMarkup(keyboard)


def servers_keyboard() -> InlineKeyboardMarkup:
    servers = json_storage.get('servers')
    servers = [server for server in servers if server['status'] == 'enabled']
    keyboard = []

    if not servers:
        keyboard.append([InlineKeyboardButton('❌ هیچ سرور فعالی وجود ندارد', callback_data='noneFunctioningButton')])
    else:
        for server in servers:
            keyboard.append([
                InlineKeyboardButton(
                    f'{server['emoji']} {server['name']}',
                    callback_data=f'server:{server['id']}')
            ])

    keyboard.append([InlineKeyboardButton('↩️ بازگشت به پلن‌ها', callback_data='returnToPlans')])
    return InlineKeyboardMarkup(keyboard)


def finalize_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton('❌ انصراف از خرید', callback_data='returnToMainMenu'), InlineKeyboardButton('✅ تایید خرید', callback_data='approve'), ],
        [InlineKeyboardButton('↩️ بازگشت به سرورها', callback_data='returnToServers')]
    ]
    return InlineKeyboardMarkup(keyboard)


# --- END Purchase Keyboards ---#

# --- BEGIN Wallet Keyboards ---#

def top_up_amounts_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton('50,000 تومان', callback_data='topUpAmount:50000')],
        [InlineKeyboardButton('100,000 تومان', callback_data='topUpAmount:100000')],
        [InlineKeyboardButton('200,000 تومان', callback_data='topUpAmount:200000')],
        [InlineKeyboardButton('500,000 تومان', callback_data='topUpAmount:500000')],
        [InlineKeyboardButton('1,000,000 تومان', callback_data='topUpAmount:1000000')],
        [InlineKeyboardButton('مبلغ دلخواه', callback_data='topUpAmount:custom')],
        [InlineKeyboardButton('↩️ بازگشت به منوی اصلی', callback_data='returnToMainMenu')]
    ]
    return InlineKeyboardMarkup(keyboard)


def payment_methods_keyboard(methods) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(f'{method['name']}', callback_data=f'paymentMethod:{method['id']}')] for method in methods
    ]

    return InlineKeyboardMarkup(keyboard)

# --- END Wallet Keyboards ---#
