# tools/crypto_chart.py — данные графиков с Bybit (публичный API, без ключей)
import requests
from datetime import datetime


INTERVALS = {
    "1м": "1", "5м": "5", "15м": "15", "30м": "30",
    "1ч": "60", "4ч": "240", "1д": "D", "1н": "W"
}


def get_candles(symbol: str, interval: str = "60", limit: int = 20) -> str:
    """Последние свечи по паре. symbol: BTCUSDT. interval: 1, 5, 15, 60, 240, D."""
    try:
        s = symbol.upper().replace("/", "")
        url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={s}&interval={interval}&limit={limit}"
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return f"Bybit вернул код {r.status_code}"
        data = r.json()
        if data.get("retCode") != 0:
            return f"Ошибка Bybit: {data.get('retMsg', 'неизвестная')}"
        candles = data["result"]["list"]
        if not candles:
            return f"Нет данных по паре {s}"
        candles = list(reversed(candles))
        lines = [f"📊 {s}, таймфрейм {interval}, последние {len(candles)} свечей:"]
        for c in candles[-5:]:
            ts = int(c[0]) // 1000
            dt = datetime.fromtimestamp(ts).strftime("%d.%m %H:%M")
            o, h, l, cl = c[1], c[2], c[3], c[4]
            lines.append(f"{dt}: O={o} H={h} L={l} C={cl}")
        last = candles[-1]
        first = candles[0]
        change = (float(last[4]) - float(first[1])) / float(first[1]) * 100
        sign = "+" if change >= 0 else ""
        lines.append(f"\nИзменение за период: {sign}{round(change, 2)}%")
        lines.append(f"Текущая цена: {last[4]}")
        return "\n".join(lines)
    except Exception as e:
        return f"Ошибка получения свечей: {e}"


def get_price(symbol: str) -> str:
    """Текущая цена пары на Bybit."""
    try:
        s = symbol.upper().replace("/", "")
        url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={s}"
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return f"Bybit вернул код {r.status_code}"
        data = r.json()
        if data.get("retCode") != 0:
            return f"Ошибка: {data.get('retMsg', 'неизвестная')}"
        tickers = data["result"]["list"]
        if not tickers:
            return f"Пара {s} не найдена"
        t = tickers[0]
        price = t.get("lastPrice", "?")
        change = t.get("price24hPcnt", "0")
        try:
            change_pct = round(float(change) * 100, 2)
        except Exception:
            change_pct = "?"
        sign = "+" if str(change_pct).startswith("-") is False else ""
        return f"💰 {s}: {price} USDT, за 24ч: {sign}{change_pct}%"
    except Exception as e:
        return f"Ошибка: {e}"


FUNCTIONS = {
    "get_candles": get_candles,
    "get_price": get_price,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_candles",
            "description": "Возвращает последние свечи (OHLC) для криптопары с Bybit. Например, BTCUSDT на часовом таймфрейме",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Пара, например BTCUSDT или ETHUSDT"},
                    "interval": {"type": "string", "description": "Таймфрейм: 1, 5, 15, 30, 60, 240, D, W"},
                    "limit": {"type": "integer", "description": "Сколько свечей вернуть (по умолчанию 20)"}
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_price",
            "description": "Возвращает текущую цену криптопары на Bybit и изменение за 24 часа",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Пара, например BTCUSDT"}
                },
                "required": ["symbol"]
            }
        }
    }
]
