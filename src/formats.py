from datetime import datetime as dt

from settings import date_format, time_format


def date_to_text(date):
    return dt.strftime(date, date_format)


def text_to_date(text_date):
    return dt.strptime(text_date, date_format)


def time_to_text(time):
    return dt.strftime(time, time_format)


def text_to_time(text_time):
    return dt.strptime(text_time, time_format)
