# tools/video.py — помощь в генерации видео
# Прямых бесплатных API без ключей нет, поэтому:
# - выдаём список сервисов
# - готовим промпт для генерации


def find_video_services(query: str = "") -> str:
    """Возвращает список сервисов генерации видео (бесплатные и с бесплатным лимитом)."""
    services = [
        ("Runway ML", "https://runwayml.com/", "Бесплатно 125 кредитов при регистрации"),
        ("Pika Labs", "https://pika.art/", "Бесплатный доступ через Discord"),
        ("Kling AI", "https://klingai.com/", "Бесплатные кредиты каждый день"),
        ("Luma Dream Machine", "https://lumalabs.ai/dream-machine", "Бесплатные генерации при регистрации"),
        ("Hailuo AI (MiniMax)", "https://hailuoai.video/", "Бесплатный лимит в день"),
        ("PixVerse", "https://pixverse.ai/", "Бесплатные кредиты при регистрации"),
        ("Stable Video Diffusion", "https://replicate.com/stability-ai/stable-video-diffusion", "Через Replicate, оплата по факту"),
    ]
    lines = [f"🎬 Сервисы генерации видео" + (f" по запросу «{query}»" if query else "") + ":"]
    for name, url, desc in services:
        lines.append(f"• {name} — {desc}\n  {url}")
    lines.append("\n⚠ Все требуют регистрации. Полностью бесплатных API для видео пока нет.")
    lines.append("💡 Готовый промпт для видео можно составить — просто опиши идею.")
    return "\n".join(lines)


def make_video_prompt(idea: str, style: str = "realistic", duration: int = 5) -> str:
    """Помогает составить промпт для генерации видео.
    idea — идея видео, style — стиль (realistic, anime, cinematic, cyberpunk),
    duration — длительность в секундах."""
    style_map = {
        "realistic": "realistic, 4k, high detail, natural lighting",
        "anime": "anime style, studio ghibli, vibrant colors, hand drawn",
        "cinematic": "cinematic, dramatic lighting, film grain, widescreen",
        "cyberpunk": "cyberpunk, neon lights, rainy city, blade runner style",
        "fantasy": "fantasy, epic, magical, ethereal, dreamlike",
        "minimal": "minimalist, clean, flat design, pastel colors",
    }
    style_desc = style_map.get(style.lower(), style)
    prompt_en = f"{idea}, {style_desc}, smooth motion, {duration} seconds"
    return (
        f"📝 Промпт для видео:\n\n"
        f"Русский: {idea}. Стиль: {style}. Длительность: {duration} сек.\n\n"
        f"English (для зарубежных сервисов):\n{prompt_en}\n\n"
        f"💡 Вставь English-версию в Runway, Pika или Kling."
    )


def video_tips() -> str:
    """Советы по генерации видео."""
    return (
        "🎥 Советы для хорошего видео:\n\n"
        "1. Короткие промпты работают лучше (5–15 слов)\n"
        "2. Указывай движение: 'камера пролетает', 'волны набегают', 'человек идёт'\n"
        "3. Описывай освещение: 'закат', 'неон', 'туман', 'солнечный свет'\n"
        "4. Не проси больше 5–10 секунд — бесплатные сервисы режут длину\n"
        "5. Генерируй несколько вариантов и выбирай лучший\n"
        "6. Избегай текста в видео — он плохо получается\n"
        "7. Для реализма добавляй '4k, cinematic, realistic'\n"
    )


FUNCTIONS = {
    "find_video_services": find_video_services,
    "make_video_prompt": make_video_prompt,
    "video_tips": video_tips,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "find_video_services",
            "description": "Возвращает список бесплатных сервисов генерации видео (Runway, Pika, Kling и др.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Что ищем (необязательно)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "make_video_prompt",
            "description": "Составляет готовый промпт для генерации видео. Пользователь описывает идею, инструмент делает правильный промпт для Runway/Pika/Kling",
            "parameters": {
                "type": "object",
                "properties": {
                    "idea": {"type": "string", "description": "Идея видео на русском"},
                    "style": {"type": "string", "description": "Стиль: realistic, anime, cinematic, cyberpunk, fantasy, minimal"},
                    "duration": {"type": "integer", "description": "Длительность в секундах (3–10)"}
                },
                "required": ["idea"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "video_tips",
            "description": "Советы по генерации видео для новичков",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]
