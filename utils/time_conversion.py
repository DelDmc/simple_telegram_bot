import time
from datetime import datetime


def times_from_to_current_month() -> dict:
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


def times_from_to_by_days(days_back) -> dict:
    times_dict = {}
    time_to = int(time.time())
    seconds_in_day = 86400
    hours_of_current_day = time.localtime(time_to).tm_hour
    days_to_sec = days_back * seconds_in_day
    times_dict["time_from"] = time_to - days_to_sec - hours_of_current_day
    times_dict["time_to"] = time_to
    return times_dict


def time_from_sec_to_date(seconds: int) -> str:
    return datetime.fromtimestamp(seconds).strftime("%d-%m")


def time_one_day_from_to(day: int, month: int) -> dict:
    times_dict = {}
    seconds_in_day = 86400
    time_struct_from = time.strptime(f"{day}-{month}-22", "%d-%m-%y")
    time_from = int(time.mktime(time_struct_from))
    times_dict['time_from'] = int(time_from)
    times_dict['time_to'] = int(time_from + seconds_in_day)
    return times_dict


if __name__ == "__main__":
    print(times_from_to_by_days(7))
    print("from", time_from_sec_to_date(1659559688))
    print("to", time_from_sec_to_date(1660164511))

    print(times_from_to_by_days(30))
    print("from", time_from_sec_to_date(1657572488))
    print("to", time_from_sec_to_date(1660164511))

    print(time_one_day_from_to(7, 8))
    print("from", time_from_sec_to_date(1659819600))
    print("to", time_from_sec_to_date(1659906000))
