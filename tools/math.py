# tools/math.py — математические инструменты для Атласа

import math as _math


def add(a: float, b: float) -> float:
    """Складывает два числа."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Вычитает второе число из первого."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Умножает два числа."""
    return a * b


def divide(a: float, b: float) -> str:
    """Делит первое число на второе. Проверяет деление на ноль."""
    if b == 0:
        return "Ошибка: на ноль делить нельзя"
    return str(round(a / b, 6))


def power(a: float, b: float) -> float:
    """Возводит число в степень."""
    return a ** b


def sqrt(a: float) -> str:
    """Квадратный корень числа."""
    if a < 0:
        return "Ошибка: нельзя извлечь корень из отрицательного числа"
    return str(round(_math.sqrt(a), 6))


def percent(total: float, pct: float) -> float:
    """Считает процент от числа. percent(200, 15) = 30."""
    return total * pct / 100


FUNCTIONS = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
    "power": power,
    "sqrt": sqrt,
    "percent": percent,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Складывает два числа",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Первое число"},
                    "b": {"type": "number", "description": "Второе число"}
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "subtract",
            "description": "Вычитает второе число из первого",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Уменьшаемое"},
                    "b": {"type": "number", "description": "Вычитаемое"}
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "Умножает два числа",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Первое число"},
                    "b": {"type": "number", "description": "Второе число"}
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "divide",
            "description": "Делит первое число на второе",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Делимое"},
                    "b": {"type": "number", "description": "Делитель"}
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "power",
            "description": "Возводит число в степень",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Число"},
                    "b": {"type": "number", "description": "Степень"}
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sqrt",
            "description": "Квадратный корень числа",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Число"}
                },
                "required": ["a"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "percent",
            "description": "Считает процент от числа. Например, 15 процентов от 200",
            "parameters": {
                "type": "object",
                "properties": {
                    "total": {"type": "number", "description": "Число, от которого считаем"},
                    "pct": {"type": "number", "description": "Процент"}
                },
                "required": ["total", "pct"]
            }
        }
    }
]
