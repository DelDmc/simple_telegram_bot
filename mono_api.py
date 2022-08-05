"""
USD	840
EUR	978
UAH	980
BGN	975
"""
import requests

CODE = {
    "UAH": 980,
    "USD": 840,
    "EUR": 978,
    "BGN": 975,
}

url = "https://api.monobank.ua/bank/currency"
rates = requests.get(url).json()


def actual_currency_rate():
    message = []
    for rate in rates:
        try:
            if rate["currencyCodeA"] == CODE["USD"]:
                # print(f"{'=' * 10}\n")
                # print(f"USD rate:\nBUY: {rate['rateBuy']} UAH\nSELL: {rate['rateSell']} UAH")
                message.append(f"КУРС К ГРИВНЕ\n")
                message.append(f"{'=' * 10}\n")
                message.append(f"USD ПОКУПКА / ПРОДАЖА\n{rate['rateBuy']} / {rate['rateSell']}\n")
                # print("".join(message))
            if rate["currencyCodeA"] == CODE["EUR"] and rate["currencyCodeB"] == CODE["UAH"]:
                # print(f"{'=' * 10}\n")
                message.append(f"{'=' * 10}\n")
                # print(f"EUR rate:\nBUY: {rate['rateBuy']} UAH\nSELL: {rate['rateSell']} UAH")
                message.append(f"EUR ПОКУПКА / ПРОДАЖА\n{rate['rateBuy']} / {rate['rateSell']}\n")
            if rate["currencyCodeA"] == CODE["BGN"]:
                message.append(f"{'=' * 10}\n")
                # print(f"{'=' * 10}\n")
                # print(f"BGN rate:\nRATECROSS: {rate['rateCross']} UAH")
                message.append(f"BGN\nКУРС: {rate['rateCross']} UAH\n")
        except (AttributeError, TypeError):
            message = "Слишком частые запросы, попробуй через пару минут"
    message = "".join(message)
    return message


if __name__ == "__main__":
    actual_currency_rate()



