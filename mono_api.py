import requests
from decouple import config

from utils.time_conversion import times_from_to_current_month

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


def statement_info(times_func):
    r = requests.get(
        url_statement.format(
            config(
                "MONOBANK_BLACK_ACCOUNT"
            ),
            times_func["time_from"],
            times_func["time_to"]),
        headers=headers
    )
    return r.json()


def balance_info():
    message = ""
    info = requests.get(url_info, headers=headers).json()
    for account in info["accounts"]:
        if account["type"] == "black" and account["currencyCode"] == CODE["UAH"]:
            balance = round(account["balance"] / 100, 2)
            message = f"Текущий баланс: {balance} UAH"
    return message


def actual_currency_rate():
    return requests.get(url_rates).json()


if __name__ == "__main__":
    actual_currency_rate()
