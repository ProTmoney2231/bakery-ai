import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/assistant", methods=["POST"])
@app.route("/chat", methods=["POST"])  # 👈 /chat is now an alias
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant for a bakery website."},
            {"role": "user", "content": user_message}
        ]
    )

    reply = completion.choices[0].message.content
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
