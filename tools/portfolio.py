# tools/portfolio.py — аналитика портфеля
try:
    import yfinance as yf
    _YF_OK = True
except Exception:
    _YF_OK = False


def _get_stock_price(ticker: str):
    if not _YF_OK:
        return None
    try:
        t = yf.Ticker(ticker.upper())
        info = t.info
        price = info.get("regularMarketPrice") or info.get("currentPrice")
        return price
    except Exception:
        return None


def _get_crypto_price(symbol: str):
    import requests
    ids = {
        "btc": "bitcoin", "eth": "ethereum", "sol": "solana",
        "bnb": "binancecoin", "xrp": "ripple", "ton": "the-open-network",
        "ada": "cardano", "doge": "dogecoin", "avax": "avalanche-2"
    }
    cid = ids.get(symbol.lower())
    if not cid:
        return None
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cid}&vs_currencies=usd"
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return None
        data = r.json()
        return data.get(cid, {}).get("usd")
    except Exception:
        return None


def analyze_portfolio(items: str) -> str:
    """Анализ портфеля. items — строка вида: 'AAPL:10:150, BTC:0.5:40000, TSLA:5:200'.
    Формат: ТИКЕР:КОЛИЧЕСТВО:ЦЕНА_ПОКУПКИ (цена покупки опциональна)."""
    if not items:
        return "Пустой портфель. Пример: AAPL:10:150, BTC:0.5:40000"

    total_value = 0
    total_cost = 0
    lines = ["💼 Анализ портфеля:"]

    for entry in items.split(","):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split(":")
        if len(parts) < 2:
            lines.append(f"⚠ Пропущено: {entry} (нужен формат ТИКЕР:КОЛИЧЕСТВО)")
            continue
        ticker = parts[0].strip().upper()
        try:
            qty = float(parts[1])
        except Exception:
            lines.append(f"⚠ Неверное количество: {entry}")
            continue
        buy_price = None
        if len(parts) >= 3:
            try:
                buy_price = float(parts[2])
            except Exception:
                buy_price = None

        price = _get_stock_price(ticker)
        if price is None:
            price = _get_crypto_price(ticker)
        if price is None:
            lines.append(f"❓ {ticker}: цена не найдена")
            continue

        value = price * qty
        total_value += value

        if buy_price is not None:
            cost = buy_price * qty
            total_cost += cost
            pl = value - cost
            pl_pct = (pl / cost * 100) if cost > 0 else 0
            sign = "+" if pl >= 0 else ""
            lines.append(
                f"• {ticker}: {qty} × ${round(price, 2)} = ${round(value, 2)} "
                f"| P/L: {sign}${round(pl, 2)} ({sign}{round(pl_pct, 2)}%)"
            )
        else:
            lines.append(f"• {ticker}: {qty} × ${round(price, 2)} = ${round(value, 2)}")

    lines.append(f"\n💰 Общая стоимость: ${round(total_value, 2)}")
    if total_cost > 0:
        total_pl = total_value - total_cost
        total_pl_pct = total_pl / total_cost * 100
        sign = "+" if total_pl >= 0 else ""
        lines.append(f"📊 Общий P/L: {sign}${round(total_pl, 2)} ({sign}{round(total_pl_pct, 2)}%)")
        lines.append(f"💵 Вложено: ${round(total_cost, 2)}")

    return "\n".join(lines)


FUNCTIONS = {
    "analyze_portfolio": analyze_portfolio,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_portfolio",
            "description": "Анализирует портфель: считает стоимость, прибыль/убыток. Формат: ТИКЕР:КОЛИЧЕСТВО:ЦЕНА_ПОКУПКИ через запятую",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "string",
                        "description": "Портфель: 'AAPL:10:150, BTC:0.5:40000'. Цена покупки опциональна"
                    }
                },
                "required": ["items"]
            }
        }
    }
]
