import time

import requests
from decouple import config

CODE = {
    "UAH": 980,
    "USD": 840,
    "EUR": 978,
    "BGN": 975,
}

url_rates = "https://api.monobank.ua/bank/currency"
url_info = "https://api.monobank.ua/personal/client-info"
url_statement = "https://api.monobank.ua/personal/statement/{}/{}/{}"
headers = {"X-Token": config("MONOBANK_TOKEN")}
rates = requests.get(url_rates).json()
info = requests.get(url_info, headers=headers).json()


def get_statement_info(url, url_headers, account, time_from, time_to):
    statement_data = requests.get(url.format(account, time_from, time_to), headers=url_headers).json()
    return statement_data


def times() -> dict:
    times_dict = {}
    time_to = int(time.time())
    secs_in_day = 86400
    days_of_current_month = time.localtime(time_to).tm_mday
    hours_of_current_day = time.localtime(time_to).tm_hour
    days_to_sec = days_of_current_month * secs_in_day - secs_in_day
    hours_to_sec = hours_of_current_day * 3600
    times_dict["time_from"] = time_to - days_to_sec - hours_to_sec
    times_dict["time_to"] = time_to
    return times_dict


def statement_info():
    r = requests.get(url_statement.format(config("MONOBANK_BLACK_ACCOUNT"),
                                          times()["time_from"], times()["time_to"]), headers=headers)
    statements = r.json()
    for statement in statements:
        print(statement)
    # for statement in statements:
    #     print(statement)


def balance_info():
    message = ""
    for account in info["accounts"]:
        if account["type"] == "black" and account["currencyCode"] == CODE["UAH"]:
            balance_main = account["balance"] // 100
            decimals = account["balance"] % 100
            message = f"Текущий баланс: {balance_main}.{decimals} UAH"
    return message


def actual_currency_rate():
    message = []
    for rate in rates:
        try:
            if rate["currencyCodeA"] == CODE["USD"]:
                message.append(f"КУРС К ГРИВНЕ\n")
                message.append(f"{'=' * 10}\n")
                message.append(f"USD ПОКУПКА / ПРОДАЖА\n{rate['rateBuy']} / {rate['rateSell']}\n")
            if rate["currencyCodeA"] == CODE["EUR"] and rate["currencyCodeB"] == CODE["UAH"]:
                message.append(f"{'=' * 10}\n")
                message.append(f"EUR ПОКУПКА / ПРОДАЖА\n{rate['rateBuy']} / {rate['rateSell']}\n")
            if rate["currencyCodeA"] == CODE["BGN"]:
                message.append(f"{'=' * 10}\n")
                message.append(f"BGN\nКУРС: {rate['rateCross']} UAH\n")
        except (AttributeError, TypeError):
            message = "Слишком частые запросы, попробуй через пару минут"
    message = "".join(message)
    return message


if __name__ == "__main__":
    actual_currency_rate()
    statement_info()
