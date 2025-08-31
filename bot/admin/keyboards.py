from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def review_transaction_keyboard(transaction_id):
    keyboard = [
        [
            InlineKeyboardButton(text='❌ رد کردن پرداخت', callback_data=f'reviewTransaction:deny:{transaction_id}'),
            InlineKeyboardButton(text='✅ تایید کردن پرداخت', callback_data=f'reviewTransaction:approve:{transaction_id}'),
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def transaction_already_reviewed_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton(text='این تراکنش قبلا بررسی شده است', callback_data='nonFunctioningButton')]])
