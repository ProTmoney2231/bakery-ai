from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import os

# Load .env if present (local dev)
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    # On Render this must be set in Settings → Environment
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")

client = OpenAI(api_key=api_key)
app = FastAPI(title="Bakery AI")

# CORS (frontends can call us from any origin; tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

def chat_reply(user_text: str) -> str:
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a friendly bakery assistant. Be concise and helpful."},
                {"role": "user", "content": user_text},
            ],
            temperature=0.7,
        )
        return resp.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assistant")
def assistant(req: ChatRequest):
    return {"reply": chat_reply(req.message)}

# Alias so /chat works too
@app.post("/chat")
def chat(req: ChatRequest):
    return {"reply": chat_reply(req.message)}

# Simple health check
@app.get("/")
def root():
    return {"ok": True, "service": "bakery-ai"}

# --- Added homepage route ---
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Sweet Treats Bakery AI</title>
        </head>
        <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
            <h1>🥐 Welcome to Sweet Treats Bakery AI</h1>
            <p>Your AI assistant is ready to help!</p>
            <p>Try our endpoints:</p>
            <ul style="list-style:none;">
                <li><a href="/docs" target="_blank">📘 API Docs (/docs)</a></li>
                <li><a href="/assistant" target="_blank">🤖 Assistant (/assistant)</a></li>
                <li><a href="/chat" target="_blank">💬 Chat (/chat)</a></li>
            </ul>
        </body>
    </html>
    """
