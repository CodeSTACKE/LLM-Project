from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import FileResponse, StreamingResponse
import ollama
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()
API_KEY = os.getenv("API_KEY")
DEV_MODE = os.getenv("DEV_MODE", "false").lower() in ("1", "true", "yes")
API_KEY_CREDITS = {API_KEY: 10} if API_KEY else {}

app = FastAPI()


def verify_api_key(x_api_key: str = Header(None)):
    # If dev mode is enabled, bypass API key requirement
    if DEV_MODE:
        return x_api_key or "dev"

    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing x-api-key header")

    credits = API_KEY_CREDITS.get(x_api_key, 0)
    if credits <= 0:
        raise HTTPException(status_code=401, detail="Invalid API Key or no credits left")
    return x_api_key


@app.get("/", response_class=FileResponse)
def read_index():
    return FileResponse("templates/index.html")


@app.get("/health")
def health():
    try:
        # Test if Ollama is reachable by trying a quick chat
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": "hi"}])
        return {"ok": True, "ollama": True, "mistral_available": True}
    except Exception as e:
        return {"ok": False, "ollama": False, "error": f"Ollama unavailable: {str(e)[:50]}"}


def _decrement_credit(x_api_key: str):
    if DEV_MODE:
        return
    if x_api_key in API_KEY_CREDITS:
        API_KEY_CREDITS[x_api_key] -= 1


@app.post("/generate")
def generate(prompt: str, x_api_key: str = Depends(verify_api_key)):
    _decrement_credit(x_api_key)
    try:
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        return {"response": response["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama error: {e}")


@app.post("/ask")
def ask(payload: dict, x_api_key: str = Depends(verify_api_key)):
    prompt = payload.get("prompt", "")
    _decrement_credit(x_api_key)
    try:
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        return {"answer": response["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama error: {e}")


@app.post("/stream")
async def stream(payload: dict, x_api_key: str = Depends(verify_api_key)):
    prompt = payload.get("prompt", "")
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing prompt")

    _decrement_credit(x_api_key)

    try:
        # Request full response from Ollama, then stream it back to client in small chunks.
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        text = response["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama error: {e}")

    async def generator():
        chunk_size = 40
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size]
            yield chunk
            await asyncio.sleep(0.03)

    return StreamingResponse(generator(), media_type="text/plain")