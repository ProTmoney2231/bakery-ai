from flask import Flask, request, jsonify

app = Flask(__name__)

# Homepage (HTML)
@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bakery AI Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; background: #faf3e0; text-align: center; padding: 50px; }
            h1 { color: #d2691e; }
            p { font-size: 18px; }
            .box { background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block; }
            .chat-link { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #d2691e; color: white; text-decoration: none; border-radius: 5px; }
            .chat-link:hover { background: #a0522d; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Welcome to Bakery AI</h1>
            <p>Your friendly assistant for bakery recommendations 🍞🥐🍰</p>
            <a href="/chat" class="chat-link">Try the Chat API</a>
        </div>
    </body>
    </html>
    """

# Chat API endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # Simple rule-based reply
    if "bread" in user_message.lower():
        reply = "Our sourdough bread is freshly baked and very popular!"
    elif "cake" in user_message.lower():
        reply = "We have chocolate, vanilla, and strawberry cakes available."
    else:
        reply = "Hello! I recommend trying our croissants – they’re buttery and perfect for any time of day."

    return jsonify({"reply": reply})

# Health check
@app.route("/healthz")
def healthz():
    return jsonify({"ok": True, "service": "bakery-ai"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
