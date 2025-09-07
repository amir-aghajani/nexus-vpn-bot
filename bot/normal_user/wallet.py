from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, filters, MessageHandler

from bot.admin.keyboards import review_transaction_keyboard
from bot.helpers import user_check
from bot.normal_user.keyboards import payment_methods_keyboard, top_up_amounts_keyboard
from config import settings
from data import json_storage
from handlers.globals import clean_user_data
from database import db_client
from handlers.globals import return_to_main_menu_filter, return_to_main_menu_handler, return_to_main_menu_inline_handler, start_command_handler
from keyboards import get_return_to_main_menu_keyboard

CHOOSE_AMOUNT, CUSTOM_AMOUNT, CHOOSE_PAYMENT_METHOD, SCREENSHOT_PROOF = range(4)


@user_check
async def wallet_start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db_data) -> int:
    query = update.callback_query

    await clean_user_data(update, context)
    context.user_data['topUpPhase'] = {}

    await query.edit_message_text(
        f'👤 شناسه کاربری شما: {user_db_data['id']}\n\n'
        f'💰 موجودی کیف‌پول شما: {user_db_data['walletBalance']} تومان\n\n'
        '🔹 لطفاً مبلغ مورد نظر برای افزایش موجودی کیف‌پول خود را انتخاب کنید',
        reply_markup=top_up_amounts_keyboard()
    )

    return CHOOSE_AMOUNT


@user_check
async def on_amount(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db_data) -> int:
    query = update.callback_query
    await query.answer()
    callback_data = query.data.split(':')

    if callback_data[1] == 'custom':
        await query.delete_message()
        print(update.effective_user.id)
        await context.bot.send_message(
            text=
            '🌟 لطفا مبلغ مورد نظر خود را به اعداد لاتین ارسال کنید. 🌟\n\n' +
            '💡 نمونه: \n' +
            '69000',
            reply_markup=get_return_to_main_menu_keyboard(),
            chat_id=update.effective_user.id
        )

        return CUSTOM_AMOUNT

    else:
        amount = int(callback_data[1])
        context.user_data['topUpPhase']['amount'] = amount
        await query.edit_message_text(
            '💳 لطفاً روش پرداخت خود را انتخاب کنید:',
            reply_markup=payment_methods_keyboard(json_storage.get('paymentMethods'))
        )

        return CHOOSE_PAYMENT_METHOD


@user_check
async def on_custom_amount(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db_data):
    message = update.message
    amount = message.text
    try:
        amount_value = int(amount)

        if amount_value > 10000000 or amount_value < 10000:
            await update.message.reply_text(
                '✨💸 لطفا یک مبلغ بین 10,000 تا 10,000,000 وارد کنید 💸✨',
                reply_markup=get_return_to_main_menu_keyboard(),
                reply_to_message_id=message.message_id
            )

            return CUSTOM_AMOUNT

        context.user_data['topUpPhase']['amount'] = amount_value
        await message.reply_text(
            '💳 لطفاً روش پرداخت خود را انتخاب کنید:',
            reply_to_message_id=message.message_id,
            reply_markup=payment_methods_keyboard(json_storage.get('paymentMethods'))
        )

        return CHOOSE_PAYMENT_METHOD

    except ValueError:
        await update.message.reply_text(
            '✨💸 لطفا یک مبلغ معتبر وارد کنید 💸✨',
            reply_markup=get_return_to_main_menu_keyboard(),
            reply_to_message_id=message.message_id
        )

        return CUSTOM_AMOUNT


@user_check
async def on_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db_data):
    query = update.callback_query
    callback_data = query.data.split(':')

    payment_method_details = json_storage.get('paymentMethods', callback_data[1])
    context.user_data['topUpPhase']['paymentMethod'] = payment_method_details['id']

    if payment_method_details['type'] == 'cardTransfer':
        await query.edit_message_text(
            text='⚠️ لطفا مبلغ ' + f'{context.user_data['topUpPhase']['amount']:,}' + ' را به شماره کارت\n' +
                 f'<code>{payment_method_details['apiKey']}</code>\n' +
                 'به نام ' + f'<code>{payment_method_details['cardHolderName']}</code>' + ' واریز کرده و سپس رسید تراکنش را اینجا به صورت عکس ارسال کنید:',
            parse_mode='HTML'
        )

        return SCREENSHOT_PROOF

    else:
        await query.delete_message()
        await query.answer('این روش پرداخت هنوز فعال نشده است!')

        return ConversationHandler.END


@user_check
async def on_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db_data):
    user_id = update.effective_user.id

    created_transaction = db_client.create(
        'transactions', data={
            'userId': user_id,
            'messageId': update.message.message_id,
            'amount': context.user_data['topUpPhase']['amount'],
            'paymentMethodId': context.user_data['topUpPhase']['paymentMethod'],
            'status': 'UNDER_REVIEW'
        }
    )

    if update.message.photo:
        photo = update.message.photo[-1]
        for admin_id in settings.telegram_bot_admin_ids:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=photo.file_id,
                caption=f'تراکنش جدید\n\n' + f'مبلغ انتخابی ' + f'{created_transaction['amount']:,}' + ' است. لطفاً بررسی کنید 🔍\n\n' + 'پروفایل کاربر : ' +
                        f'<a href="https://t.me/@id{user_id}">{user_id}</a>',
                reply_markup=review_transaction_keyboard(created_transaction['id']),
                parse_mode='HTML'
            )

    await update.message.reply_text(
        '⏳✨ رسید شما با موفقیت به کارشناس مربوطه ارجاع داده شده است.\n\n'
        '■ در صورت تایید تراکنش، کیف‌پول شما ظرف چند دقیقه/لحظه شارژ خواهد شد و ما شما را مطلع خواهیم کرد.\n'
        '» لطفاً از ارسال پیام به پشتیبانی در این زمینه خودداری نمایید! 🚫📩✨',
    )

    return ConversationHandler.END


top_up_wallet_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(wallet_start, pattern=r'^user:topUpWallet'),
    ],
    states={
        CHOOSE_AMOUNT: [
            CallbackQueryHandler(on_amount, pattern=r'^topUpAmount:'),
        ],
        CUSTOM_AMOUNT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND & ~return_to_main_menu_filter, on_custom_amount),
        ],
        CHOOSE_PAYMENT_METHOD: [
            CallbackQueryHandler(on_payment_method, pattern=r'^paymentMethod:'),
        ],
        SCREENSHOT_PROOF: [
            MessageHandler(filters.PHOTO, on_screenshot)
        ]
    },
    fallbacks=[
        return_to_main_menu_inline_handler,
        return_to_main_menu_handler,
        start_command_handler,
    ],
    name='top_up_wallet_conversation',
    persistent=True,
    allow_reentry=False,
)
