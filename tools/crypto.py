# tools/crypto.py — курсы криптовалют (CoinGecko, без ключей)
import requests

_CACHE = {"data": None, "time": 0}
_CACHE_TTL = 120

COINS = {
    "btc": "bitcoin",
    "bitcoin": "bitcoin",
    "биткоин": "bitcoin",
    "eth": "ethereum",
    "ethereum": "ethereum",
    "эфир": "ethereum",
    "usdt": "tether",
    "tether": "tether",
    "bnb": "binancecoin",
    "sol": "solana",
    "solana": "solana",
    "xrp": "ripple",
    "ada": "cardano",
    "doge": "dogecoin",
    "dogecoin": "dogecoin",
    "ton": "the-open-network",
    "avax": "avalanche-2",
    "dot": "polkadot",
    "matic": "matic-network",
    "link": "chainlink",
    "ltc": "litecoin",
}


def _get_prices():
    import time
    now = time.time()
    if _CACHE["data"] and (now - _CACHE["time"]) < _CACHE_TTL:
        return _CACHE["data"]
    try:
        ids = ",".join(set(COINS.values()))
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd,rub&include_24hr_change=true"
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return None
        _CACHE["data"] = r.json()
        _CACHE["time"] = now
        return _CACHE["data"]
    except Exception:
        return None


def _resolve(name: str):
    key = name.lower().strip()
    return COINS.get(key)


def get_crypto_price(coin: str) -> str:
    """Курс одной монеты в USD и RUB + изменение за 24 часа."""
    cid = _resolve(coin)
    if not cid:
        return f"Монета '{coin}' не найдена. Попробуй BTC, ETH, SOL, TON."
    prices = _get_prices()
    if not prices or cid not in prices:
        return "Не удалось получить курс крипты"
    p = prices[cid]
    usd = p.get("usd", "?")
    rub = p.get("rub", "?")
    change = p.get("usd_24h_change", 0)
    sign = "+" if change >= 0 else ""
    return f"{coin.upper()}: ${usd} ({rub} ₽), за 24ч: {sign}{round(change, 2)}%"


def get_top_crypto() -> str:
    """Топ-5 криптовалют по капитализации."""
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=5&page=1"
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return "Не удалось получить топ крипты"
        data = r.json()
        lines = ["Топ-5 криптовалют:"]
        for i, coin in enumerate(data, 1):
            name = coin.get("name", "?")
            symbol = coin.get("symbol", "?").upper()
            price = coin.get("current_price", "?")
            change = coin.get("price_change_percentage_24h", 0) or 0
            sign = "+" if change >= 0 else ""
            lines.append(f"{i}. {name} ({symbol}): ${price} ({sign}{round(change, 2)}%)")
        return "\n".join(lines)
    except Exception as e:
        return f"Ошибка: {e}"


FUNCTIONS = {
    "get_crypto_price": get_crypto_price,
    "get_top_crypto": get_top_crypto,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_crypto_price",
            "description": "Возвращает курс криптовалюты в USD и RUB + изменение за 24 часа",
            "parameters": {
                "type": "object",
                "properties": {
                    "coin": {"type": "string", "description": "Название монеты: BTC, ETH, SOL, TON, DOGE и т.д."}
                },
                "required": ["coin"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_crypto",
            "description": "Возвращает топ-5 криптовалют по капитализации с ценами",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]
