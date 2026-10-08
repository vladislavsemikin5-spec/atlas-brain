# Atlas Brain v0.6 — чат с логотипом и индикатором
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
    return {"status": "ok", "version": "0.6", "tools_loaded": len(TOOLS)}

@app.get("/health")
def health():
    return {"status": "healthy"}

CHAT_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Atlas Chat</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 720px; margin: 30px auto; padding: 20px; background: #f5f7fb; }
.header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.logo { width: 44px; height: 44px; border-radius: 10px; background: #131722; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.logo svg { width: 26px; height: 26px; }
h1 { margin: 0; color: #2962ff; font-size: 22px; }
#log { background: #fff; padding: 18px; border-radius: 10px; min-height: 240px; margin-bottom: 14px; white-space: pre-wrap; border: 1px solid #e3e6ec; line-height: 1.6; }
#msg { width: 100%; padding: 12px 14px; font-size: 16px; border-radius: 8px; border: 1px solid #ccc; box-sizing: border-box; }
#btn { padding: 12px 24px; margin-top: 10px; background: #2962ff; color: #fff; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
#btn:disabled { background: #a5b8e8; cursor: not-allowed; }
.loading { display: inline-block; margin-left: 8px; }
.loading span { display: inline-block; width: 8px; height: 8px; margin: 0 2px; background: #2962ff; border-radius: 50%; animation: blink 1.4s infinite both; }
.loading span:nth-child(2) { animation-delay: .2s; }
.loading span:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 0%,80%,100% { opacity: .3; } 40% { opacity: 1; } }
</style>
</head>
<body>
<div class="header">
<div class="logo"><svg viewBox="0 0 64 64"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#667eea"/><stop offset="100%" stop-color="#764ba2"/></linearGradient></defs><path d="M16 50 L32 16 L48 50" stroke="url(#g)" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M23 38 L41 38" stroke="url(#g)" stroke-width="7" stroke-linecap="round"/></svg></div>
<h1>Atlas Chat</h1>
</div>
<div id="log">Привет! Задай вопрос Атласу.</div>
<input id="msg" placeholder="Введи сообщение..." autofocus>
<button id="btn" onclick="send()">Отправить</button>
<script>
async function send(){
  var btn=document.getElementById('btn');
  var m=document.getElementById('msg').value.trim();
  if(!m){alert('Введи сообщение');return;}
  var l=document.getElementById('log');
  l.textContent+='\\n\\nТы: '+m;
  document.getElementById('msg').value='';
  btn.disabled=true;
  l.textContent+='\\n\\nАтлас: ';
  var loading=document.createElement('span');
  loading.className='loading';
  loading.id='loadingIndicator';
  loading.innerHTML='<span></span><span></span><span></span>';
  l.appendChild(loading);
  l.scrollTop=l.scrollHeight;
  try{
    var r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
    var d=await r.json();
    var ind=document.getElementById('loadingIndicator');
    if(ind)ind.remove();
    l.textContent=l.textContent+(d.reply||d.error);
  }catch(e){
    var ind=document.getElementById('loadingIndicator');
    if(ind)ind.remove();
    l.textContent+='Ошибка: '+e.message;
  }
  btn.disabled=false;
  l.scrollTop=l.scrollHeight;
}
document.getElementById('msg').addEventListener('keydown',e=>{if(e.key==='Enter')send();});
</script>
</body>
</html>"""

ADMIN_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Atlas Admin</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 720px; margin: 30px auto; padding: 20px; background: #fff5f5; }
.header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.logo { width: 44px; height: 44px; border-radius: 10px; background: #b91c1c; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.logo svg { width: 26px; height: 26px; }
h1 { margin: 0; color: #b91c1c; font-size: 22px; }
#log { background: #fff; padding: 18px; border-radius: 10px; min-height: 240px; margin-bottom: 14px; white-space: pre-wrap; border: 1px solid #f3c8c8; line-height: 1.6; }
#pwd { width: 100%; padding: 10px 12px; font-size: 14px; border-radius: 8px; border: 1px solid #ccc; box-sizing: border-box; margin-bottom: 8px; }
#msg { width: 100%; padding: 12px 14px; font-size: 16px; border-radius: 8px; border: 1px solid #ccc; box-sizing: border-box; }
#btn { padding: 12px 24px; margin-top: 10px; background: #b91c1c; color: #fff; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
#btn:disabled { background: #e5a5a5; cursor: not-allowed; }
.loading { display: inline-block; margin-left: 8px; }
.loading span { display: inline-block; width: 8px; height: 8px; margin: 0 2px; background: #b91c1c; border-radius: 50%; animation: blink 1.4s infinite both; }
.loading span:nth-child(2) { animation-delay: .2s; }
.loading span:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 0%,80%,100% { opacity: .3; } 40% { opacity: 1; } }
</style>
</head>
<body>
<div class="header">
<div class="logo"><svg viewBox="0 0 64 64"><path d="M16 50 L32 16 L48 50" stroke="#fff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M23 38 L41 38" stroke="#fff" stroke-width="7" stroke-linecap="round"/></svg></div>
<h1>Atlas Admin</h1>
</div>
<div id="log">Режим создателя. Введи пароль и задай вопрос.</div>
<input id="pwd" type="password" placeholder="Пароль администратора">
<input id="msg" placeholder="Введи сообщение...">
<button id="btn" onclick="send()">Отправить</button>
<script>
async function send(){
  var btn=document.getElementById('btn');
  var m=document.getElementById('msg').value.trim();
  var p=document.getElementById('pwd').value;
  if(!m){alert('Введи сообщение');return;}
  if(!p){alert('Введи пароль');return;}
  var l=document.getElementById('log');
  l.textContent+='\\n\\n[Admin] '+m;
  document.getElementById('msg').value='';
  btn.disabled=true;
  l.textContent+='\\n\\nАтлас: ';
  var loading=document.createElement('span');
  loading.className='loading';
  loading.id='loadingIndicator';
  loading.innerHTML='<span></span><span></span><span></span>';
  l.appendChild(loading);
  l.scrollTop=l.scrollHeight;
  try{
    var r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m,password:p})});
    var d=await r.json();
    var ind=document.getElementById('loadingIndicator');
    if(ind)ind.remove();
    l.textContent=l.textContent+(d.reply||d.error);
  }catch(e){
    var ind=document.getElementById('loadingIndicator');
    if(ind)ind.remove();
    l.textContent+='Ошибка: '+e.message;
  }
  btn.disabled=false;
  l.scrollTop=l.scrollHeight;
}
document.getElementById('msg').addEventListener('keydown',e=>{if(e.key==='Enter')send();});
</script>
</body>
</html>"""

@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return CHAT_HTML

@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return ADMIN_HTML

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
