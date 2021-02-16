from datetime import datetime


def str_to_date(date: str) -> datetime:
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')


def date_to_str(date: datetime) -> str:
    return date.strftime('%Y-%m-%d %H:%M:%S')


def str_to_timestamp(date: str) -> int:
    d = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return int(d.timestamp() * 1000)


def parse_timeframe(timeframe: str) -> int:
    amount = int(timeframe[0:-1])
    unit = timeframe[-1]
    if 'y' == unit:
        scale = 60 * 60 * 24 * 365
    elif 'M' == unit:
        scale = 60 * 60 * 24 * 30
    elif 'w' == unit:
        scale = 60 * 60 * 24 * 7
    elif 'd' == unit:
        scale = 60 * 60 * 24
    elif 'h' == unit:
        scale = 60 * 60
    elif 'm' == unit:
        scale = 60
    elif 's' == unit:
        scale = 1
    else:
        raise Exception('timeframe unit {} is not supported'.format(unit))
    return amount * scale
