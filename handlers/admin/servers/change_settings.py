from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, filters, MessageHandler

from database import servers_db
from keyboards import get_return_to_main_menu_keyboard

ENTER_NEW_VALUE = range(1)

changeables = {
    'name': 'نام سرور',
    'limit': 'محدودیت سرور',
    'emoji': 'ایموجی سرور',
    'panelUrl': 'آدرس پنل',
    'panelUsername': 'نام کاربری پنل',
    'panelPassword': 'رمز عبور پنل'
}


async def change_settings_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split(':')
    context.user_data['settingToChange'] = data[2]
    context.user_data['serverId'] = data[3]

    await query.delete_message()
    await context.bot.send_message(
        text='🔧 لطفاً ' + changeables[data[2]] + ' را وارد کنید:',
        chat_id=query.message.chat.id,
        reply_markup=get_return_to_main_menu_keyboard(changeables[data[2]])
    )
    await query.answer()

    return ENTER_NEW_VALUE


async def change_setting_value_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    new_value = message.text.strip()
    setting_to_change = context.user_data['settingToChange']
    server_id = context.user_data.get['serverId']
    servers_db.update(server_id=server_id, server_data={setting_to_change: new_value})

    await message.reply_text(
        text=f'✅ {changeables[setting_to_change]} با موفقیت تغییر یافت به: {new_value}',
        reply_to_message_id=message.message_id,
        reply_markup=get_return_to_main_menu_keyboard()
    )

    return ConversationHandler.END


async def toggle_setting_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split(':')

    context.bot.send_message(
        chat_id=query.message.chat.id,
        text=f'✅ تنظیم {data[1]} با موفقیت تغییر یافت.',
        reply_markup=None
    )

    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(change_settings_entry, pattern='^admin:editSetting:')],
    states={
        ENTER_NEW_VALUE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, change_settings_entry)
        ]
    },
    fallbacks=[],
    name='change_settings',
    persistent=True
)
