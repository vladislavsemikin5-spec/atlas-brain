# tools/export.py — экспорт отчётов и данных
import os
import json
import csv
from datetime import datetime


EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)


def save_report(title: str, content: str) -> str:
    """Сохраняет текстовый отчёт в файл."""
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_")[:40].strip().replace(" ", "_")
        if not safe_title:
            safe_title = "report"
        filename = f"{EXPORT_DIR}/{safe_title}_{ts}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n")
            f.write(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
            f.write(content)
        abs_path = os.path.abspath(filename)
        return f"✅ Отчёт сохранён: {filename}\nПолный путь: {abs_path}"
    except Exception as e:
        return f"Ошибка сохранения: {e}"


def save_json(title: str, data_json: str) -> str:
    """Сохраняет JSON-данные в файл."""
    try:
        data = json.loads(data_json)
    except Exception as e:
        return f"Ошибка JSON: {e}"
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_")[:40].strip().replace(" ", "_")
        if not safe_title:
            safe_title = "data"
        filename = f"{EXPORT_DIR}/{safe_title}_{ts}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        abs_path = os.path.abspath(filename)
        return f"✅ JSON сохранён: {filename}\nПолный путь: {abs_path}"
    except Exception as e:
        return f"Ошибка сохранения JSON: {e}"


def save_csv(title: str, csv_text: str) -> str:
    """Сохраняет CSV-данные в файл. csv_text — строки через \\n, разделитель — запятая."""
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_")[:40].strip().replace(" ", "_")
        if not safe_title:
            safe_title = "table"
        filename = f"{EXPORT_DIR}/{safe_title}_{ts}.csv"
        with open(filename, "w", encoding="utf-8", newline="") as f:
            f.write(csv_text)
        abs_path = os.path.abspath(filename)
        return f"✅ CSV сохранён: {filename}\nПолный путь: {abs_path}"
    except Exception as e:
        return f"Ошибка сохранения CSV: {e}"


def list_exports() -> str:
    """Показывает список сохранённых файлов."""
    try:
        files = os.listdir(EXPORT_DIR)
        if not files:
            return "Файлов пока нет"
        files.sort(reverse=True)
        lines = [f"📁 Сохранённых файлов: {len(files)}"]
        for f in files[:20]:
            path = os.path.join(EXPORT_DIR, f)
            size = os.path.getsize(path)
            lines.append(f"• {f} ({size} байт)")
        return "\n".join(lines)
    except Exception as e:
        return f"Ошибка: {e}"


FUNCTIONS = {
    "save_report": save_report,
    "save_json": save_json,
    "save_csv": save_csv,
    "list_exports": list_exports,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "save_report",
            "description": "Сохраняет текстовый отчёт в файл. Используй когда пользователь просит сохранить или экспортировать результат",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Название отчёта"},
                    "content": {"type": "string", "description": "Содержимое отчёта"}
                },
                "required": ["title", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_json",
            "description": "Сохраняет данные в формате JSON",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Название файла"},
                    "data_json": {"type": "string", "description": "JSON-строка с данными"}
                },
                "required": ["title", "data_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_csv",
            "description": "Сохраняет данные в формате CSV (таблица)",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Название файла"},
                    "csv_text": {"type": "string", "description": "CSV-текст: строки через \\n, столбцы через запятую"}
                },
                "required": ["title", "csv_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_exports",
            "description": "Показывает список всех сохранённых файлов",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]
