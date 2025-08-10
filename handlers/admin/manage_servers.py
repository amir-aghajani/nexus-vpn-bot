from database import servers_db
from telegram import Update
from telegram.ext import CallbackQueryHandler, ConversationHandler, ContextTypes
from keyboards import get_manage_servers_keyboard


async def manage_servers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.edit_message_text('مدیریت سرورها در حال حاضر در دسترس نیست.', reply_markup=get_manage_servers_keyboard())
    await query.answer()


new_3x_ui_handler = ConversationHandler(
    entry_points=[

    ],
    states={},
    fallbacks=[],
    allow_reentry=True,
)


def register_server_management_handlers(app):
    app.add_handler(CallbackQueryHandler(manage_servers_handler, pattern=r'^admin:manageServers'))
