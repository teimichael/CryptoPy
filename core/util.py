from datetime import datetime


def str_to_date(date: str) -> datetime:
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')


def date_to_str(date: datetime) -> str:
    return date.strftime('%Y-%m-%d %H:%M:%S')


def str_to_timestamp(date: str) -> int:
    d = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return int(d.timestamp() * 1000)
