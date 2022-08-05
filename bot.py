from decouple import config
from telebot import TeleBot, types

from models import User
from mono_api import actual_currency_rate

bot = TeleBot(config("TELEGRAM_TOKEN"))


stringList = {"rates": "Курс валют", "balance": "Остаток на счету"}
crossIcon = u"\u274C"


def make_keyboard():
    markup = types.InlineKeyboardMarkup()
    for key, value in stringList.items():
        markup.add(types.InlineKeyboardButton(text=value,
                                              callback_data=f"{key} {value}"))
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
                     reply_markup=make_keyboard(),
                     parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data.startswith("rates"):
        text_message = actual_currency_rate()
        bot.send_message(chat_id=call.message.chat.id, reply_markup=make_keyboard(), text=text_message)
        # bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=text_message)


@bot.message_handler(commands=["rates"])
def show_currency_rates(message):
    bot.send_message(chat_id=message.chat.id, text="Я проверю для тебя курсы валют!")
    text_message = actual_currency_rate()
    bot.send_message(chat_id=message.chat.id, text=text_message)


bot.infinity_polling()
