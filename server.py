from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"reply": "Hi! Ask me about today’s pastries 😊"})

    low = msg.lower()
    if "recommend" in low or "suggest" in low or "best" in low:
        reply = "Today’s bestsellers: Almond Croissant, Lemon Cupcake, and our Sourdough Loaf 🥐🧁🍞"
    elif "hours" in low or "open" in low or "time" in low:
        reply = "We’re open daily from 7:00 AM to 7:00 PM."
    elif "location" in low or "address" in low:
        reply = "Find us on Main Street, next to the park. Plenty of parking!"
    else:
        reply = f"Thanks for your message! For now I’m a simple demo bot—here’s what I heard: “{msg}”."
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
