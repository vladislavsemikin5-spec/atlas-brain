# tools/converter.py — конвертер текста
import json
import base64


def to_upper(text: str) -> str:
    """Переводит текст в ВЕРХНИЙ РЕГИСТР."""
    return text.upper()


def to_lower(text: str) -> str:
    """Переводит текст в нижний регистр."""
    return text.lower()


def to_title(text: str) -> str:
    """Делает Каждое Слово С Большой Буквы."""
    return text.title()


def reverse_text(text: str) -> str:
    """Переворачивает текст задом наперёд."""
    return text[::-1]


def count_chars(text: str) -> str:
    """Считает символы, слова, строки."""
    chars = len(text)
    words = len(text.split())
    lines = len(text.split("\n"))
    return f"Символов: {chars}, слов: {words}, строк: {lines}"


def to_base64(text: str) -> str:
    """Кодирует текст в Base64."""
    try:
        return base64.b64encode(text.encode("utf-8")).decode("ascii")
    except Exception as e:
        return f"Ошибка: {e}"


def from_base64(text: str) -> str:
    """Раскодирует Base64 в текст."""
    try:
        return base64.b64decode(text.encode("ascii")).decode("utf-8")
    except Exception as e:
        return f"Ошибка: {e}"


def to_json(text: str) -> str:
    """Форматирует JSON-строку красиво (с отступами)."""
    try:
        data = json.loads(text)
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Ошибка JSON: {e}"


def replace_text(text: str, old: str, new: str) -> str:
    """Заменяет все вхождения одной строки на другую."""
    return text.replace(old, new)


def trim_spaces(text: str) -> str:
    """Убирает лишние пробелы в начале и конце строк."""
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines)


FUNCTIONS = {
    "to_upper": to_upper,
    "to_lower": to_lower,
    "to_title": to_title,
    "reverse_text": reverse_text,
    "count_chars": count_chars,
    "to_base64": to_base64,
    "from_base64": from_base64,
    "to_json": to_json,
    "replace_text": replace_text,
    "trim_spaces": trim_spaces,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "to_upper",
            "description": "Переводит текст в ВЕРХНИЙ РЕГИСТР",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "Текст"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "to_lower",
            "description": "Переводит текст в нижний регистр",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "Текст"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "to_title",
            "description": "Делает Каждое Слово С Большой Буквы",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "Текст"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reverse_text",
            "description": "Переворачивает текст задом наперёд",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "Текст"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "count_chars",
            "description": "Считает количество символов, слов и строк в тексте",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "Текст"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "to_base64",
            "description": "Кодирует текст в Base64",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "Текст"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "from_base64",
            "description": "Раскодирует Base64 в обычный текст",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "Base64-строка"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "to_json",
            "description": "Форматирует JSON-строку красиво с отступами",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "JSON-строка"}},
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "replace_text",
            "description": "Заменяет все вхождения одной строки на другую в тексте",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Исходный текст"},
                    "old": {"type": "string", "description": "Что заменить"},
                    "new": {"type": "string", "description": "На что заменить"}
                },
                "required": ["text", "old", "new"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "trim_spaces",
            "description": "Убирает лишние пробелы в начале и конце каждой строки",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "Текст"}},
                "required": ["text"]
            }
        }
    }
]
