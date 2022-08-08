import time
from datetime import datetime


def times_from_to() -> dict:
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


def time_from_sec_to_date(seconds: int) -> str:
    return datetime.fromtimestamp(seconds).strftime("%d-%m")


if __name__ == "__main__":
    print(time_from_sec_to_date(1659773715))
    print(time_from_sec_to_date(1659711475))
    print(time_from_sec_to_date(1659706198))
    print(time_from_sec_to_date(1659216665))
