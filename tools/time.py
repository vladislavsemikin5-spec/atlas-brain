# tools/time.py — инструменты времени и даты
from datetime import datetime, timezone, timedelta


def get_time() -> str:
    """Текущее время (Москва, UTC+3)."""
    moscow = timezone(timedelta(hours=3))
    now = datetime.now(moscow)
    return now.strftime("%H:%M:%S")


def get_date() -> str:
    """Текущая дата (Москва)."""
    moscow = timezone(timedelta(hours=3))
    now = datetime.now(moscow)
    return now.strftime("%d.%m.%Y")


def get_datetime() -> str:
    """Текущие дата и время (Москва)."""
    moscow = timezone(timedelta(hours=3))
    now = datetime.now(moscow)
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    return f"{days[now.weekday()]}, {now.strftime('%d.%m.%Y %H:%M:%S')} (МСК)"


def get_day_of_week() -> str:
    """Текущий день недели."""
    moscow = timezone(timedelta(hours=3))
    now = datetime.now(moscow)
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    return days[now.weekday()]


FUNCTIONS = {
    "get_time": get_time,
    "get_date": get_date,
    "get_datetime": get_datetime,
    "get_day_of_week": get_day_of_week,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Возвращает текущее время в Москве (МСК)",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_date",
            "description": "Возвращает текущую дату в Москве",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "Возвращает текущие дату и время в Москве, включая день недели",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_day_of_week",
            "description": "Возвращает текущий день недели",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]
