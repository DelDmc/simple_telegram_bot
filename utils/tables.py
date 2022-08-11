import prettytable as pt
from mono_api import statement_info, actual_currency_rate, CODE
from utils.time_conversion import time_from_sec_to_date, times_from_to_current_month, times_from_to_by_days


def create_rates_table():
    rates = actual_currency_rate()
    limited_rates = []
    for rate in rates:
        try:
            if rate["currencyCodeA"] == CODE["USD"]:
                limited_rates.append(rate)
            if rate["currencyCodeA"] == CODE["EUR"] and rate["currencyCodeB"] == CODE["UAH"]:
                limited_rates.append(rate)
            if rate["currencyCodeA"] == CODE["BGN"]:
                limited_rates.append(rate)
        except (AttributeError, TypeError):
            return "Слишком частые запросы, попробуй через пару минут"

    table_rates = pt.PrettyTable(
        field_names=["---", "ПОКУПКА", "ПРОДАЖА"], border=False)

    buy_usd = limited_rates[0]['rateBuy']
    sell_usd = limited_rates[0]['rateSell']
    table_rates.add_row(["USD", buy_usd, sell_usd])

    buy_eur = limited_rates[1]['rateBuy']
    sell_eur = limited_rates[1]['rateSell']
    table_rates.add_row(["EUR", buy_eur, sell_eur])

    rate_bgn = limited_rates[2]['rateCross']
    table_rates.add_row(["===", "===", "======="])
    table_rates.add_row(["КУРС", "BGN", rate_bgn])

    return table_rates


def create_statement_table(times_func):
    statement_json = statement_info(times_func)
    table = pt.PrettyTable(["Дата", "Сумма", "Описание"])
    table.align["Date"] = "c"
    table.align["Sum"] = "r"
    table.align["Description"] = "r"
    data = []
    for statement in statement_json:
        data.append(
            (
                time_from_sec_to_date(int(statement["time"])),
                f"{round(statement['amount']/100, 2)}",
                statement['description'][:15]
            )
        )
    for date, sum, description in data:
        table.add_row(
            [
                date,
                f'{sum}',
                f'{description}'
            ]
        )
    return table


if __name__ == "__main__":
    # print(create_statement_table(times_from_to_current_month()))
    # print(create_statement_table(times_from_to_by_days(7)))
    # limited_rates = [
    #     rate for rate in rates if rate["currencyCodeA"] == CODE["USD"] or
    #     (rate["currencyCodeA"] == CODE["EUR"] and rate["currencyCodeB"] == CODE["UAH"]) or
    #     rate["currencyCodeA"] == CODE["BGN"]
    # ]
    # print(limited_rates)
    print(create_rates_table())

