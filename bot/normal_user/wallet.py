from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from data import json_storage
from database import db_client
import time

CUSTOM_AMOUNT, SCREENSHOT_PROOF = range(2)


async def wallet_start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db_data) -> int:
    """Starts the wallet section and sends the user the wallet keyboard"""

    user_id = update.effective_user.id
    funds = user_db_data.get('funds', 0)

    replay_keyboard = get_wallet_amount_keyboard()

    await update.message.reply_text(
        f"🌟✨👤 شناسه کاربری شما: {user_id} ✨🌟\n\n"
        f"💎💰 موجودی کیف‌پول شما: {funds} تومان 💰💎\n",
        reply_markup=get_wallet_amount_keyboard()
    )
    return ConversationHandler.END


@channel_membership_and_phone_number_required
async def wallet_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db_data) -> int:
    """Handles the callback query's if the user clicks on the preset amounts"""

    user_id = update.effective_user.id
    query = update.callback_query
    await query.answer()
    callback_data = query.data.split(':')

    if callback_data[2] == 'custom':
        await update.callback_query.message.delete()
        await update.callback_query.message.reply_text(
            "🌟 لطفا مبلغ مورد نظر خود را به اعداد لاتین ارسال کنید. 🌟\n"
            "💡 نمونه: \n\n"
            "69000",
            reply_markup=get_back_to_menu_keyboard()
        )
        return CUSTOM_AMOUNT
    else:
        amount = int(callback_data[2])
        context.user_data['amount_to_add'] = amount
        await update.callback_query.message.delete()
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=BLUEBANK_PHOTO_URL,
            caption=get_payment_message(amount),
            reply_markup=get_back_to_menu_keyboard()
        )
        return SCREENSHOT_PROOF


@channel_membership_and_phone_number_required
async def wallet_custom_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db_data):
    """Handles the callback query's if the user clicks on the custom amount"""

    amount = update.message.text
    try:
        amount_value = int(amount)
        context.user_data['amount_to_add'] = amount_value
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=BLUEBANK_PHOTO_URL,
            caption=get_payment_message(amount_value),
            reply_markup=get_back_to_menu_keyboard()
        )

        return SCREENSHOT_PROOF

    except ValueError:
        await update.message.reply_text("✨💸 لطفا یک مبلغ معتبر وارد کنید 💸✨")

        return CUSTOM_AMOUNT


@channel_membership_and_phone_number_required
async def handle_screenshot_submission(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db_data):
    """Handles the submission of the screenshot and sends the reciept to the admin for review"""

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


wallet_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(wallet_amount_handler, pattern=r'^wallet:add:'),
    ],
    states={
        CUSTOM_AMOUNT: [
            MessageHandler(filters.TEXT & filters.Regex(r'^🔙🏠 بازگشت به منوی اصلی 🏠🔙$'), return_to_main_menu),
            MessageHandler(filters.TEXT & ~filters.COMMAND, wallet_custom_amount_handler),
        ],
        SCREENSHOT_PROOF: [
            MessageHandler(filters.TEXT & filters.Regex(r'^🔙🏠 بازگشت به منوی اصلی 🏠🔙$'), return_to_main_menu),
            MessageHandler(filters.TEXT & ~filters.COMMAND, return_to_main_menu),
            MessageHandler(filters.PHOTO, handle_screenshot_submission)
        ]
    },
    fallbacks=[
        CommandHandler("start", start_command),
        MessageHandler(filters.TEXT & filters.Regex(r'^🔙🏠 بازگشت به منوی اصلی 🏠🔙$'), return_to_main_menu),
    ]
)
