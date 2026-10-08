# tools/compare.py — сравнение активов (волатильность, корреляция)
import requests
from datetime import datetime, timedelta


def _get_crypto_history(symbol: str, days: int = 30):
    """История цен крипты через CoinGecko."""
    ids = {
        "btc": "bitcoin", "eth": "ethereum", "sol": "solana",
        "bnb": "binancecoin", "xrp": "ripple", "ton": "the-open-network",
        "ada": "cardano", "doge": "dogecoin", "avax": "avalanche-2"
    }
    cid = ids.get(symbol.lower(), symbol.lower())
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{cid}/market_chart?vs_currency=usd&days={days}"
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            return None
        data = r.json()
        return [p[1] for p in data.get("prices", [])]
    except Exception:
        return None


def _get_stock_history(ticker: str, days: int = 30):
    """История цен акции через yfinance."""
    try:
        import yfinance as yf
        t = yf.Ticker(ticker.upper())
        period = f"{days}d"
        hist = t.history(period=period)
        if hist.empty:
            return None
        return hist["Close"].tolist()
    except Exception:
        return None


def _get_history(symbol: str, days: int = 30):
    prices = _get_stock_history(symbol, days)
    if prices:
        return prices
    return _get_crypto_history(symbol, days)


def _volatility(prices):
    if not prices or len(prices) < 2:
        return None
    returns = []
    for i in range(1, len(prices)):
        if prices[i - 1] > 0:
            returns.append((prices[i] - prices[i - 1]) / prices[i - 1])
    if not returns:
        return None
    mean = sum(returns) / len(returns)
    var = sum((r - mean) ** 2 for r in returns) / len(returns)
    return (var ** 0.5) * 100


def _correlation(a, b):
    if not a or not b:
        return None
    n = min(len(a), len(b))
    a = a[-n:]
    b = b[-n:]
    ra = [(a[i] - a[i - 1]) / a[i - 1] for i in range(1, n) if a[i - 1] > 0]
    rb = [(b[i] - b[i - 1]) / b[i - 1] for i in range(1, n) if b[i - 1] > 0]
    m = min(len(ra), len(rb))
    ra = ra[-m:]
    rb = rb[-m:]
    if m < 2:
        return None
    ma = sum(ra) / m
    mb = sum(rb) / m
    cov = sum((ra[i] - ma) * (rb[i] - mb) for i in range(m)) / m
    sa = (sum((x - ma) ** 2 for x in ra) / m) ** 0.5
    sb = (sum((x - mb) ** 2 for x in rb) / m) ** 0.5
    if sa == 0 or sb == 0:
        return None
    return cov / (sa * sb)


def get_volatility(symbol: str, days: int = 30) -> str:
    """Волатильность актива за N дней (в %)."""
    prices = _get_history(symbol, days)
    if not prices:
        return f"Не удалось получить данные по {symbol}"
    vol = _volatility(prices)
    if vol is None:
        return f"Недостаточно данных по {symbol}"
    if vol < 2:
        level = "низкая"
    elif vol < 5:
        level = "средняя"
    else:
        level = "высокая"
    return f"📊 {symbol.upper()}: волатильность за {days} дней — {round(vol, 2)}% ({level})"


def compare_assets(symbol1: str, symbol2: str, days: int = 30) -> str:
    """Сравнивает два актива: волатильность и корреляция."""
    p1 = _get_history(symbol1, days)
    p2 = _get_history(symbol2, days)
    if not p1:
        return f"Не удалось получить данные по {symbol1}"
    if not p2:
        return f"Не удалось получить данные по {symbol2}"
    v1 = _volatility(p1)
    v2 = _volatility(p2)
    corr = _correlation(p1, p2)
    lines = [f"🔍 Сравнение {symbol1.upper()} и {symbol2.upper()} за {days} дней:"]
    if v1 is not None:
        lines.append(f"• Волатильность {symbol1.upper()}: {round(v1, 2)}%")
    if v2 is not None:
        lines.append(f"• Волатильность {symbol2.upper()}: {round(v2, 2)}%")
    if corr is not None:
        if corr > 0.7:
            desc = "сильная прямая"
        elif corr > 0.3:
            desc = "умеренная прямая"
        elif corr > -0.3:
            desc = "слабая / отсутствует"
        elif corr > -0.7:
            desc = "умеренная обратная"
        else:
            desc = "сильная обратная"
        lines.append(f"• Корреляция: {round(corr, 3)} ({desc})")
    return "\n".join(lines)


FUNCTIONS = {
    "get_volatility": get_volatility,
    "compare_assets": compare_assets,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_volatility",
            "description": "Считает волатильность актива (акции или крипты) за N дней",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Тикер (AAPL, BTC, ETH)"},
                    "days": {"type": "integer", "description": "За сколько дней (по умолчанию 30)"}
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_assets",
            "description": "Сравнивает два актива: волатильность и корреляцию",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol1": {"type": "string", "description": "Первый актив"},
                    "symbol2": {"type": "string", "description": "Второй актив"},
                    "days": {"type": "integer", "description": "За сколько дней (по умолчанию 30)"}
                },
                "required": ["symbol1", "symbol2"]
            }
        }
    }
]
