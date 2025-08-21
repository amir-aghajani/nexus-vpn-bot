from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler

from data import json_storage
from handlers.globals import return_to_main_menu_inline_handler, start_command_handler
from .keyboards import categories_keyboard, finalize_keyboard, plans_keyboard, servers_keyboard

SELECT_CATEGORY, SELECT_PLAN, SELECT_SERVER, FINALIZE = range(4)


async def buy_subscription_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(context.user_data)
    context.user_data['buyPhase'] = {}
    if 'latestConversationMessageId' in context.user_data:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_user.id,
                message_id=context.user_data['latestConversationMessageId']
            )
        except Exception as e:
            print(f"Error deleting message: {e}")
    context.user_data['latestConversationMessageId'] = update.callback_query.message.message_id
    query = update.callback_query

    await query.answer()
    await query.edit_message_text(
        text="لطفاً یک دسته‌بندی انتخاب کنید:",
        reply_markup=categories_keyboard()
    )

    return SELECT_CATEGORY


async def on_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == 'returnToPlans':
        category_id = context.user_data['buyPhase']['categoryId']
    else:
        category_id = query.data
        context.user_data['buyPhase']['categoryId'] = category_id

    await query.edit_message_text(
        text="لطفاً یک پلن انتخاب کنید:",
        reply_markup=plans_keyboard(category_id)
    )
    await query.answer()
    print(context.user_data)

    return SELECT_PLAN


async def on_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == 'returnToCategories':
        return await buy_subscription_start(update, context)

    context.user_data['buyPhase']['planId'] = query.data

    await query.edit_message_text(
        text="لطفاً یک سرور را انتخاب کنید:",
        reply_markup=servers_keyboard()
    )
    await query.answer()
    print(context.user_data)

    return SELECT_SERVER


async def on_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == 'returnToPlans':
        context.user_data['buyPhase'].pop('planId')
        return await on_category(update, context)

    server_id = query.data
    context.user_data['buyPhase']['serverId'] = server_id
    categry_details = json_storage.get('categories', context.user_data['buyPhase']['categoryId'])
    plan_details = json_storage.get('plans', context.user_data['buyPhase']['planId'])
    server_details = json_storage.get('servers', server_id)

    await query.edit_message_text(
        text="اطلاعات خرید شما:\n\n"
             "نام پلن: " + f"{plan_details['name']}\n\n" +
             "لوکیشن سرور: " + f"{server_details['emoji']} {server_details['name']}\n\n" +
             f"پلن: {plan_details['name']}\n\n",
        reply_markup=finalize_keyboard()
    )
    await query.answer()
    print(context.user_data)

    return FINALIZE


async def on_finalize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == 'returnToServers':
        context.user_data['buyPhase'].pop('serverId')
        return await on_plan(update, context)

    if query.data == 'approve':
        categry_details = json_storage.get('categories', context.user_data['buyPhase']['categoryId'])
        plan_details = json_storage.get('plans', context.user_data['buyPhase']['planId'])
        server_details = json_storage.get('servers', context.user_data['buyPhase']['serverId'])
        print(categry_details)
        print(plan_details)
        print(server_details)
    else:
        context.user_data.pop('buyPhase')

    print(context.user_data)

    return ConversationHandler.END


buy_subscription_callback_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(buy_subscription_start, pattern='^user:purchase')],
    states={
        SELECT_CATEGORY: [
            CallbackQueryHandler(on_category, pattern=r'^(?!user:purchase$)(?!returnToMainMenu$).*')
        ],
        SELECT_PLAN: [
            CallbackQueryHandler(on_plan, pattern=r'^(?!user:purchase$)(?!returnToMainMenu$).*')
        ],
        SELECT_SERVER: [
            CallbackQueryHandler(on_server, pattern=r'^(?!user:purchase$)(?!returnToMainMenu$).*')
        ],
        FINALIZE: [
            CallbackQueryHandler(on_finalize, pattern=r'^(?!user:purchase$)(?!returnToMainMenu$).*')
        ],
    },
    fallbacks=[
        return_to_main_menu_inline_handler,
        start_command_handler
    ],
    persistent=True,
    allow_reentry=False,
    name='buy_subscription_conversation_handler',
)
