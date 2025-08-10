from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from keyboards import get_manage_servers_keyboard
from .sanaei_3x_ui import new_sanaei_3x_ui_handler


async def manage_servers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.edit_message_text('مدیریت سرورها در حال حاضر در دسترس نیست.', reply_markup=get_manage_servers_keyboard())
    await query.answer()


def register_server_management_handlers(app):
    app.add_handler(CallbackQueryHandler(manage_servers_handler, pattern=r'^admin:manageServers'))
    app.add_handler(new_sanaei_3x_ui_handler)
