from firebase_admin.firestore import firestore
from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from bot.admin.keyboards import transaction_already_reviewed_keyboard
from database import db_client


async def handle_screenshot_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    callback_data = query.data.split(':')

    transaction_data = db_client.fetch('transactions', callback_data[2])

    if transaction_data['status'] != 'UNDER_REVIEW':
        await query.edit_message_reply_markup(
            reply_markup=transaction_already_reviewed_keyboard()
        )

        return

    target_user_data = db_client.fetch('users', transaction_data['userId'])

    if callback_data[1] == 'approve':
        db_client.update('transactions', transaction_data['id'], {
            'status': 'APPROVED'
        })

        db_client.update('users', target_user_data['id'], {
            'walletBalance': firestore.Increment(transaction_data['amount'])
        })

        await query.answer('✅ تراکنش با موفقیت تایید شد!', show_alert=True)

        await context.bot.send_message(
            chat_id=transaction_data['userId'],
            text=f"پرداخت موفقیت‌آمیز بود! مبلغ {transaction_data['amount']:,} به حساب کاربری شما با موفقیت اضافه شد. 💰✅",
            reply_to_message_id=transaction_data['messageId']
        )

    elif callback_data[1] == 'deny':
        db_client.update('transactions', transaction_data['id'], {
            'status': 'DENIED'
        })

        await query.answer('⚠️ تراکنش با موفقیت رد شد!', show_alert=True)

        await context.bot.send_message(
            chat_id=transaction_data['userId'],
            text="⚠️ پرداخت موفقیت‌آمیز نبود. لطفاً دوباره تلاش کنید! 🔄",
            reply_to_message_id=transaction_data['messageId']
        )

    await query.edit_message_reply_markup(
        reply_markup=transaction_already_reviewed_keyboard()
    )

    return


review_transaction_handler = CallbackQueryHandler(handle_screenshot_review, pattern=r'^reviewTransaction:')
