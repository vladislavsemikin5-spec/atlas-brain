# tools/calendar.py — экономический календарь
from datetime import datetime, timedelta


def _next_weekday(target_weekday: int) -> datetime:
    """Ближайший день недели (0=Пн, 6=Вс)."""
    today = datetime.now()
    days = (target_weekday - today.weekday()) % 7
    if days == 0:
        days = 7
    return today + timedelta(days=days)


def get_key_events() -> str:
    """Ключевые регулярные события на ближайшие дни."""
    moscow = datetime.now()
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    events = []

    # Заседания ФРС — обычно среда
    fed = _next_weekday(2)
    events.append((fed, "Заседание ФРС (FOMC)", "Высокое"))

    # ЕЦБ — обычно четверг
    ecb = _next_weekday(3)
    events.append((ecb, "Заседание ЕЦБ", "Высокое"))

    # Данные по безработице США — четверг
    nfp = _next_weekday(3)
    events.append((nfp, "Заявки на пособия США", "Среднее"))

    # PMI Германии — понедельник
    pmi = _next_weekday(0)
    events.append((pmi, "Индекс PMI Германии", "Среднее"))

    # Отчёты крупных компаний — пятница
    earnings = _next_weekday(4)
    events.append((earnings, "Отчёты крупных компаний", "Среднее"))

    events.sort(key=lambda x: x[0])

    lines = ["📅 Ключевые события (МСК):"]
    for date, name, impact in events[:5]:
        d = date.strftime("%d.%m")
        wd = days[date.weekday()]
        lines.append(f"• {wd} {d} — {name} [{impact}]")
    return "\n".join(lines)


def get_events_for_date(date_str: str) -> str:
    """События на конкретную дату (формат ДД.ММ.ГГГГ)."""
    try:
        target = datetime.strptime(date_str, "%d.%m.%Y")
    except Exception:
        return "Неверный формат даты. Используй ДД.ММ.ГГГГ"
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    wd = days[target.weekday()]
    return f"На {target.strftime('%d.%m.%Y')} ({wd}) крупных регулярных событий обычно нет. Проверь Investing.com для точного календаря."


def get_today_info() -> str:
    """Информация о сегодняшнем дне."""
    now = datetime.now()
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    return f"Сегодня {days[now.weekday()]}, {now.strftime('%d.%m.%Y')}, время {now.strftime('%H:%M')} МСК."


FUNCTIONS = {
    "get_key_events": get_key_events,
    "get_events_for_date": get_events_for_date,
    "get_today_info": get_today_info,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_key_events",
            "description": "Возвращает ключевые экономические события на ближайшие дни (ФРС, ЕЦБ, макро-данные, отчёты)",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_events_for_date",
            "description": "Возвращает экономические события на конкретную дату",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {"type": "string", "description": "Дата в формате ДД.ММ.ГГГГ"}
                },
                "required": ["date_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_today_info",
            "description": "Возвращает информацию о сегодняшнем дне: дата, день недели, время",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]
