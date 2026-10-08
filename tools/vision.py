# tools/vision.py — анализ изображений через мультимодальную модель
import os
import base64
import requests


VISION_MODEL = "google/gemini-2.0-flash-exp:free"
FALLBACK_MODEL = "qwen/qwen-2-vl-7b-instruct:free"


def _encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _mime_type(path: str) -> str:
    p = path.lower()
    if p.endswith(".png"):
        return "image/png"
    if p.endswith(".jpg") or p.endswith(".jpeg"):
        return "image/jpeg"
    if p.endswith(".webp"):
        return "image/webp"
    if p.endswith(".gif"):
        return "image/gif"
    return "image/png"


def _call_vision(image_b64: str, mime: str, question: str, model: str) -> dict:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return {"error": "Не задан OPENROUTER_API_KEY в .env"}
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{image_b64}"}
                    }
                ]
            }
        ]
    }
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers, json=payload, timeout=90
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def analyze_image(file_path: str, question: str = "Опиши это изображение подробно") -> str:
    """Анализирует изображение: описывает содержимое, читает текст, отвечает на вопрос."""
    if not os.path.exists(file_path):
        return f"Файл не найден: {file_path}"
    try:
        b64 = _encode_image(file_path)
        mime = _mime_type(file_path)
    except Exception as e:
        return f"Ошибка чтения файла: {e}"

    for model in [VISION_MODEL, FALLBACK_MODEL]:
        result = _call_vision(b64, mime, question, model)
        if "error" in result and isinstance(result["error"], str):
            continue
        if "error" in result:
            err_msg = result["error"].get("message", str(result["error"]))
            continue
        choices = result.get("choices", [])
        if not choices:
            continue
        content = choices[0].get("message", {}).get("content", "")
        if content:
            return f"🖼 Анализ изображения:\n\n{content}"

    return (
        "Не удалось проанализировать изображение. "
        "Возможно, бесплатная vision-модель недоступна. "
        "Попробуй позже или используй другую модель."
    )


def read_text_from_image(file_path: str) -> str:
    """Распознаёт текст на картинке (OCR)."""
    return analyze_image(file_path, "Прочитай весь текст на этом изображении. Выведи только текст, без комментариев.")


FUNCTIONS = {
    "analyze_image": analyze_image,
    "read_text_from_image": read_text_from_image,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_image",
            "description": "Анализирует изображение по указанному пути: описывает содержимое, отвечает на вопросы о нём",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Путь к файлу изображения"},
                    "question": {"type": "string", "description": "Вопрос или задача по изображению"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_text_from_image",
            "description": "Распознаёт текст с картинки (OCR)",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Путь к файлу изображения"}
                },
                "required": ["file_path"]
            }
        }
    }
]
