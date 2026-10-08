# tools/image.py — генерация картинок (Pollinations.ai, без ключей)
import requests
import os
import hashlib


SAVE_DIR = "generated"
os.makedirs(SAVE_DIR, exist_ok=True)


def generate_image(prompt: str) -> str:
    """Генерирует картинку по описанию. Возвращает имя файла и ссылку."""
    try:
        encoded = requests.utils.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&model=flux"
        r = requests.get(url, timeout=90)
        if r.status_code != 200:
            return f"Не удалось сгенерировать картинку (код {r.status_code})"
        h = hashlib.md5(prompt.encode("utf-8")).hexdigest()[:8]
        filename = f"{SAVE_DIR}/img_{h}.png"
        with open(filename, "wb") as f:
            f.write(r.content)
        abs_path = os.path.abspath(filename)
        return f"Картинка готова: {filename}\nПрямая ссылка: {url}\nФайл: {abs_path}"
    except Exception as e:
        return f"Ошибка генерации: {e}"


def generate_image_url(prompt: str) -> str:
    """Возвращает только ссылку на сгенерированную картинку (без сохранения)."""
    try:
        encoded = requests.utils.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&model=flux"
        return f"Ссылка на картинку по запросу '{prompt}':\n{url}"
    except Exception as e:
        return f"Ошибка: {e}"


FUNCTIONS = {
    "generate_image": generate_image,
    "generate_image_url": generate_image_url,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "generate_image",
            "description": "Генерирует картинку по текстовому описанию и сохраняет её. Используй когда пользователь просит нарисовать, создать изображение или картинку",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Описание картинки на русском или английском языке"}
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_image_url",
            "description": "Возвращает ссылку на сгенерированную картинку без сохранения на диск. Быстрее чем generate_image",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Описание картинки"}
                },
                "required": ["prompt"]
            }
        }
    }
]
