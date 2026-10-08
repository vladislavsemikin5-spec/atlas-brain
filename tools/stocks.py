# tools/stocks.py — данные акций (yfinance, без ключей)
try:
    import yfinance as yf
    _OK = True
except Exception:
    _OK = False


def get_stock_price(ticker: str) -> str:
    """Текущая цена акции и изменение за день."""
    if not _OK:
        return "Инструмент акций недоступен (yfinance не установлен)"
    try:
        t = yf.Ticker(ticker.upper())
        info = t.info
        price = info.get("regularMarketPrice") or info.get("currentPrice")
        prev = info.get("regularMarketPreviousClose") or info.get("previousClose")
        name = info.get("shortName") or ticker.upper()
        if price is None:
            return f"Не удалось получить цену {ticker}"
        change_pct = "?"
        if prev:
            change_pct = round((price - prev) / prev * 100, 2)
        sign = "+" if str(change_pct).startswith("-") is False else ""
        return f"📈 {name} ({ticker.upper()}): ${round(price, 2)}, за день: {sign}{change_pct}%"
    except Exception as e:
        return f"Ошибка: {e}"


def get_stock_info(ticker: str) -> str:
    """Базовая информация о компании."""
    if not _OK:
        return "Инструмент недоступен"
    try:
        t = yf.Ticker(ticker.upper())
        info = t.info
        name = info.get("shortName") or ticker.upper()
        sector = info.get("sector", "?")
        industry = info.get("industry", "?")
        country = info.get("country", "?")
        market_cap = info.get("marketCap")
        pe = info.get("trailingPE", "?")
        div = info.get("dividendYield", "?")
        lines = [
            f"🏢 {name} ({ticker.upper()})",
            f"Сектор: {sector}",
            f"Отрасль: {industry}",
            f"Страна: {country}",
        ]
        if market_cap:
            lines.append(f"Капитализация: ${round(market_cap / 1e9, 2)} млрд")
        lines.append(f"P/E: {pe}")
        lines.append(f"Дивиденды: {div}")
        return "\n".join(lines)
    except Exception as e:
        return f"Ошибка: {e}"


def compare_stocks(ticker1: str, ticker2: str) -> str:
    """Сравнивает две акции."""
    if not _OK:
        return "Инструмент недоступен"
    try:
        t1 = yf.Ticker(ticker1.upper())
        t2 = yf.Ticker(ticker2.upper())
        i1 = t1.info
        i2 = t2.info
        p1 = i1.get("regularMarketPrice", 0)
        p2 = i2.get("regularMarketPrice", 0)
        pe1 = i1.get("trailingPE", "?")
        pe2 = i2.get("trailingPE", "?")
        mc1 = i1.get("marketCap", 0)
        mc2 = i2.get("marketCap", 0)
        return (
            f"Сравнение {ticker1.upper()} и {ticker2.upper()}:\n"
            f"{ticker1.upper()}: ${round(p1, 2)}, P/E {pe1}, капитализация ${round(mc1 / 1e9, 2)} млрд\n"
            f"{ticker2.upper()}: ${round(p2, 2)}, P/E {pe2}, капитализация ${round(mc2 / 1e9, 2)} млрд"
        )
    except Exception as e:
        return f"Ошибка: {e}"


FUNCTIONS = {
    "get_stock_price": get_stock_price,
    "get_stock_info": get_stock_info,
    "compare_stocks": compare_stocks,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Возвращает текущую цену акции и изменение за день. Тикеры: AAPL, MSFT, TSLA и т.д.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Тикер акции (AAPL, TSLA, NVDA)"}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_info",
            "description": "Возвращает базовую информацию о компании: сектор, капитализация, P/E, дивиденды",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Тикер акции"}
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_stocks",
            "description": "Сравнивает две акции по цене, P/E и капитализации",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker1": {"type": "string", "description": "Первый тикер"},
                    "ticker2": {"type": "string", "description": "Второй тикер"}
                },
                "required": ["ticker1", "ticker2"]
            }
        }
    }
]
