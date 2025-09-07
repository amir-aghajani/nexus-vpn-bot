from datetime import datetime, timedelta, timezone

from firebase_admin.firestore import firestore
from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler

from api_client import sanaei
from bot.helpers import parse_callback, user_check
from bot.qr_maker import generate_qr
from data import json_storage
from database import db_client
from errors import BotError
from handlers.globals import return_to_main_menu_inline_handler, start_command_handler
from .keyboards import servers_keyboard

SELECT_SERVER = range(1)


@user_check
async def test_subscription_start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db_data):
    query = update.callback_query

    latest_test = user_db_data.get('testService', {}).get('latestUse')
    if latest_test:
        latest_use = datetime.fromisoformat(latest_test)
        if latest_use > datetime.now(timezone.utc) - timedelta(days=30):
            await query.answer(
                'شما به تازگی از سرویس تست ما استفاده کرده اید لطفا 30 روز پس از آخرین تست خود مجددا تلاش کنید',
                show_alert=True
            )

            return ConversationHandler.END

    context.user_data["latestInlineConversationMessageId"] = query.message.message_id

    await query.edit_message_text(
        text="لطفاً یک سرور را انتخاب کنید:",
        reply_markup=servers_keyboard(show_return_to_plans=False)
    )
    await query.answer()

    return SELECT_SERVER


async def on_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(context.user_data)
    query = update.callback_query
    action, value = parse_callback(query.data)

    server_details = json_storage.get('servers', value)

    if server_details['panelType'] == 'sanaei':
        try:
            client = sanaei.SanaeiClient(
                server_details['panelUrl'],
                server_details['panelUsername'],
                server_details['panelPassword']
            )

            created_sub = client.create_sub(
                duration=7,
                bandwidth=2,
                user_tg_id=update.effective_user.id
            )
            sub_url = client.get_sub_base_url() + f'{created_sub['subID']}'

            db_client.create('subscriptions', {
                'userId': update.effective_user.id,
                'subDuration': 7,
                'subBandwidth': 2,
                'serverId': value,
                **created_sub,
                'isActive': True,
                'subType': 'test'
            })

            db_client.update('users', str(update.effective_user.id), {
                'testService': {
                    'latestUse': firestore.SERVER_TIMESTAMP
                }
            })

            qrcode = generate_qr(sub_url, bg_path='assets/qr_bg.png')
            await update.effective_chat.send_photo(
                photo=qrcode,
                caption=
                "✔️ سرویس تست جدید شما با موفقیت آماده شد!\n\n"
                "⏰ مدت سرویس: 7 روز\n" +
                "🔋 حجم سرویس: 2 گیگابایت\n" +
                "📍 لوکیشن سرور: " + f"{server_details['emoji']} {server_details['name']}\n\n" +
                "🔻 لینک سابسکریپشن شما:\n\n" + f"<code>{sub_url}</code>",
                parse_mode="HTML"
            )

        except Exception as e:
            raise BotError(e)

    await query.delete_message()
    await query.answer()

    return ConversationHandler.END


test_subscription_callback_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(test_subscription_start, pattern="^user:testSubscription$")
    ],
    states={
        SELECT_SERVER: [
            CallbackQueryHandler(on_server, pattern="^server:"),
        ]
    },
    fallbacks=[
        return_to_main_menu_inline_handler,
        start_command_handler,
    ],
    name="test_subscription_conversation_handler",
    persistent=True,
    allow_reentry=False,
)
