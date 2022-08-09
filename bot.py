import telebot.types
from decouple import config
from telebot import TeleBot, types

from models import User, db
from mono_api import actual_currency_rate, balance_info
from utils import tables

bot = TeleBot(config("TELEGRAM_TOKEN"))
bot.set_my_commands(
    [
        telebot.types.BotCommand("/start", "Главное меню"),
        telebot.types.BotCommand("/rates", "Курс валют"),
        telebot.types.BotCommand("/authorization", "Запрос авторизации"),
        telebot.types.BotCommand("/balance", "Состояние счета"),
        telebot.types.BotCommand("/statement", "Приход/Расход за текущий месяц")
    ]
)

deny_icon = u"\u274C"
accept_icon = u"\u2705"
options_list = {"rates": "Курс валют", "balance": "Остаток на счету", "statement": "Выписка за текущий месяц"}
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
    superuser = User.select().where(User.id == 1).get(db)
    superuser.is_authorized, superuser.is_superuser = 1, 1

    if message.chat.last_name:
        credentials = f"{message.chat.first_name} {message.chat.last_name}"
    else:
        credentials = f"{message.chat.first_name} {message.chat.username}"
    text_message = f"Привет, {credentials}!\nТебя приветствует Finance Bot\n" \
                   f"{'=' * 25}\n" \
                   f"На данный момент доступны следующие команды:\n" \
                   f"/rates - Актуальный курс валют Монобанка\n" \
                   f"/balance - Текущее состояния счета\n" \
                   f"/authorization - Запрос авторизации\n" \
                   f"/statement - Выписка за текущий месяц"
    bot.send_message(chat_id=message.chat.id, text=text_message)
    bot.send_message(chat_id=message.chat.id,
                     text="Доступны следующие опции",
                     reply_markup=make_keyboard(options_list)
                     )


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

    if call.data.startswith("statement"):
        user = User.select().where(User.chat_id == call.message.chat.id).get(db)
        if user.is_authorized == 1:
            bot.send_message(chat_id=call.message.chat.id, text="Готовлю выписку за текущий месяц!")
            bot.send_message(chat_id=call.message.chat.id, parse_mode="HTML",
                             text=f'''<pre>{tables.create_table()}</pre>''')
        else:
            text_message = "Вы не авторизованы.\nИспользуйте команду /authorization"
            bot.send_message(chat_id=call.message.chat.id, reply_markup=make_keyboard(options_list), text=text_message)


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


@bot.message_handler(commands=["statement"])
def show_statement_for_current_month(message):
    user = User.select().where(User.chat_id == message.chat.id).get(db)
    if user.is_authorized == 1:
        table = tables.create_table()
        bot.send_message(chat_id=message.chat.id, text="Готовлю выписку за текущий месяц!")
        bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=f'''<pre>{table}</pre>''')
    else:
        text_message = "Вы не авторизованы.\nИспользуйте команду /authorization"
        bot.send_message(chat_id=message.chat.id, reply_markup=make_keyboard(options_list), text=text_message)


# @bot.message_handler(commands=["test"])
# def test_message(message):
#     bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=f'''<pre>{tables.create_table()}</pre>''')


bot.infinity_polling()
