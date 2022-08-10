import os

import telebot.types
from decouple import config
from flask import Flask, request
from telebot import TeleBot, types

from models import User, db
from mono_api import actual_currency_rate, balance_info
from utils import tables
from utils.time_conversion import times_from_to_current_month, times_from_to_by_days

bot = TeleBot(config("TELEGRAM_TOKEN"))
URL = "https://simple-fin-telegram-bot.herokuapp.com/"

bot.set_my_commands(
    [
        telebot.types.BotCommand("/start", "Главное меню"),
        telebot.types.BotCommand("/help", "Описание"),
    ]
)


deny_icon = u"\u274C"
accept_icon = u"\u2705"
authorization_list = {"accept": accept_icon, "deny": deny_icon}


def make_keyboard(options, args=None):
    markup = types.InlineKeyboardMarkup()
    for key, value in options.items():

        markup.add(types.InlineKeyboardButton(text=value, callback_data=f"{key} {args}"))
    return markup


def make_keyboard_for_unauthorized():
    markup = types.ReplyKeyboardMarkup()
    rate_btn = types.KeyboardButton("Курс валюты")
    authorization_btn = types.KeyboardButton("Авторизация")
    markup.row(rate_btn, authorization_btn)
    return markup


def make_first_user_superuser():
    user = User.select().where(User.id == 1).get(db)
    user.is_authorized, user.is_superuser = 1, 1
    user.save()


@bot.message_handler(func=lambda message: message.text == 'Меню Старт')
@bot.message_handler(commands=["start"])
def start_handler(message):
    if not User.select().where(User.chat_id == message.chat.id):
        User.create(
            chat_id=message.chat.id,
            first_name=message.chat.first_name,
            username=message.chat.username
        )
    make_first_user_superuser()
    user = User.select().where(User.chat_id == message.chat.id).get(db)
    if user.is_authorized == 1:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        rate_btn = types.KeyboardButton("Курс валюты")
        balance_btn = types.KeyboardButton("Остаток на счету")
        statement_btn = types.KeyboardButton("Выписка")
        markup.row(rate_btn, balance_btn)
        markup.row(statement_btn)

        bot.send_message(
            chat_id=message.chat.id,
            text="Главное меню",
            reply_markup=markup
        )
    else:
        text_message = "Вы не авторизованы.\nПройдите авторизацию"
        bot.send_message(chat_id=message.chat.id, reply_markup=make_keyboard_for_unauthorized(), text=text_message)


@bot.message_handler(func=lambda message: message.text == 'Авторизация')
def authorization_handler(message):
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


@bot.message_handler(func=lambda message: message.text == 'Выписка')
def statement_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    week_btn = types.KeyboardButton("Выписка за неделю")
    month_btn = types.KeyboardButton("Выписка за 30 дней")
    cur_month_btn = types.KeyboardButton("Выписка за текущий месяц")
    choose_date = types.KeyboardButton("Выписка\nВыбрать день")
    start_btn = types.KeyboardButton("Меню Старт")
    markup.row(week_btn, month_btn)
    markup.row(cur_month_btn, choose_date)
    markup.row(start_btn)
    bot.send_message(
        chat_id=message.chat.id,
        text="Меню выписки",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == 'Выписка за текущий месяц')
def current_month_statement_handler(message):
    user = User.select().where(User.chat_id == message.chat.id).get(db)
    if user.is_authorized == 1:
        time_from_time_to_current_month = times_from_to_current_month()
        table = tables.create_table(time_from_time_to_current_month)
        bot.send_message(chat_id=message.chat.id, text="Готовлю выписку за текущий месяц!")
        bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=f'''<pre>{table}</pre>''')
    else:
        text_message = "Вы не авторизованы.\nПройдите авторизацию"
        bot.send_message(chat_id=message.chat.id, reply_markup=make_keyboard_for_unauthorized(), text=text_message)


@bot.message_handler(func=lambda message: message.text == 'Выписка за неделю' or message.text == 'Выписка за 30 дней')
def current_month_statement_handler(message):
    user = User.select().where(User.chat_id == message.chat.id).get(db)
    time_from_time_to_week = {}
    if user.is_authorized == 1:
        if message.text == 'Выписка за неделю':
            time_from_time_to_week = times_from_to_by_days(7)
            bot.send_message(chat_id=message.chat.id, text="Готовлю выписку за неделю!")
        elif message.text == 'Выписка за 30 дней':
            time_from_time_to_week = times_from_to_by_days(30)
            bot.send_message(chat_id=message.chat.id, text="Готовлю выписку за 30 дней!")

        table = tables.create_table(time_from_time_to_week)
        bot.send_message(chat_id=message.chat.id, parse_mode="HTML", text=f'''<pre>{table}</pre>''')
    else:
        text_message = "Вы не авторизованы.\nПройдите авторизацию"
        bot.send_message(chat_id=message.chat.id, reply_markup=make_keyboard_for_unauthorized(), text=text_message)


@bot.message_handler(func=lambda message: message.text == 'Курс валюты')
def currency_rates_handler(message):
    text_message = actual_currency_rate()
    bot.send_message(chat_id=message.chat.id, text=text_message)


@bot.message_handler(func=lambda message: message.text == 'Остаток на счету')
def actual_balance_handler(message):
    user = User.select().where(User.chat_id == message.chat.id).get(db)
    if user.is_authorized == 1:
        text_message = balance_info()
        bot.send_message(chat_id=message.chat.id, text=text_message)
    else:
        text_message = "Вы не авторизованы.\nПройдите авторизацию"
        bot.send_message(chat_id=message.chat.id, reply_markup=make_keyboard_for_unauthorized(), text=text_message)


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    data = call.data.rsplit(" ")
    if data[1] != "None":
        user_identity = int(data[1])

    if call.data.startswith("accept"):
        user_to_authorize = User.select().where(User.chat_id == user_identity).get(db)
        user_to_authorize.is_authorized = 1
        user_to_authorize.save()
        bot.send_message(chat_id=call.message.chat.id, text="Пользователь авторизован")
        bot.send_message(chat_id=user_identity, text="Поздравляю, Вы авторизованы, все опции доступны.")

    if call.data.startswith("deny"):
        bot.send_message(chat_id=call.message.chat.id, text="Пользователю отказано в авторизации")
        bot.send_message(chat_id=user_identity, text="Извините, Вам отказано в авторизации")


if __name__ == '__main__':
    bot.remove_webhook()
    bot.infinity_polling()

