# tools/search.py — поиск в интернете (DuckDuckGo, без ключей)
try:
    from duckduckgo_search import DDGS
    _OK = True
except Exception:
    _OK = False


def search_web(query: str, max_results: int = 5) -> str:
    """Ищет в интернете, возвращает список результатов."""
    if not _OK:
        return "Инструмент поиска недоступен (библиотека не установлена)"
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = r.get("title", "")
                body = r.get("body", "")
                href = r.get("href", "")
                results.append(f"• {title}\n  {body}\n  {href}")
        if not results:
            return f"По запросу '{query}' ничего не найдено"
        return f"Результаты поиска по '{query}':\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"Ошибка поиска: {e}"


def get_news(topic: str, max_results: int = 5) -> str:
    """Свежие новости по теме."""
    if not _OK:
        return "Инструмент поиска недоступен"
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.news(topic, max_results=max_results):
                title = r.get("title", "")
                body = r.get("body", "")
                date = r.get("date", "")
                source = r.get("source", "")
                results.append(f"• {title} ({source}, {date})\n  {body}")
        if not results:
            return f"Новостей по '{topic}' не найдено"
        return f"Новости по '{topic}':\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"Ошибка новостей: {e}"


FUNCTIONS = {
    "search_web": search_web,
    "get_news": get_news,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Ищет информацию в интернете через DuckDuckGo. Используй для актуальной информации, которой нет в твоих знаниях",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Поисковый запрос"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Возвращает свежие новости по указанной теме",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Тема новостей (например, криптовалюты, технологии)"}
                },
                "required": ["topic"]
            }
        }
    }
]
