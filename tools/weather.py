# tools/weather.py — инструмент погоды (wttr.in, без ключей)
import requests


def get_weather(city: str) -> str:
    """Текущая погода в городе."""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return f"Не удалось получить погоду для {city}"
        data = r.json()
        current = data["current_condition"][0]
        temp = current.get("temp_C", "?")
        feels = current.get("FeelsLikeC", "?")
        humidity = current.get("humidity", "?")
        wind = current.get("windspeedKmph", "?")
        desc = current.get("weatherDesc", [{"value": "?"}])[0]["value"]
        return f"Погода в {city}: {desc}, {temp}C (ощущается как {feels}C), влажность {humidity}%, ветер {wind} км/ч."
    except Exception as e:
        return f"Ошибка погоды: {e}"


def get_forecast(city: str) -> str:
    """Прогноз на 3 дня."""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return f"Не удалось получить прогноз для {city}"
        data = r.json()
        weather = data.get("weather", [])[:3]
        lines = [f"Прогноз для {city}:"]
        for day in weather:
            date = day.get("date", "?")
            max_t = day.get("maxtempC", "?")
            min_t = day.get("mintempC", "?")
            hourly = day.get("hourly", [])
            desc = "?"
            if hourly:
                desc = hourly[0].get("weatherDesc", [{"value": "?"}])[0]["value"]
            lines.append(f"{date}: {desc}, от {min_t}C до {max_t}C")
        return "\n".join(lines)
    except Exception as e:
        return f"Ошибка прогноза: {e}"


FUNCTIONS = {
    "get_weather": get_weather,
    "get_forecast": get_forecast,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Возвращает текущую погоду в указанном городе",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Название города, например Москва или London"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_forecast",
            "description": "Возвращает прогноз погоды на 3 дня для указанного города",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Название города"}
                },
                "required": ["city"]
            }
        }
    }
]
