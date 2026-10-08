# tools/warnings.py — система предупреждений
import os
import json
from datetime import datetime, timedelta


FILE = "warnings.json"
RESET_DAYS = 7
MAX_WARNINGS = 3


def _load() -> dict:
    if not os.path.exists(FILE):
        return {}
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: dict):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _clean_old(data: dict):
    """Обнуляет счётчик, если прошло больше 7 дней без нарушений."""
    now = datetime.now()
    for user, info in data.items():
        last = info.get("last_warning")
        if not last:
            continue
        try:
            dt = datetime.strptime(last, "%d.%m.%Y %H:%M")
        except Exception:
            continue
        if (now - dt) > timedelta(days=RESET_DAYS):
            info["count"] = 0
            info["last_warning"] = None
            info["history"] = []


def warn(user_id: str, reason: str) -> str:
    """Выдаёт предупреждение пользователю. При 3-х — бан."""
    data = _load()
    _clean_old(data)

    if user_id not in data:
        data[user_id] = {"count": 0, "last_warning": None, "history": [], "banned": False}

    if data[user_id].get("banned"):
        return f"🚫 Пользователь {user_id} уже заблокирован."

    data[user_id]["count"] += 1
    data[user_id]["last_warning"] = datetime.now().strftime("%d.%m.%Y %H:%M")
    data[user_id]["history"].append({
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "reason": reason
    })

    count = data[user_id]["count"]

    if count >= MAX_WARNINGS:
        data[user_id]["banned"] = True
        _save(data)
        return (
            f"🚫 Предупреждение {count}/{MAX_WARNINGS}: {reason}\n\n"
            f"Пользователь заблокирован на 30 дней."
        )

    _save(data)
    if count == 1:
        return f"⚠️ Предупреждение 1/{MAX_WARNINGS}: {reason}\nЭто первое предупреждение."
    if count == 2:
        return (
            f"⚠️ Предупреждение 2/{MAX_WARNINGS}: {reason}\n"
            f"Следующее — блокировка на 30 дней.\n"
            f"Если 7 дней без нарушений — счётчик обнулится."
        )
    return f"Предупреждение {count}/{MAX_WARNINGS}: {reason}"


def check_user(user_id: str) -> str:
    """Показывает статус пользователя."""
    data = _load()
    _clean_old(data)
    if user_id not in data:
        return f"Пользователь {user_id}: предупреждений нет"
    info = data[user_id]
    count = info.get("count", 0)
    banned = info.get("banned", False)
    if banned:
        return f"🚫 Пользователь {user_id}: ЗАБЛОКИРОВАН"
    if count == 0:
        return f"✅ Пользователь {user_id}: чисто, предупреждений нет"
    last = info.get("last_warning", "?")
    return f"⚠️ Пользователь {user_id}: {count}/{MAX_WARNINGS} предупреждений. Последнее: {last}"


def unban(user_id: str) -> str:
    """Снимает бан (только для владельца)."""
    data = _load()
    if user_id not in data:
        return f"Пользователь {user_id} не найден"
    data[user_id]["banned"] = False
    data[user_id]["count"] = 0
    data[user_id]["history"] = []
    _save(data)
    return f"✅ Пользователь {user_id} разблокирован"


def list_warned() -> str:
    """Показывает всех с предупреждениями."""
    data = _load()
    _clean_old(data)
    if not data:
        return "Предупреждений ни у кого нет"
    lines = ["📋 Предупреждённые пользователи:"]
    for user, info in data.items():
        count = info.get("count", 0)
        banned = "🚫" if info.get("banned") else "⚠️"
        if count > 0 or info.get("banned"):
            lines.append(f"{banned} {user}: {count}/{MAX_WARNINGS}")
    if len(lines) == 1:
        return "Предупреждений ни у кого нет"
    return "\n".join(lines)


FUNCTIONS = {
    "warn": warn,
    "check_user": check_user,
    "unban": unban,
    "list_warned": list_warned,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "warn",
            "description": "Выдаёт предупреждение пользователю за нарушение. 3 предупреждения — бан",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "ID пользователя"},
                    "reason": {"type": "string", "description": "Причина нарушения"}
                },
                "required": ["user_id", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_user",
            "description": "Показывает статус пользователя (сколько предупреждений, забанен ли)",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "ID пользователя"}
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "unban",
            "description": "Разблокирует пользователя и обнуляет предупреждения. Только для владельца",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "ID пользователя"}
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_warned",
            "description": "Показывает всех пользователей с предупреждениями",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]
