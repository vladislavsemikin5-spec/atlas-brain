# Atlas Brain v0.5 — автообнаружение инструментов
import os
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from tools import TOOLS, FUNCTIONS

load_dotenv()
app = FastAPI()
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ.get("OPENROUTER_API_KEY"))
MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
SYS_USER = "Ты Atlas AI - ассистент. Отвечай кратко на русском. Если нужен точный расчёт или данные - используй инструменты."
SYS_ADMIN = "Ты Atlas AI, общаешься с создателем проекта. Помогай с кодом и развитием. Используй инструменты когда нужно."

class ChatRequest(BaseModel):
    message: str
    password: str = ""

@app.get("/")
def root():
    return {"status": "ok", "version": "0.5", "tools_loaded": len(TOOLS)}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return "<html><head><meta charset='utf-8'><title>Atlas Chat</title></head><body><h1>Atlas Chat</h1><div id='log'>Привет! Задай вопрос.</div><input id='msg' placeholder='Сообщение'><button onclick='send()'>Отправить</button><script>async function send(){var m=document.getElementById('msg').value.trim();if(!m){alert('Введи сообщение');return;}var l=document.getElementById('log');l.textContent+='\\n\\nТы: '+m;document.getElementById('msg').value='';try{var r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});var d=await r.json();l.textContent+='\\n\\nАтлас: '+(d.reply||d.error);}catch(e){l.textContent+='\\n\\nОшибка: '+e.message;}}</script></body></html>"

@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return "<html><head><meta charset='utf-8'><title>Atlas Admin</title></head><body><h1>Atlas Admin</h1><div id='log'>Режим создателя.</div><input id='pwd' type='password' placeholder='Пароль'><input id='msg' placeholder='Сообщение'><button onclick='send()'>Отправить</button><script>async function send(){var m=document.getElementById('msg').value.trim();var p=document.getElementById('pwd').value;if(!m){alert('Введи сообщение');return;}if(!p){alert('Введи пароль');return;}var l=document.getElementById('log');l.textContent+='\\n\\n[Admin] '+m;document.getElementById('msg').value='';try{var r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m,password:p})});var d=await r.json();l.textContent+='\\n\\nАтлас: '+(d.reply||d.error);}catch(e){l.textContent+='\\n\\nОшибка: '+e.message;}}</script></body></html>"

def run_tool(name, args):
    func = FUNCTIONS.get(name)
    if not func:
        return "Инструмент не найден"
    try:
        return str(func(**args))
    except Exception as e:
        return f"Ошибка инструмента: {e}"

@app.post("/api/chat")
def chat(req: ChatRequest):
    try:
        if req.password and req.password == ADMIN_PASSWORD:
            sp = SYS_ADMIN
        elif req.password:
            return {"error": "Неверный пароль"}
        else:
            sp = SYS_USER

        messages = [
            {"role": "system", "content": sp},
            {"role": "user", "content": req.message}
        ]

        for _ in range(5):
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS if TOOLS else None,
                temperature=0.7
            )
            if not response or not response.choices:
                return {"reply": "Модель не ответила. Попробуй ещё раз."}

            msg = response.choices[0].message

            if not msg.tool_calls:
                content = msg.content or "Пустой ответ"
                return {"reply": content}

            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in msg.tool_calls
                ]
            })

            for tc in msg.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                except Exception:
                    args = {}
                result = run_tool(name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })

        return {"reply": "Слишком много шагов. Попробуй переформулировать."}

    except Exception as e:
        print("ОШИБКА:", repr(e))
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
