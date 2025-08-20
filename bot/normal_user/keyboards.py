from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from data import json_storage


def categories_keyboard() -> InlineKeyboardMarkup:
    categories = json_storage.get('categories') or []
    keyboard = [[InlineKeyboardButton(f'{category['name']}', callback_data=category['id'])] for category in categories]
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
            keyboard.append([InlineKeyboardButton(f'{plan['name']} - {plan['price']} تومان', callback_data=plan['id'])])

    keyboard.append([InlineKeyboardButton('↩️ بازگشت به دسته بندی‌ها', callback_data='returnToCategories')])
    return InlineKeyboardMarkup(keyboard)


def servers_keyboard() -> InlineKeyboardMarkup:
    servers = json_storage.get('servers')
    servers = [server for server in servers if server['status'] == 'ACTIVE']
    keyboard = []

    if not servers:
        keyboard.append([InlineKeyboardButton('❌ هیچ سرور فعالی وجود ندارد', callback_data='noneFunctioningButton')])
    else:
        for server in servers:
            keyboard.append([
                InlineKeyboardButton(
                    f'{server['emoji']} {server['name']}',
                    callback_data=server['id'])
            ])

    keyboard.append([InlineKeyboardButton('↩️ بازگشت به پلن‌ها', callback_data='returnToPlans')])
    return InlineKeyboardMarkup(keyboard)
