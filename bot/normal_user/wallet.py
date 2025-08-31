import time

from telegram import Update
from telegram.ext import (CallbackQueryHandler, ContextTypes, ConversationHandler, filters, MessageHandler)

from bot.helpers import user_check
from bot.normal_user.keyboards import payment_methods_keyboard, top_up_amounts_keyboard
from data import json_storage
from handlers.globals import return_to_main_menu_filter, return_to_main_menu_handler, return_to_main_menu_inline_handler, start_command_handler
from keyboards import get_return_to_main_menu_keyboard

CHOOSE_AMOUNT, CUSTOM_AMOUNT, CHOOSE_PAYMENT_METHOD, SCREENSHOT_PROOF = range(4)


@user_check
async def wallet_start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db_data) -> int:
    context.user_data['topUpPhase'] = {}

    if "latestInlineConversationMessageId" in context.user_data:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_user.id,
                message_id=context.user_data["latestInlineConversationMessageId"]
            )
        except Exception as e:
            print(f"Error deleting message: {e}")

    query = update.callback_query
    await query.edit_message_text(
        f"👤 شناسه کاربری شما: {user_db_data['id']}\n\n"
        f"💰 موجودی کیف‌پول شما: {user_db_data['walletBalance']} تومان\n\n"
        "🔹 لطفاً مبلغ مورد نظر برای افزایش موجودی کیف‌پول خود را انتخاب کنید",
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
            "🌟 لطفا مبلغ مورد نظر خود را به اعداد لاتین ارسال کنید. 🌟\n\n" +
            "💡 نمونه: \n" +
            "69000",
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
                "✨💸 لطفا یک مبلغ بین 10,000 تا 10,000,000 وارد کنید 💸✨",
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
            "✨💸 لطفا یک مبلغ معتبر وارد کنید 💸✨",
            reply_markup=get_return_to_main_menu_keyboard(),
            reply_to_message_id=message.message_id
        )

        return CUSTOM_AMOUNT


@user_check
async def on_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db_data):
    user_id = update.effective_user.id
    transaction_data = {
        'messageId': update.message.message_id,
        'userId': user_id,
        'timeStamp': int(time.time()),
        'amount': context.user_data['amount_to_add'],
        'status': 'UNDER_REVIEW'
    }

    transactions_ref = FIRESTORE_DATABASE.collection('transactions')
    doc_ref = transactions_ref.document()
    doc_ref.set(transaction_data)
    admin_text = f"مبلغ انتخابی {transaction_data['amount']} است. لطفاً بررسی کنید 🔍"

    if update.message.photo:
        photo = update.message.photo[-1]
        await context.bot.send_photo(
            chat_id=ADMIN_CHANNEL_CHAT_ID,
            photo=photo.file_id,
            caption=f'<a href="tg://user?id={user_id}">لینک کاربر</a>',
            parse_mode='HTML'
        )
        await context.bot.send_message(chat_id=ADMIN_CHANNEL_CHAT_ID, text=admin_text, reply_markup=get_transaction_decision_keyboard(doc_ref.id))

    await update.message.reply_text(
        "⏳✨ رسید شما با موفقیت به کارشناس مربوطه ارجاع داده شده است.\n\n"
        "■ در صورت تایید تراکنش، کیف‌پول شما ظرف چند دقیقه/لحظه شارژ خواهد شد و ما شما را مطلع خواهیم کرد.\n"
        "» لطفاً از ارسال پیام به پشتیبانی در این زمینه خودداری نمایید! 🚫📩✨",
        reply_markup=get_custom_keyboard()
    )

    return ConversationHandler.END


async def handle_screenshot_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the review of the screenshot"""

    user_id = update.effective_user.id
    query = update.callback_query
    await query.answer()
    callback_data = query.data.split(':')

    transaction_doc_ref = FIRESTORE_DATABASE.collection('transactions').document(str(callback_data[2]))
    transaction_data = transaction_doc_ref.get().to_dict()

    if transaction_data['status'] != 'UNDER_REVIEW':
        await update.callback_query.message.reply_text(
            "درخواست قبلاً بررسی شده 🔍"
        )

        return

    user_doc_ref = FIRESTORE_DATABASE.collection('users').document(str(transaction_data['userId']))
    user_data = user_doc_ref.get().to_dict()
    user_funds = user_data.get('funds', 0)

    if callback_data[1] == 'approve':
        transaction_doc_ref.set({'status': 'APPROVED'}, merge=True)
        user_doc_ref.set({'funds': int(user_funds + transaction_data['amount'])}, merge=True)

        await update.callback_query.message.reply_text(
            "درخواست با موفقیت تایید شد ✅"
        )

        await context.bot.send_message(
            chat_id=transaction_data['userId'],
            text=f"پرداخت موفقیت‌آمیز بود! مبلغ {transaction_data['amount']} به حساب کاربری شما با موفقیت اضافه شد. 💰✅",
            reply_to_message_id=transaction_data['messageId']
        )

        return

    elif callback_data[1] == 'deny':
        transaction_doc_ref.set({'status': 'DENIED'}, merge=True)
        await update.callback_query.message.reply_text(
            "درخواست با موفقیت رد شد ❌"
        )

        await context.bot.send_message(
            chat_id=transaction_data['userId'],
            text="⚠️ پرداخت موفقیت‌آمیز نبود. لطفاً دوباره تلاش کنید! 🔄",
            reply_to_message_id=transaction_data['messageId']
        )

        return


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
