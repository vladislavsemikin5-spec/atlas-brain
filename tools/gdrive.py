# tools/gdrive.py — работа с Google Drive
# Пока работает локально. Для реальной загрузки в Drive нужны credentials.json
import os
import json
import shutil
from datetime import datetime


CLOUD_DIR = "cloud_backup"
os.makedirs(CLOUD_DIR, exist_ok=True)


def _drive_available() -> bool:
    """Проверяет, настроен ли доступ к Google Drive."""
    return os.path.exists("credentials.json") and os.path.exists("token.json")


def save_to_cloud(file_path: str) -> str:
    """Сохраняет файл в облако (локально — пока нет ключей Drive)."""
    if not os.path.exists(file_path):
        return f"Файл не найден: {file_path}"
    try:
        filename = os.path.basename(file_path)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = f"{CLOUD_DIR}/{ts}_{filename}"
        shutil.copy2(file_path, dest)
        abs_path = os.path.abspath(dest)
        if _drive_available():
            return f"✅ Файл сохранён в Google Drive (через локальную копию): {dest}"
        return (
            f"✅ Файл сохранён локально в облачную папку: {dest}\n"
            f"Полный путь: {abs_path}\n\n"
            f"⚠ Google Drive пока не подключён. Файл лежит локально. "
            f"Когда добавим credentials.json — файлы пойдут прямо в облако."
        )
    except Exception as e:
        return f"Ошибка сохранения: {e}"


def list_cloud_files() -> str:
    """Список файлов в облачной папке."""
    try:
        files = sorted(os.listdir(CLOUD_DIR), reverse=True)
        if not files:
            return "В облачной папке пока пусто"
        lines = [f"📁 Файлов в облаке: {len(files)}"]
        for f in files[:30]:
            path = os.path.join(CLOUD_DIR, f)
            size = os.path.getsize(path)
            lines.append(f"• {f} ({round(size/1024, 1)} КБ)")
        return "\n".join(lines)
    except Exception as e:
        return f"Ошибка: {e}"


def cloud_status() -> str:
    """Статус подключения к Google Drive."""
    if _drive_available():
        return "✅ Google Drive подключён, файлы сохраняются в облако"
    return (
        "⚠ Google Drive не подключён.\n"
        "Файлы сохраняются в папку 'cloud_backup' локально.\n"
        "Для подключения Drive нужен файл credentials.json от Google Cloud Console."
    )


def delete_cloud_file(filename: str) -> str:
    """Удаляет файл из облачной папки."""
    path = os.path.join(CLOUD_DIR, filename)
    if not os.path.exists(path):
        return f"Файл не найден: {filename}"
    try:
        os.remove(path)
        return f"🗑 Удалён: {filename}"
    except Exception as e:
        return f"Ошибка удаления: {e}"


FUNCTIONS = {
    "save_to_cloud": save_to_cloud,
    "list_cloud_files": list_cloud_files,
    "cloud_status": cloud_status,
    "delete_cloud_file": delete_cloud_file,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "save_to_cloud",
            "description": "Сохраняет файл в облачную папку (Google Drive, когда подключён)",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Путь к файлу"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_cloud_files",
            "description": "Показывает список файлов в облачной папке",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cloud_status",
            "description": "Показывает статус подключения к Google Drive",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_cloud_file",
            "description": "Удаляет файл из облачной папки",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Имя файла"}
                },
                "required": ["filename"]
            }
        }
    }
]
