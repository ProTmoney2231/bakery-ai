from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI(title="bakery-ai")

@app.get("/")
async def root():
    return {"ok": True, "service": "bakery-ai", "status": "healthy"}

class ChatIn(BaseModel):
    message: str

@app.post("/assistant")
async def assistant(body: ChatIn):
    return {
        "reply": f"Hello! You said: '{body.message}'. Try our almond croissant today. 🥐"
    }

@app.post("/chat")
async def chat(body: ChatIn):
    return {
        "reply": "Top picks: raspberry tart, almond croissant, and sourdough loaf."
    }

# Optional local run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
