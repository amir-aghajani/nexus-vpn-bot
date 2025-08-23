from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, filters, MessageHandler

from data import json_storage
from handlers.globals import return_to_main_menu_filter, return_to_main_menu_handler, return_to_main_menu_inline_handler, start_command_handler
from keyboards import get_return_to_main_menu_keyboard, manage_categories_keyboard

ENTER_CATEGORY_NAME = range(1)

ENTER_NEW_NAME = range(1)


async def manage_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.delete_message()
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='📂 مدیریت دسته‌بندی‌ها\n\n'
             'در این بخش می‌توانید دسته‌بندی‌های مختلف را مدیریت کنید.',
        reply_markup=manage_categories_keyboard(json_storage.get('categories'))
    )
    await query.answer()


async def new_category_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.delete_message()

    await context.bot.send_message(
        text='✏️ لطفاً نام دسته‌بندی جدید را وارد کنید:',
        chat_id=update.effective_user.id,
        reply_markup=get_return_to_main_menu_keyboard('نام جدید دسته‌بندی')
    )

    return ENTER_NEW_NAME


async def new_category_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    cat_name = message.text.strip()
    cat_id = categories_db.create({'name': cat_name})
    json_storage.add('categories', {'id': cat_id, 'name': cat_name})

    await message.reply_text(
        text=f'✅ دسته‌بندی با موفقیت ایجاد شد!',
        reply_to_message_id=message.message_id,
        reply_markup=manage_categories_keyboard(json_storage.get('categories')),
    )

    return ConversationHandler.END


async def category_rename_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split(':')

    context.user_data['categoryId'] = data[2]
    await query.delete_message()
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='✏️ لطفاً نام جدید دسته‌بندی را وارد کنید:',
        reply_markup=get_return_to_main_menu_keyboard('نام جدید دسته‌بندی')
    )

    return ENTER_NEW_NAME


async def category_rename_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    new_name = message.text.strip()
    category_id = context.user_data.get('categoryId')

    categories_db.update(category_id, {'name': new_name})
    json_storage.update('categories', category_id, {'name': new_name})

    await message.reply_text(
        text=f'✅ نام دسته‌بندی به {new_name} تغییر یافت!',
        reply_to_message_id=message.message_id,
        reply_markup=manage_categories_keyboard(json_storage.get('categories')),
    )

    return ConversationHandler.END


async def delete_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split(':')
    category_id = data[2]

    if categories_db.delete(category_id):
        json_storage.remove('categories', category_id)
        await query.edit_message_text(
            text='✅ دسته‌بندی با موفقیت حذف شد.',
            reply_markup=manage_categories_keyboard(json_storage.get('categories'))
        )
    else:
        await query.answer('❌ خطا در حذف دسته‌بندی', show_alert=True)


create_category_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(new_category_entry, pattern=r'^admin:createCategory')
    ],
    states={
        ENTER_CATEGORY_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND & ~return_to_main_menu_filter, new_category_name_handler),
        ]
    },
    fallbacks=[
        start_command_handler,
        return_to_main_menu_handler,
        return_to_main_menu_inline_handler
    ],
    allow_reentry=True,
    name='new_category_handler'
)

rename_category_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(category_rename_entry, pattern=r'^admin:renameCategory:'),
    ],
    states={
        ENTER_NEW_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND & ~return_to_main_menu_filter, category_rename_handler),
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