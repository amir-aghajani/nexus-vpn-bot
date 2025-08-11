from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from data import json_storage
from keyboards import get_manage_servers_keyboard, get_single_server_keyboard
from .sanaei_3x_ui import new_sanaei_3x_ui_handler
from ..globals import return_to_main_menu


async def manage_servers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    servers = json_storage.get_all_servers()
    await query.edit_message_text(
        text='☑️ به بخش مدیریت سرور ها خوش آمدید',
        reply_markup=get_manage_servers_keyboard(servers=servers)
    )
    await query.answer('مدیریت سرور ها')


async def manage_server_settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split(':')
    server_id = data[3] if len(data) > 2 else None

    if server_id:
        server = json_storage.get_server(server_id)
        if not server:
            await query.answer('سرور یافت نشد')
            return

        await query.edit_message_text(
            text=f'🔧 تنظیمات سرور {server["name"]}:\n\n'
                 f'📦 ظرفیت: {server["configLimit"]}\n'
                 f'🌐 آدرس پنل: {server["panelUrl"]}\n'
                 f'👤 نام کاربری پنل: {server["panelUsername"]}\n'
                 f'🔑 رمز عبور پنل: {server["panelPassword"]}',
            reply_markup=get_single_server_keyboard(server)
        )
    else:
        await query.answer('شناسه سرور معتبر نیست', show_alert=True)

def register_server_management_handlers(app):
    app.add_handler(CallbackQueryHandler(manage_server_settings_handler, pattern=r'^admin:manageServers:settings:'))
    app.add_handler(new_sanaei_3x_ui_handler)
    app.add_handler(CallbackQueryHandler(manage_servers_handler, pattern=r'^admin:manageServers'))
