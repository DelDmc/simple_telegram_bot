import telebot.types
from decouple import config
from telebot import TeleBot, types

from models import User, db
from mono_api import actual_currency_rate, balance_info

bot = TeleBot(config("TELEGRAM_TOKEN"))
bot.set_my_commands(
    [
        telebot.types.BotCommand("/start", "Main menu"),
        telebot.types.BotCommand("/rates", "Rates"),
        telebot.types.BotCommand("/authorization", "Authorization request"),
    ]
)

deny_icon = u"\u274C"
accept_icon = u"\u2705"
options_list = {"rates": "Курс валют", "balance": "Остаток на счету"}
authorization_list = {"accept": accept_icon, "deny": deny_icon}


def make_keyboard(options):
    markup = types.InlineKeyboardMarkup()
    for key, value in options.items():
        markup.add(types.InlineKeyboardButton(text=value, callback_data=f"{key}"))
        print(f"{key}")
    return markup


@bot.message_handler(commands=["start"])
def start_handler(message):
    if not User.select().where(User.chat_id == message.chat.id):
        User.create(
            chat_id=message.chat.id,
            first_name=message.chat.first_name,
            username=message.chat.username
        )
    if message.chat.last_name:
        credentials = f"{message.chat.first_name} {message.chat.last_name}"
    else:
        credentials = f"{message.chat.first_name} {message.chat.username}"
    bot.send_message(chat_id=message.chat.id, text=f"Привет, {credentials}!\nТебя приветствует Finance Bot\n")
    bot.send_message(chat_id=message.chat.id,
                     text="Доступны следующие опции",
                     reply_markup=make_keyboard(options_list),
                     parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data.startswith("rates"):
        text_message = actual_currency_rate()
        bot.send_message(chat_id=call.message.chat.id, reply_markup=make_keyboard(options_list), text=text_message)
        # bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=text_message)
    if call.data.startswith("balance"):
        print(User.chat_id)
        user = User.select().where(User.chat_id == call.message.chat.id).get(db)
        print(user)
        if user.is_authorized == 1:
            text_message = balance_info()
            bot.send_message(chat_id=call.message.chat.id, reply_markup=make_keyboard(options_list), text=text_message)
        else:
            text_message = "Вы не авторизированы.\nВведите в чате команду '/authorization'"
            bot.send_message(chat_id=call.message.chat.id, reply_markup=make_keyboard(options_list), text=text_message)


@bot.message_handler(commands=["authorization"])
def request_for_authorization(message):
    # su_chat_id = get_superuser_chat_id()
    bot.send_message(
        chat_id=458837540,
        text=f"{message.chat.id} Запрос авторизации от {message.chat.first_name} {message.chat.username}"
    )
    msg = bot.send_message(chat_id=458837540,
                           text="Авторизовать?",
                           reply_markup=make_keyboard(authorization_list),
                           parse_mode='HTML')
    bot.register_next_step_handler(msg, handle_authorization_request)
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Запрос авторизации отправлен на рассмотрение. Ожидайте..."
    )


# @bot.callback_query_handler(func=lambda call: True)
def handle_authorization_request(call):
    print(call)
    # if call.data.startswith("accept"):
    #     print("1", call)
    #     print("Accept", callback.message.chat.id)
    #     bot.send_message(chat_id=1370609777, reply_markup=make_keyboard(authorization_list), text="accepted")
    # if callback.data.startswith("deny"):
    #     print("Deny", callback.message.chat.id)


@bot.message_handler(commands=["rates"])
def show_currency_rates(message):
    bot.send_message(chat_id=message.chat.id, text="Я проверю для тебя курсы валют!")
    text_message = actual_currency_rate()
    bot.send_message(chat_id=message.chat.id, text=text_message)


bot.infinity_polling()
