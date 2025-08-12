from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, filters, MessageHandler
from data import json_storage
from database import categories_db

from handlers.globals import return_to_main_menu_filter, return_to_main_menu_handler, return_to_main_menu_inline_handler, start_command_handler
from keyboards import get_return_to_main_menu_keyboard

ENTER_NEW_NAME = range(1)


async def manage_categories_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split(':')
    action = data[2] if len(data) > 2 else None
    if action == 'delete':
        category_id = data[3] if len(data) > 3 else None
        context.user_data['categoryId'] = category_id

        return
    await query.delete_message()
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='📂 مدیریت دسته‌بندی‌ها\n\n'
             'در این بخش می‌توانید دسته‌بندی‌های مختلف را مدیریت کنید.',
        reply_markup=None
    )
    await query.answer()


async def rename_category_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split(':')
    category_id = data[3]

    context.user_data['categoryId'] = category_id
    await query.edit_message_text(
        text='🔧 لطفاً نام جدید دسته‌بندی را وارد کنید:',
        reply_markup=get_return_to_main_menu_keyboard('نام جدید دسته‌بندی')
    )

    return ENTER_NEW_NAME


async def category_new_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    new_name = message.text.strip()

    category_id = context.user_data.get('categoryId')

    await message.reply_text(
        text=f'✅ نام دسته‌بندی با شناسه {category_id} به "{new_name}" تغییر یافت.',
        reply_to_message_id=message.message_id
    )

    return ConversationHandler.END


rename_category_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(rename_category_entry, pattern=r'^admin:manageCategories:rename:')
    ],
    states={
        ENTER_NEW_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND & ~return_to_main_menu_filter, category_new_name_handler),
        ]
    },
    fallbacks=[
        start_command_handler,
        return_to_main_menu_handler,
        return_to_main_menu_inline_handler
    ],
    allow_reentry=True,
    name='renameCategory',
)
