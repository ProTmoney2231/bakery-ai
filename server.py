from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# Setup OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Homepage with chat box
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
            .box { background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block; }
            #chat-box { margin-top: 20px; text-align: left; max-width: 400px; margin-left: auto; margin-right: auto; }
            .msg { background: #eee; padding: 10px; margin: 5px 0; border-radius: 8px; }
            .user { background: #d2691e; color: white; text-align: right; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Welcome to Bakery AI 🥐</h1>
            <p>Ask me about breads, cakes, or pastries!</p>
            <input id="user-input" type="text" placeholder="Type your message..." style="padding:10px;width:80%;border-radius:5px;border:1px solid #ccc;">
            <button onclick="sendMessage()" style="padding:10px 15px;margin-left:5px;background:#d2691e;color:white;border:none;border-radius:5px;">Send</button>
            <div id="chat-box"></div>
        </div>

        <script>
            async function sendMessage() {
                const input = document.getElementById("user-input");
                const chatBox = document.getElementById("chat-box");
                const userMsg = input.value;
                if (!userMsg) return;

                chatBox.innerHTML += '<div class="msg user">' + userMsg + '</div>';
                input.value = "";

                const res = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: userMsg })
                });
                const data = await res.json();

                chatBox.innerHTML += '<div class="msg">' + data.reply + '</div>';
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

# Chat endpoint with OpenAI
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Fast & cheap model
            messages=[
                {"role": "system", "content": "You are a helpful bakery assistant. Answer about breads, cakes, and pastries in a friendly way."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Error: {str(e)}"

    return jsonify({"reply": reply})

# Health check
@app.route("/healthz")
def healthz():
    return jsonify({"ok": True, "service": "bakery-ai"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
