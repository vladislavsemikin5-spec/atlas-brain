# Atlas Brain v0.8 — KodikRouter + Gemini 2.5 Flash Lite
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

client = OpenAI(
    base_url="https://api.kodikrouter.ru/v1",
    api_key=os.environ.get("KODIK_API_KEY")
)

MODEL = "google/gemini-2.5-flash-lite"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

SYS_USER = "Ты Atlas AI - ассистент. Отвечай кратко на русском. Если нужен точный расчёт или данные - используй инструменты."
SYS_ADMIN = "Ты Atlas AI, общаешься с создателем проекта. Помогай с кодом и развитием. Используй инструменты когда нужно."


class ChatRequest(BaseModel):
    message: str
    password: str = ""


@app.get("/")
def root():
    return {"status": "ok", "version": "0.8", "tools_loaded": len(TOOLS)}


@app.get("/health")
def health():
    return {"status": "healthy"}


CHAT_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Atlas Chat</title>
<style>
body { font-family: -apple-system, sans-serif; max-width: 720px; margin: 30px auto; padding: 20px; background: #f5f7fb; }
.header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.logo { width: 44px; height: 44px; border-radius: 10px; background: #131722; display: flex; align-items: center; justify-content: center; }
.logo svg { width: 26px; height: 26px; }
h1 { margin: 0; color: #2962ff; font-size: 22px; }
#log { background: #fff; padding: 18px; border-radius: 10px; min-height: 240px; margin-bottom: 14px; white-space: pre-wrap; border: 1px solid #e3e6ec; line-height: 1.6; font-size: 14px; }
#msg { width: 100%; padding: 12px 14px; font-size: 16px; border-radius: 8px; border: 1px solid #ccc; box-sizing: border-box; }
#btn { padding: 12px 24px; margin-top: 10px; background: #2962ff; color: #fff; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
#btn:disabled { background: #a5b8e8; cursor: not-allowed; }
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
  l.textContent+='\\n\\nАтлас: ...';
  l.scrollTop=l.scrollHeight;
  try{
    var r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
    var d=await r.json();
    l.textContent=l.textContent.replace('Атлас: ...','Атлас: '+(d.reply||d.error));
  }catch(e){
    l.textContent+='Ошибка: '+e.message;
  }
  btn.disabled=false;
  l.scrollTop=l.scrollHeight;
}
document.getElementById('msg').addEventListener('keydown',e=>{if(e.key==='Enter')send();});
</script>
</body>
</html>"""
ADMIN_HTML = CHAT_HTML.replace('Atlas Chat', 'Atlas Admin').replace('#2962ff', '#b91c1c')


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


@app.post("/api/chat_stream")
async def chat_stream(req: ChatRequest):
    from sse_starlette.sse import EventSourceResponse

    async def event_generator():
        try:
            if req.password and req.password == ADMIN_PASSWORD:
                sp = SYS_ADMIN
            elif req.password:
                yield f'data: {json.dumps({"type": "answer", "text": "Неверный пароль"})}\n\n'
                yield 'data: [DONE]\n\n'
                return
            else:
                sp = SYS_USER

            messages = [
                {"role": "system", "content": sp},
                {"role": "user", "content": req.message}
            ]

            for _ in range(5):
                stream = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=TOOLS if TOOLS else None,
                    stream=True
                )

                collected_content = ""
                tool_calls = []

                for chunk in stream:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if not delta:
                        continue

                    if delta.content:
                        collected_content += delta.content
                        yield f'data: {json.dumps({"type": "answer", "text": delta.content})}\n\n'

                    if delta.tool_calls:
                        for tc in delta.tool_calls:
                            if tc.index is not None:
                                while len(tool_calls) <= tc.index:
                                    tool_calls.append({"id": "", "name": "", "arguments": ""})
                                if tc.id:
                                    tool_calls[tc.index]["id"] = tc.id
                                if tc.function:
                                    if tc.function.name:
                                        tool_calls[tc.index]["name"] += tc.function.name
                                    if tc.function.arguments:
                                        tool_calls[tc.index]["arguments"] += tc.function.arguments

                if not tool_calls:
                    yield 'data: [DONE]\n\n'
                    return

                messages.append({
                    "role": "assistant",
                    "content": collected_content,
                    "tool_calls": [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {"name": tc["name"], "arguments": tc["arguments"]}
                        } for tc in tool_calls
                    ]
                })

                for tc in tool_calls:
                    name = tc["name"]
                    try:
                        args = json.loads(tc["arguments"])
                    except Exception:
                        args = {}
                    yield f'data: {json.dumps({"type": "tool", "text": "Вызываю: " + name})}\n\n'
                    result = run_tool(name, args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result
                    })

            yield f'data: {json.dumps({"type": "answer", "text": "Слишком много шагов."})}\n\n'
            yield 'data: [DONE]\n\n'

        except Exception as e:
            yield f'data: {json.dumps({"type": "answer", "text": f"Ошибка: {e}"})}\n\n'
            yield 'data: [DONE]\n\n'

    return EventSourceResponse(event_generator())


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
                return {"reply": "Модель не ответила."}

            msg = response.choices[0].message

            if not msg.tool_calls:
                return {"reply": msg.content or "Пустой ответ"}

            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments}
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

        return {"reply": "Слишком много шагов."}

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
