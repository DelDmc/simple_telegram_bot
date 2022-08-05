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
headers = {"X-Token": config("MONOBANK_TOKEN")}
rates = requests.get(url_rates).json()
info = requests.get(url_info, headers=headers).json()


def balance_info():
    message = ""
    for account in info["accounts"]:
        if account["type"] == "black" and account["currencyCode"] == CODE["UAH"]:
            balance_main = account["balance"] // 100
            decimals = account["balance"] % 100
            message = f"Текущий баланс: {balance_main}.{decimals} UAH"
            print(f"{balance_main}.{decimals}")
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



