 </body>
    </html>
    """


@app.post("/api/chat")
def chat(req: ChatRequest):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Ты Atlas AI — умный ассистент. Отвечай кратко и по делу на русском."},
                {"role": "user", "content": req.message}
            ],
            temperature=0.7
        )
        return {"reply": response.choices[0].message.content}
        except Exception as e:
        print("=" * 40)
        print("ОШИБКА OpenRouter:", repr(e))
        print("=" * 40)
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
