# tools/music.py — генерация музыки (Pollinations.AI) + поиск легальных источников
import os
import hashlib
import requests


SAVE_DIR = "generated"
os.makedirs(SAVE_DIR, exist_ok=True)


def generate_music(prompt: str) -> str:
    """Генерирует музыку по описанию через Pollinations.AI."""
    try:
        encoded = requests.utils.quote(prompt)
        url = f"https://audio.pollinations.ai/prompt/{encoded}"
        r = requests.get(url, timeout=120)
        if r.status_code != 200:
            return f"Не удалось сгенерировать музыку (код {r.status_code})"
        if len(r.content) < 1000:
            return "Сервис вернул пустой файл. Попробуй другой промпт."
        h = hashlib.md5(prompt.encode("utf-8")).hexdigest()[:8]
        filename = f"{SAVE_DIR}/music_{h}.mp3"
        with open(filename, "wb") as f:
            f.write(r.content)
        abs_path = os.path.abspath(filename)
        return f"🎵 Музыка готова: {filename}\nПолный путь: {abs_path}\nРазмер: {round(len(r.content)/1024, 1)} КБ"
    except Exception as e:
        return f"Ошибка генерации музыки: {e}"


def find_free_music_sources(query: str) -> str:
    """Ищет легальные бесплатные источники музыки по запросу."""
    sources = [
        ("Free Music Archive", "https://freemusicarchive.org/", "Тысячи треков под открытыми лицензиями"),
        ("Jamendo", "https://www.jamendo.com/", "Бесплатная музыка от независимых артистов"),
        ("YouTube Audio Library", "https://studio.youtube.com/", "Бесплатные треки для видео"),
        ("Pixabay Music", "https://pixabay.com/music/", "Бесплатно, без указания автора"),
        ("ccMixter", "https://ccmixter.org/", "Ремиксы под Creative Commons"),
        ("Incompetech", "https://incompetech.com/music/", "Музыка Kevin MacLeod"),
    ]
    lines = [f"🎼 Легальные источники музыки по запросу «{query}»:"]
    for name, url, desc in sources:
        lines.append(f"• {name} — {desc}\n  {url}")
    lines.append("\n⚠ Все источники бесплатные и легальные. Проверяй лицензию каждого трека.")
    return "\n".join(lines)


FUNCTIONS = {
    "generate_music": generate_music,
    "find_free_music_sources": find_free_music_sources,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "generate_music",
            "description": "Генерирует музыку по текстовому описанию (жанр, настроение, инструменты). Сохраняет MP3-файл",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Описание музыки: 'lo-fi трек для учёбы, спокойный, дождь'"}
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_free_music_sources",
            "description": "Возвращает список легальных бесплатных сайтов с музыкой по теме",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Что ищем: жанр, настроение, тема"}
                },
                "required": ["query"]
            }
        }
    }
]
