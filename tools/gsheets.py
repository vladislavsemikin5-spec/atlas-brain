# tools/gsheets.py — сохранение заказов и истории (локально, готово к Google Sheets)
import os
import json
from datetime import datetime


DATA_FILE = "sheets_data.json"
os.makedirs("sheets", exist_ok=True)


def _load() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _sheets_available() -> bool:
    return os.path.exists("credentials.json") and os.path.exists("token.json")


def add_record(sheet_name: str, values: str) -> str:
    """Добавляет строку в таблицу. values — значения через | (вертикальная черта)."""
    data = _load()
    if sheet_name not in data:
        data[sheet_name] = []
    row = {
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "values": [v.strip() for v in values.split("|")]
    }
    data[sheet_name].append(row)
    _save(data)
    count = len(data[sheet_name])
    suffix = " (Google Sheets)" if _sheets_available() else " (локально)"
    return f"✅ Запись добавлена в '{sheet_name}'. Всего записей: {count}{suffix}"


def list_records(sheet_name: str) -> str:
    """Показывает все записи из таблицы."""
    data = _load()
    if sheet_name not in data or not data[sheet_name]:
        return f"Таблица '{sheet_name}' пустая"
    rows = data[sheet_name]
    lines = [f"📋 {sheet_name} — записей: {len(rows)}"]
    for i, row in enumerate(rows[-20:], 1):
        vals = " | ".join(row.get("values", []))
        lines.append(f"{i}. [{row.get('date', '?')}] {vals}")
    return "\n".join(lines)


def list_sheets() -> str:
    """Показывает список всех таблиц."""
    data = _load()
    if not data:
        return "Таблиц пока нет"
    lines = ["📊 Таблицы:"]
    for name, rows in data.items():
        lines.append(f"• {name} — {len(rows)} записей")
    return "\n".join(lines)


def delete_record(sheet_name: str, index: int) -> str:
    """Удаляет запись по номеру."""
    data = _load()
    if sheet_name not in data:
        return f"Таблица '{sheet_name}' не найдена"
    rows = data[sheet_name]
    if index < 1 or index > len(rows):
        return f"Запись №{index} не найдена"
    removed = rows.pop(index - 1)
    data[sheet_name] = rows
    _save(data)
    return f"🗑 Удалена запись: {' | '.join(removed.get('values', []))}"


def sheets_status() -> str:
    """Статус подключения к Google Sheets."""
    data = _load()
    total = sum(len(v) for v in data.values())
    if _sheets_available():
        return f"✅ Google Sheets подключён. Таблиц: {len(data)}, записей: {total}"
    return (
        f"⚠ Google Sheets не подключён. Локально: таблиц — {len(data)}, записей — {total}.\n"
        f"Данные хранятся в файле {DATA_FILE}.\n"
        f"Для подключения нужны credentials.json и token.json от Google Cloud."
    )


FUNCTIONS = {
    "add_record": add_record,
    "list_records": list_records,
    "list_sheets": list_sheets,
    "delete_record": delete_record,
    "sheets_status": sheets_status,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_record",
            "description": "Добавляет запись в таблицу. Используй для сохранения заказов, клиентов, истории. values — значения через |",
            "parameters": {
                "type": "object",
                "properties": {
                    "sheet_name": {"type": "string", "description": "Название таблицы (например, 'Заказы', 'Клиенты')"},
                    "values": {"type": "string", "description": "Значения через |. Например: 'Иван|Купил сайт|50000'"}
                },
                "required": ["sheet_name", "values"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_records",
            "description": "Показывает записи из таблицы",
            "parameters": {
                "type": "object",
                "properties": {
                    "sheet_name": {"type": "string", "description": "Название таблицы"}
                },
                "required": ["sheet_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_sheets",
            "description": "Показывает список всех таблиц",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_record",
            "description": "Удаляет запись из таблицы по номеру",
            "parameters": {
                "type": "object",
                "properties": {
                    "sheet_name": {"type": "string", "description": "Название таблицы"},
                    "index": {"type": "integer", "description": "Номер записи"}
                },
                "required": ["sheet_name", "index"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sheets_status",
            "description": "Статус подключения к Google Sheets",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]
