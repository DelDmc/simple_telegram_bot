import prettytable as pt
from mono_api import statement_info
from utils.time_conversion import time_from_sec_to_date, times_from_to_current_month, times_from_to_by_days


def create_table(times_func):
    statement_json = statement_info(times_func)
    table = pt.PrettyTable(["Дата", "Сумма", "Описание"])
    table.align["Date"] = "c"
    table.align["Sum"] = "r"
    table.align["Description"] = "r"
    data = []
    for statement in statement_json:
        data.append(
            (
                time_from_sec_to_date(statement["time"]),
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
    print(create_table(times_from_to_current_month()))
    print(create_table(times_from_to_by_days(7)))


