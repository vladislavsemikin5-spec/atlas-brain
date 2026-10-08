# tools/reminders.py — календарь-запоминалка
import json
import os
from datetime import datetime


FILE = "reminders.json"


def _load():
    if not os.path.exists(FILE):
        return []
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save(items):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def add_reminder(text: str, when: str) -> str:
    """Добавляет напоминание. when — дата и время в формате ДД.ММ.ГГГГ ЧЧ:ММ."""
    try:
        dt = datetime.strptime(when, "%d.%m.%Y %H:%M")
    except Exception:
        return "Неверный формат. Используй ДД.ММ.ГГГГ ЧЧ:ММ (например, 15.10.2026 14:30)"
    items = _load()
    items.append({
        "text": text,
        "when": dt.strftime("%d.%m.%Y %H:%M"),
        "created": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "done": False
    })
    _save(items)
    return f"✅ Напоминание добавлено: «{text}» на {dt.strftime('%d.%m.%Y %H:%M')}"


def list_reminders() -> str:
    """Показывает все напоминания."""
    items = _load()
    if not items:
        return "Напоминаний нет"
    lines = ["📋 Мои напоминания:"]
    for i, r in enumerate(items, 1):
        status = "✓" if r.get("done") else "•"
        lines.append(f"{status} {i}. {r.get('when')} — {r.get('text')}")
    return "\n".join(lines)


def delete_reminder(index: int) -> str:
    """Удаляет напоминание по номеру."""
    items = _load()
    if index < 1 or index > len(items):
        return f"Напоминание №{index} не найдено"
    removed = items.pop(index - 1)
    _save(items)
    return f"🗑 Удалено: «{removed.get('text')}»"


def check_due() -> str:
    """Проверяет, какие напоминания уже наступили."""
    items = _load()
    now = datetime.now()
    due = []
    for r in items:
        if r.get("done"):
            continue
        try:
            dt = datetime.strptime(r.get("when"), "%d.%m.%Y %H:%M")
        except Exception:
            continue
        if dt <= now:
            due.append(r)
    if not due:
        return "Активных напоминаний, время которых уже наступило, нет."
    lines = ["⏰ Наступившие напоминания:"]
    for r in due:
        lines.append(f"• {r.get('when')} — {r.get('text')}")
    return "\n".join(lines)


FUNCTIONS = {
    "add_reminder": add_reminder,
    "list_reminders": list_reminders,
    "delete_reminder": delete_reminder,
    "check_due": check_due,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_reminder",
            "description": "Добавляет напоминание на конкретную дату и время",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Текст напоминания"},
                    "when": {"type": "string", "description": "Когда напомнить, формат ДД.ММ.ГГГГ ЧЧ:ММ"}
                },
                "required": ["text", "when"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_reminders",
            "description": "Показывает все сохранённые напоминания",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_reminder",
            "description": "Удаляет напоминание по его номеру",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer", "description": "Номер напоминания из списка"}
                },
                "required": ["index"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_due",
            "description": "Проверяет, какие напоминания уже наступили по времени",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]
