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
        telebot.types.BotCommand("/balance", "Actual balance")
    ]
)

deny_icon = u"\u274C"
accept_icon = u"\u2705"
options_list = {"rates": "Курс валют", "balance": "Остаток на счету"}
authorization_list = {"accept": accept_icon, "deny": deny_icon}


def make_keyboard(options, args=None):
    markup = types.InlineKeyboardMarkup()
    for key, value in options.items():
        markup.add(types.InlineKeyboardButton(text=value, callback_data=f"{key} {args}"))
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
    text_message = f"Привет, {credentials}!\nТебя приветствует Finance Bot\n" \
                   f"{'=' * 25}\n" \
                   f"На данный момент доступны следующие команды:\n" \
                   f"/rates - Актуальный курс валют Монобанка\n" \
                   f"/balance - Текущее состояния счета\n" \
                   f"/authorization - Запрос авторизации\n"
    bot.send_message(chat_id=message.chat.id, text=text_message)
    bot.send_message(chat_id=message.chat.id,
                     text="Доступны следующие опции",
                     reply_markup=make_keyboard(options_list),
                     parse_mode='HTML')


@bot.message_handler(commands=["authorization"])
def request_for_authorization(message):
    superuser = User.select().where(User.is_superuser == 1).get(db)
    user = User.select().where(User.chat_id == message.chat.id).get(db)

    if user.is_authorized != 1:
        bot.send_message(
            chat_id=superuser.chat_id,
            text=f"{message.chat.id} Запрос авторизации от {message.chat.first_name} {message.chat.username}"
                 f"\nАвторизовать?",
            reply_markup=make_keyboard(authorization_list, message.chat.id),
            parse_mode='HTML'
        )
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Запрос авторизации отправлен на рассмотрение. Ожидайте..."
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Вы прошли авторизацию. Все опции доступны."
        )


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    data = call.data.rsplit(" ")
    if data[1] != "None":
        user_identity = int(data[1])

    if call.data.startswith("rates"):
        text_message = actual_currency_rate()
        bot.send_message(chat_id=call.message.chat.id, reply_markup=make_keyboard(options_list), text=text_message)

    if call.data.startswith("balance"):
        user = User.select().where(User.chat_id == call.message.chat.id).get(db)
        if user.is_authorized == 1:
            text_message = balance_info()
            bot.send_message(chat_id=call.message.chat.id, reply_markup=make_keyboard(options_list), text=text_message)
        else:
            text_message = "Вы не авторизованы.\nИспользуйте команду /authorization"
            bot.send_message(chat_id=call.message.chat.id, reply_markup=make_keyboard(options_list), text=text_message)

    if call.data.startswith("accept"):
        user_to_authorize = User.select().where(User.chat_id == user_identity).get(db)
        user_to_authorize.is_authorized = 1
        user_to_authorize.save()
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Пользователь авторизован"
        )
        bot.send_message(
            chat_id=user_identity,
            text="Поздравляю, Вы авторизованы, все опции доступны."
        )
        bot.send_message(
            chat_id=user_identity,
            text="Доступны следующие опции",
            reply_markup=make_keyboard(options_list),
            parse_mode='HTML'
        )

    if call.data.startswith("deny"):
        bot.send_message(chat_id=call.message.chat.id, text="Пользователю отказано в авторизации")
        bot.send_message(chat_id=user_identity, text="Извините, Вам отказано в авторизации")


@bot.message_handler(commands=["rates"])
def show_currency_rates(message):
    bot.send_message(chat_id=message.chat.id, text="Я проверю для тебя курсы валют!")
    text_message = actual_currency_rate()
    bot.send_message(chat_id=message.chat.id, text=text_message)


@bot.message_handler(commands=["balance"])
def show_currency_rates(message):
    user = User.select().where(User.chat_id == message.chat.id).get(db)
    if user.is_authorized == 1:
        bot.send_message(chat_id=message.chat.id, text="Я проверю для тебя состояние счета!")
        text_message = balance_info()
        bot.send_message(chat_id=message.chat.id, text=text_message)
    else:
        text_message = "Вы не авторизованы.\nИспользуйте команду /authorization"
        bot.send_message(chat_id=message.chat.id, reply_markup=make_keyboard(options_list), text=text_message)


bot.infinity_polling()
