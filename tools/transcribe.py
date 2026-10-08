# tools/transcribe.py — транскрипция аудио (OpenAI Whisper)
import os
import requests


def transcribe_audio(file_path: str) -> str:
    """Распознаёт текст из аудио-файла через OpenAI Whisper."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return "Транскрипция недоступна: не задан ключ OPENAI_API_KEY в файле .env"
    if not os.path.exists(file_path):
        return f"Файл не найден: {file_path}"
    try:
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {api_key}"}
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"model": "whisper-1", "language": "ru"}
            r = requests.post(url, headers=headers, files=files, data=data, timeout=120)
        if r.status_code != 200:
            return f"Ошибка Whisper: {r.status_code} — {r.text[:200]}"
        result = r.json()
        text = result.get("text", "")
        if not text:
            return "Whisper вернул пустой результат"
        return f"📝 Распознанный текст:\n\n{text}"
    except Exception as e:
        return f"Ошибка транскрипции: {e}"


FUNCTIONS = {
    "transcribe_audio": transcribe_audio,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "transcribe_audio",
            "description": "Распознаёт текст из аудио-файла (MP3, WAV, M4A). Требует ключ OpenAI",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Путь к аудио-файлу"}
                },
                "required": ["file_path"]
            }
        }
    }
]
