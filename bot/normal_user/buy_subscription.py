import random
import string
import uuid
from datetime import datetime, timedelta, UTC

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
from .keyboards import categories_keyboard, finalize_keyboard, plans_keyboard, servers_keyboard

SELECT_CATEGORY, SELECT_PLAN, SELECT_SERVER, FINALIZE = range(4)


@user_check
async def buy_subscription_start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_db_data):
    query = update.callback_query
    context.user_data['buyPhase'] = {}

    if query.data != "returnToCategories":
        if "latestInlineConversationMessageId" in context.user_data:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_user.id,
                    message_id=context.user_data["latestInlineConversationMessageId"]
                )
            except Exception as e:
                raise BotError(e)

        context.user_data["latestInlineConversationMessageId"] = query.message.message_id

    await query.edit_message_text(
        text="لطفاً یک دسته‌بندی انتخاب کنید:",
        reply_markup=categories_keyboard()
    )
    await query.answer()

    return SELECT_CATEGORY


async def on_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    action, value = parse_callback(query.data)

    if action == "category":
        context.user_data["buyPhase"]["categoryId"] = value

    await query.edit_message_text(
        text="لطفاً یک پلن انتخاب کنید:",
        reply_markup=plans_keyboard(context.user_data['buyPhase']['categoryId'])
    )
    await query.answer()

    return SELECT_PLAN


async def on_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    action, value = parse_callback(query.data)

    if action == "plan":
        context.user_data['buyPhase']['planId'] = value

    await query.edit_message_text(
        text="لطفاً یک سرور را انتخاب کنید:",
        reply_markup=servers_keyboard()
    )
    await query.answer()

    return SELECT_SERVER


async def on_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(context.user_data)
    query = update.callback_query
    action, value = parse_callback(query.data)

    server_id = value
    context.user_data['buyPhase']['serverId'] = server_id
    plan_details = json_storage.get('plans', context.user_data['buyPhase']['planId'])
    server_details = json_storage.get('servers', server_id)

    await query.edit_message_text(
        text="اطلاعات خرید شما:\n\n"
             "نام پلن: " + f"{plan_details['name']}\n\n" +
             "هزینه: " + f"{plan_details['price']:,}" + ' تومان\n\n' +
             "مدت زمان: " + f"{plan_details['duration']}" + ' روز\n\n' +
             "لوکیشن سرور: " + f"{server_details['emoji']} {server_details['name']}\n\n",
        reply_markup=finalize_keyboard()
    )
    await query.answer()

    return FINALIZE


async def on_finalize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    plan_details = json_storage.get('plans', context.user_data['buyPhase']['planId'])
    server_details = json_storage.get('servers', context.user_data['buyPhase']['serverId'])

    user_wallet_balance = db_client.fetch('users', str(update.effective_user.id)).get('walletBalance', 0)
    if user_wallet_balance < plan_details['price']:
        await query.answer('❌ موجودی کیف پول شما کافی نیست ❌', show_alert=True)
        return FINALIZE

    config_uuid = str(uuid.uuid4())
    config_email = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    config_sub_id = ''.join(random.choices(string.ascii_letters + string.digits, k=20))

    if server_details['panelType'] == 'sanaei':
        expiry_date = datetime.now(UTC) + timedelta(days=plan_details['duration'])
        total_bandwidth = plan_details['bandwidth'] * 1073741824
        try:
            client = sanaei.SanaeiClient(
                server_details['panelUrl'],
                server_details['panelUsername'],
                server_details['panelPassword']
            )
            server_inbounds = client.list_of_inbounds()
            for inbound in server_inbounds:
                if inbound.get('id'):
                    inbound_data = {
                        "id": config_uuid,
                        "flow": "",
                        "email": config_email + "_INBOUD_" + str(inbound['id']),
                        "limitIp": 0,
                        "totalGB": total_bandwidth,
                        "expiryTime": int(expiry_date.timestamp()) * 1000,
                        "enable": True,
                        "tgId": update.effective_user.id,
                        "subId": config_sub_id,
                        "comment": "AUTO_GENERATED_BY_NEXUS",
                        "reset": 0
                    }
                    client.create_inbound(inbound_id=inbound['id'], inbound_data=inbound_data)
            config_url = client.get_sub_base_url() + f'{config_sub_id}'

            db_client.create('subscriptions', {
                'userId': update.effective_user.id,
                'categoryId': context.user_data['buyPhase']['categoryId'],
                'subDuration': plan_details['duration'],
                'subBandwidth': plan_details['bandwidth'],
                'serverId': context.user_data['buyPhase']['serverId'],
                'configUuid': config_uuid,
                'configEmail': config_email,
                'configSubId': config_sub_id,
                'isActive': True,
            })
            db_client.update('users', str(update.effective_user.id), {
                'walletBalance': firestore.Increment(-plan_details['price'])
            })

            qrcode = generate_qr(config_url, bg_path='assets/qr_bg.png')
            await update.effective_chat.send_photo(
                photo=qrcode,
                caption=
                "✔️ سفارش جدید شما با موفقیت انجام شد!\n\n"
                "⏰ مدت سرویس: " + f"{plan_details['duration']}" + " روز\n" +
                "🔋 حجم سرویس: " + f"{plan_details['bandwidth']}" + " گیگابایت\n" +
                "📍 لوکیشن سرور: " + f"{server_details['emoji']} {server_details['name']}\n\n" +
                "🔻 لینک کانفیگ شما:\n\n" + f"<code>{config_url}</code>",
                parse_mode="HTML"
            )

        except Exception as e:
            raise BotError(e)

    await query.answer()
    return FINALIZE

    return ConversationHandler.END


buy_subscription_callback_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(buy_subscription_start, pattern="^user:purchase$")
    ],
    states={
        SELECT_CATEGORY: [
            CallbackQueryHandler(on_category, pattern="^category:"),
        ],
        SELECT_PLAN: [
            CallbackQueryHandler(buy_subscription_start, pattern="^returnToCategories$"),
            CallbackQueryHandler(on_plan, pattern="^plan:"),
        ],
        SELECT_SERVER: [
            CallbackQueryHandler(on_category, pattern="^returnToPlans$"),
            CallbackQueryHandler(on_server, pattern="^server:"),
        ],
        FINALIZE: [
            CallbackQueryHandler(on_plan, pattern="^returnToServers$"),
            CallbackQueryHandler(on_finalize, pattern="^approve$"),
        ],
    },
    fallbacks=[
        return_to_main_menu_inline_handler,
        start_command_handler,
    ],
    name="buy_subscription_conversation_handler",
    persistent=True,
    allow_reentry=False,
)
