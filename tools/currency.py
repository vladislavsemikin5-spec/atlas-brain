# tools/currency.py — курсы валют (open.er-api.com, без ключей)
import requests

_CACHE = {"data": None, "time": 0}
_CACHE_TTL = 3600


def _get_rates():
    import time
    now = time.time()
    if _CACHE["data"] and (now - _CACHE["time"]) < _CACHE_TTL:
        return _CACHE["data"]
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=15)
        if r.status_code != 200:
            return None
        data = r.json()
        if data.get("result") != "success":
            return None
        _CACHE["data"] = data.get("rates", {})
        _CACHE["time"] = now
        return _CACHE["data"]
    except Exception:
        return None


def convert(amount: float, from_currency: str, to_currency: str) -> str:
    """Конвертирует сумму из одной валюты в другую."""
    rates = _get_rates()
    if not rates:
        return "Не удалось получить курсы валют"
    f = from_currency.upper()
    t = to_currency.upper()
    if f not in rates:
        return f"Валюта {f} не найдена"
    if t not in rates:
        return f"Валюта {t} не найдена"
    usd_amount = amount / rates[f]
    result = usd_amount * rates[t]
    return f"{amount} {f} = {round(result, 2)} {t}"


def get_rate(from_currency: str, to_currency: str) -> str:
    """Возвращает курс одной валюты к другой."""
    rates = _get_rates()
    if not rates:
        return "Не удалось получить курсы валют"
    f = from_currency.upper()
    t = to_currency.upper()
    if f not in rates:
        return f"Валюта {f} не найдена"
    if t not in rates:
        return f"Валюта {t} не найдена"
    usd_amount = 1 / rates[f]
    result = usd_amount * rates[t]
    return f"1 {f} = {round(result, 4)} {t}"


def get_popular() -> str:
    """Популярные курсы к рублю."""
    rates = _get_rates()
    if not rates:
        return "Не удалось получить курсы валют"
    if "RUB" not in rates:
        return "Рубль не найден в списке"
    rub = rates["RUB"]
    lines = ["Курсы к рублю:"]
    for code, name in [("USD", "Доллар"), ("EUR", "Евро"), ("CNY", "Юань"), ("GBP", "Фунт")]:
        if code in rates:
            value = rub / rates[code]
            lines.append(f"{name} ({code}): {round(value, 2)} ₽")
    return "\n".join(lines)


FUNCTIONS = {
    "convert": convert,
    "get_rate": get_rate,
    "get_popular": get_popular,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "convert",
            "description": "Конвертирует сумму из одной валюты в другую. Например, 100 долларов в рубли",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Сумма"},
                    "from_currency": {"type": "string", "description": "Из какой валюты (USD, EUR, RUB и т.д.)"},
                    "to_currency": {"type": "string", "description": "В какую валюту (USD, EUR, RUB и т.д.)"}
                },
                "required": ["amount", "from_currency", "to_currency"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_rate",
            "description": "Возвращает текущий курс одной валюты к другой",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {"type": "string", "description": "Валюта (USD, EUR, RUB)"},
                    "to_currency": {"type": "string", "description": "Валюта (USD, EUR, RUB)"}
                },
                "required": ["from_currency", "to_currency"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_popular",
            "description": "Возвращает популярные курсы валют к рублю (доллар, евро, юань, фунт)",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]
