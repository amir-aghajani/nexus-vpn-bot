from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, filters, MessageHandler

from api_client.sanaei import SanaeiClient
from data import json_storage
from database import servers_db
from handlers.globals import return_to_main_menu_filter, return_to_main_menu_handler, return_to_main_menu_inline_handler, start_command_handler
from keyboards import get_return_to_main_menu_keyboard

ENTER_SERVER_NAME, ENTER_SERVER_LIMIT, ENTER_SERVER_EMOJI, ENTER_PANEL_URL, ENTER_PANEL_USERNAME, ENTER_PANEL_PASSWORD = range(6)


async def handler_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.delete_message()
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='📦 افزودن سرور ' +
             '3x-ui\n\n\n'
             '▪️ مرحله اول:\n\n'
             '👤 لطفاً نام سرور را وارد کنید\n\n'
             '❗ توجه کنید ایموجی سرور در مراحل بعد از شما پرسیده خواهد شد!',
        reply_markup=get_return_to_main_menu_keyboard('نام سرور')
    )
    await query.answer()

    return ENTER_SERVER_NAME


async def server_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    context.user_data['serverName'] = message.text

    await message.reply_text(
        text=' مرحله دوم:\n\n'
             '♾️️ لطفا ظرفیت تعداد ساخت کانفیگ را برای سرور وارد کنید ( به صورت عددی )',
        reply_to_message_id=message.message_id,
        reply_markup=get_return_to_main_menu_keyboard('محدودیت سرور')
    )

    return ENTER_SERVER_LIMIT


async def server_limit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    try:
        limit = int(message.text)
        context.user_data['serverConfigLimit'] = limit
    except ValueError:
        await message.reply_text(
            text='❌ لطفاً یک عدد معتبر وارد کنید.',
            reply_to_message_id=message.message_id,
            reply_markup=get_return_to_main_menu_keyboard('محدودیت سرور')
        )
        return ENTER_SERVER_LIMIT

    await message.reply_text(
        text='️▪️ مرحله سوم:\n\n'
             '♾️️ لطفا ایموجی مربوط به سرور را ارسال کنید',
        reply_to_message_id=message.message_id,
        reply_markup=get_return_to_main_menu_keyboard('محدودیت سرور')
    )

    return ENTER_SERVER_EMOJI


async def server_emoji_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    context.user_data['serverEmoji'] = message.text

    await message.reply_text(
        text='️▪️ مرحله چهارم:\n\n'
             '️🔗 لطفا آدرس پنل 3x-ui را به صورت مثال های زیر وارد کنید (به صورت URL)\n\n'
             '❕ https://yourdomain.com:54321\n'
             '❕ https://yourdomain.com:54321/path\n'
             '❗️ http://125.12.12.36:54321\n'
             '❗️ http://125.12.12.36:54321/path\n\n'
             'اگر سرور مورد نظر با دامنه و ssl هست از مثال (❕) استفاده کنید\n'
             'اگر سرور مورد نظر با ip و بدون ssl هست از مثال (❗️) استفاده کنید\n',
        reply_to_message_id=message.message_id,
        reply_markup=get_return_to_main_menu_keyboard('آدرس پنل')
    )

    return ENTER_PANEL_URL


async def panel_url_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    panel_url = message.text
    context.user_data['serverPanelUrl'] = panel_url

    await message.reply_text(
        text='️▪️ مرحله پنجم:\n\n'
             '👤 لطفا نام کاربری پنل 3x-ui را وارد کنید',
        reply_to_message_id=message.message_id,
        reply_markup=get_return_to_main_menu_keyboard('نام کاربری پنل')
    )

    return ENTER_PANEL_USERNAME


async def panel_username_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    panel_username = message.text
    context.user_data['serverPanelUsername'] = panel_username

    await message.reply_text(
        text='️▪️ مرحله ششم:\n\n'
             '🔑 لطفا رمز عبور پنل 3x-ui را وارد کنید',
        reply_to_message_id=message.message_id,
        reply_markup=get_return_to_main_menu_keyboard('رمز عبور پنل')
    )

    return ENTER_PANEL_PASSWORD


async def panel_password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    panel_password = message.text
    context.user_data['serverPanelPassword'] = panel_password

    sanaei_client = SanaeiClient(
        panel_url=context.user_data['serverPanelUrl'],
        username=context.user_data['serverPanelUsername'],
        password=context.user_data['serverPanelPassword']
    )

    if not sanaei_client.test_client_connection():
        await message.reply_text(
            text=
            '❌ مشکلی در برقراری ارتباط با سرور پیش آمده است ❌\n\n'
            'لطفا مجددا آدرس پنل را وارد کنید',
            reply_to_message_id=message.message_id,
            parse_mode='MarkDownV2',
            reply_markup=get_return_to_main_menu_keyboard('آدرس پنل')
        )

        return ENTER_PANEL_URL

    server_data = {
        'name': context.user_data['serverName'],
        'emoji': context.user_data['serverEmoji'],
        'configLimit': context.user_data['serverConfigLimit'],
        'panelUrl': context.user_data['serverPanelUrl'],
        'panelUsername': context.user_data['serverPanelUsername'],
        'panelPassword': context.user_data['serverPanelPassword'],
        'status': 'disabled',
        'panelType': 'sanaei',
    }

    server_id = servers_db.create(server_data)
    json_storage.add('servers', {**server_data, 'id': server_id})

    await message.reply_text(
        text='✅ سرور با موفقیت اضافه شد.\n\n',
        reply_to_message_id=message.message_id,
        reply_markup=get_return_to_main_menu_keyboard()
    )

    return ConversationHandler.END


new_sanaei_3x_ui_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(handler_entry, pattern=r'^admin:addServer:3X-UI')
    ],
    states={
        ENTER_SERVER_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND & ~return_to_main_menu_filter, server_name_handler),
        ],
        ENTER_SERVER_LIMIT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND & ~return_to_main_menu_filter, server_limit_handler)
        ],
        ENTER_SERVER_EMOJI: [
            MessageHandler(filters.TEXT & ~filters.COMMAND & ~return_to_main_menu_filter, server_emoji_handler)
        ],
        ENTER_PANEL_URL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND & ~return_to_main_menu_filter, panel_url_handler)
        ],
        ENTER_PANEL_USERNAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND & ~return_to_main_menu_filter, panel_username_handler)
        ],
        ENTER_PANEL_PASSWORD: [
            MessageHandler(filters.TEXT & ~filters.COMMAND & ~return_to_main_menu_filter, panel_password_handler)
        ]
    },
    fallbacks=[
        start_command_handler,
        return_to_main_menu_handler,
        return_to_main_menu_inline_handler
    ],
    allow_reentry=True,
)
