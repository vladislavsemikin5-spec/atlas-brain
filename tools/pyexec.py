# tools/pyexec.py — безопасный запуск Python-кода
import io
import contextlib
import math

SAFE_BUILTINS = {
    "print": print, "len": len, "range": range, "sum": sum,
    "min": min, "max": max, "abs": abs, "round": round,
    "sorted": sorted, "list": list, "dict": dict, "set": set,
    "tuple": tuple, "str": str, "int": int, "float": float,
    "bool": bool, "enumerate": enumerate, "zip": zip,
    "map": map, "filter": filter, "reversed": reversed,
    "any": any, "all": all, "type": type, "isinstance": isinstance,
}

SAFE_MODULES = {
    "math": math,
}


def _safe_import(name, *args, **kwargs):
    if name in SAFE_MODULES:
        return SAFE_MODULES[name]
    raise ImportError(f"Импорт модуля '{name}' запрещён по соображениям безопасности")


def run_python(code: str) -> str:
    """Выполняет Python-код и возвращает результат.
    Запрещено: файлы, сеть, система. Разрешено: математика, строки, списки."""
    if not code or not code.strip():
        return "Пустой код"
    if len(code) > 4000:
        return "Код слишком длинный (максимум 4000 символов)"

    forbidden = [
        "import os", "import sys", "import subprocess", "import shutil",
        "import socket", "import requests", "import urllib",
        "__import__", "eval(", "exec(", "open(", "compile(",
        "globals(", "locals(", "vars(", "getattr(", "setattr(",
        "delattr(", "input(", "file(", "raw_input("
    ]
    lower = code.lower()
    for f in forbidden:
        if f in lower:
            return f"⛔ Запрещено: '{f.strip()}'. Инструмент не даёт доступ к файлам, системе и сети."

    env = {"__builtins__": dict(SAFE_BUILTINS, __import__=_safe_import)}
    buf = io.StringIO()

    try:
        with contextlib.redirect_stdout(buf):
            exec(code, env)
        output = buf.getvalue()
        if not output:
            output = "(код выполнен, но ничего не вывел — добавь print())"
        return f"✅ Результат:\n{output.strip()}"
    except Exception as e:
        return f"❌ Ошибка выполнения: {type(e).__name__}: {e}"


FUNCTIONS = {
    "run_python": run_python,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Выполняет Python-код и возвращает результат. Используй когда нужен точный расчёт, обработка списка, цикл, или пользователь просит выполнить код. Запрещён доступ к файлам, сети и системе",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python-код для выполнения. Обязательно с print() для вывода"}
                },
                "required": ["code"]
            }
        }
    }
]
