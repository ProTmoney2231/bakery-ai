from flask import Flask, request, jsonify

app = Flask(__name__)

# Homepage (with chat box)
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

                // Add user message
                chatBox.innerHTML += '<div class="msg user">' + userMsg + '</div>';
                input.value = "";

                // Send to backend
                const res = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: userMsg })
                });
                const data = await res.json();

                // Add AI reply
                chatBox.innerHTML += '<div class="msg">' + data.reply + '</div>';
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

# Chat API endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if "bread" in user_message.lower():
        reply = "Our sourdough bread is freshly baked and very popular!"
    elif "cake" in user_message.lower():
        reply = "We have chocolate, vanilla, and strawberry cakes available."
    else:
        reply = "Hello! I recommend trying our croissants – buttery and perfect any time of day."

    return jsonify({"reply": reply})

# Health check
@app.route("/healthz")
def healthz():
    return jsonify({"ok": True, "service": "bakery-ai"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
