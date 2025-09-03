import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/healthz")
def healthz():
    return jsonify(ok=True, service="bakery-ai")

def _fallback_reply(user_msg: str) -> str:
    msg = (user_msg or "").lower()
    if any(k in msg for k in ["chocolate", "brownie", "cookie"]):
        return "Chocolate lover? Try our triple-chocolate brownie or warm chocolate chip cookies 🍪"
    if any(k in msg for k in ["croissant", "butter", "flaky"]):
        return "Buttery & flaky croissant just came out of the oven 🥐 — almond croissant is a crowd favorite!"
    if any(k in msg for k in ["cake", "birthday", "party"]):
        return "For celebrations, our vanilla bean cake with strawberry compote is perfect 🎂"
    if any(k in msg for k in ["coffee", "latte", "espresso"]):
        return "Pair a hazelnut latte with a pistachio biscotti ☕️"
    return ("Welcome to Sweet Treats Bakery! Tell me what you’re craving — fruity, chocolatey, "
            "flaky, or gluten-free — and I’ll suggest the perfect pastry 💬")

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    user_msg = str(data.get("message", "")).strip()

    if not user_msg:
        return jsonify(reply="Tell me what you’re craving and I’ll suggest something ❤️")

    # Try OpenAI if available, otherwise fall back to suggestions
    reply = None
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                system = (
                    "You are a friendly pastry concierge for a local bakery called "
                    "'Sweet Treats Bakery'. Be concise, warm, and specific with 1–3 "
                    "suggestions max. Offer pairing ideas and note allergies if mentioned."
                )
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=0.7,
                    max_tokens=220,
                )
                reply = (res.choices[0].message.content or "").strip()
            except Exception:
                reply = None
    except Exception:
        reply = None

    if not reply:
        reply = _fallback_reply(user_msg)

    return jsonify(reply=reply)

if __name__ == "__main__":
    # Local dev convenience; Render will use Gunicorn via Procfile
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
