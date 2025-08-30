import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# Load .env and read API key
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY) if API_KEY else None

# FastAPI app + CORS
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # fine for local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple dataset of assistants to practice with
ASSISTANTS: Dict[str, Dict[str, Any]] = {
    "coffee_shop": {
        "name": "Bayside Coffee",
        "system_prompt": (
            "You are the helpful website assistant for Bayside Coffee, a local cafe. "
            "Answer concisely. If the user asks about hours, menu, or location, use the facts below. "
            "If something isn't in the facts, answer generally and suggest calling the shop."
        ),
        "facts": (
            "Hours: Mon–Fri 7am–6pm; Sat–Sun 8am–5pm. "
            "Location: 123 Harbor Rd, Santa Clara, CA. "
            "Phone: (408) 555-0199. "
            "Menu highlights: espresso drinks, cold brew, pastries, avocado toast."
        ),
    },
    "dentist": {
        "name": "Bright Smiles Dental",
        "system_prompt": (
            "You are the friendly assistant for Bright Smiles Dental. "
            "Be clear and reassuring. Use the facts below when relevant."
        ),
        "facts": (
            "Services: cleanings, whitening, Invisalign, crowns. "
            "Insurance: most PPO plans, cash, HSA/FSA accepted. "
            "New-patient special: $99 exam + X-rays. "
            "Address: 55 Oak Ave, Sunnyvale, CA. "
            "Phone: (650) 555-0135."
        ),
    },
}

class ChatPayload(BaseModel):
    message: str

@app.get("/")
def root():
    return {"ok": True, "message": "Biz Assistant API is running."}

@app.get("/assistants")
def list_assistants():
    return {"assistants": list(ASSISTANTS.keys())}

@app.post("/chat/{assistant_id}")
def chat(assistant_id: str, payload: ChatPayload):
    if not client:
        raise HTTPException(
            status_code=500,
            detail="Server is missing OPENAI_API_KEY. Put it in .env and restart.",
        )

    assistant = ASSISTANTS.get(assistant_id)
    if not assistant:
        raise HTTPException(status_code=404, detail="Unknown assistant id.")

    user_message = (payload.message or "").strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required.")

    messages = [
        {"role": "system", "content": assistant["system_prompt"]},
        {"role": "system", "content": f'Facts: {assistant["facts"]}'},
        {"role": "user", "content": user_message},
    ]

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4,
        )
        reply = resp.choices[0].message.content
        return {"assistant": assistant_id, "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")
