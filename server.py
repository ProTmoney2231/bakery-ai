from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI(title="Bakery AI")

HTML_PAGE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Bakery AI Chat</title>
  <style>
    :root{
      --bg:#0b0f14; --panel:#0f1520; --panel-2:#121a27; --text:#e8eef7; --muted:#a5b3c4;
      --accent:#6ee7ff; --accent-2:#63ffb3; --ring:#1e293b;
    }
    *{box-sizing:border-box}
    html,body{height:100%}
    body{
      margin:0; background:linear-gradient(180deg, #0b0f14, #0a1018);
      color:var(--text); font:16px/1.4 system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    }
    /* Floating launcher */
    .launcher{
      position:fixed; right:20px; bottom:20px; z-index:50;
    }
    .launcher button{
      border:0; width:56px; height:56px; border-radius:999px;
      background:linear-gradient(135deg, var(--accent), var(--accent-2));
      color:#001018; font-weight:700; cursor:pointer; box-shadow:0 10px 25px rgba(0,0,0,.35);
      transition:transform .12s ease, box-shadow .12s ease;
    }
    .launcher button:hover{ transform:translateY(-2px); box-shadow:0 14px 32px rgba(0,0,0,.45) }
    .launcher .badge{
      position:absolute; top:-6px; right:-6px; width:18px; height:18px; border-radius:50%;
      background:#ff5577; color:#fff; display:grid; place-items:center; font-size:11px; font-weight:700;
      box-shadow:0 0 0 2px var(--panel);
    }
    /* Chat window */
    .chat{
      position:fixed; right:20px; bottom:88px; width:360px; max-width:calc(100vw - 32px);
      height:520px; background:linear-gradient(180deg, var(--panel), var(--panel-2));
      border:1px solid #142033; border-radius:20px; box-shadow:0 16px 48px rgba(0,0,0,.45);
      overflow:hidden; display:none; flex-direction:column;
    }
    .chat.show{ display:flex; }
    .chat header{
      padding:14px 16px; display:flex; align-items:center; gap:12px; border-bottom:1px solid #142033;
      background:linear-gradient(180deg, rgba(255,255,255,.02), rgba(255,255,255,0));
    }
    .avatar{ width:34px; height:34px; border-radius:10px; background:linear-gradient(135deg, var(--accent), var(--accent-2)); }
    .title{ font-weight:700 }
    .subtitle{ color:var(--muted); font-size:12px }
    .messages{
      padding:16px; gap:10px; display:flex; flex-direction:column;
      overflow:auto; height:100%;
      scrollbar-width:thin; scrollbar-color:#203047 transparent;
    }
    .msg{
      max-width:82%; padding:10px 12px; border-radius:14px; word-wrap:break-word; white-space:pre-wrap;
    }
    .bot{ background:#0e1726; border:1px solid #18243a; color:var(--text) }
    .user{
      align-self:flex-end; background:linear-gradient(135deg, #2dd4bf, #60a5fa);
      color:#031019; font-weight:600;
    }
    .typing{ display:inline-block; width:36px; }
    .dot{ width:6px; height:6px; margin:0 2px; background:#9fb3c7; border-radius:50%; display:inline-block; animation:blink 1.2s infinite }
    .dot:nth-child(2){ animation-delay:.15s } .dot:nth-child(3){ animation-delay:.3s }
    @keyframes blink{ 0%,80%,100%{opacity:.2} 40%{opacity:1} }
    form{
      display:flex; gap:8px; padding:12px; border-top:1px solid #142033; background:#0c131f;
    }
    input[type="text"]{
      flex:1; padding:12px 12px; border-radius:12px; border:1px solid #1a2940; background:#0b1320; color:var(--text);
      outline:none; transition:border-color .12s ease, box-shadow .12s ease;
    }
    input[type="text"]:focus{ border-color:#2e4363; box-shadow:0 0 0 3px rgba(100,149,237,.15) }
    button.send{
      padding:0 14px; border-radius:10px; border:0; background:#173055; color:#e9f0fb; font-weight:700; cursor:pointer;
    }
    button.send:disabled{ opacity:.6; cursor:not-allowed }
    /* Landing hint when the window is closed */
    .hero{
      position:fixed; inset:0; display:grid; place-items:center; pointer-events:none; user-select:none;
    }
    .card{
      background:linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.01));
      border:1px solid #142033; padding:22px 20px; border-radius:16px; max-width:560px; text-align:center;
      box-shadow:0 20px 60px rgba(0,0,0,.35);
    }
    .card h1{ margin:0 0 6px; font-size:26px }
    .card p{ margin:0; color:var(--muted) }
  </style>
</head>
<body>
  <div class="hero">
    <div class="card">
      <h1>Welcome to <strong>Bakery&nbsp;AI</strong> 🍰</h1>
      <p>Tap the bubble to chat—ask for pastry recs, hours, or today’s treats.</p>
    </div>
  </div>

  <div class="launcher">
    <button id="toggle" aria-label="Open chat">💬</button>
    <div class="badge" id="badge" title="New">1</div>
  </div>

  <section class="chat" id="chat">
    <header>
      <div class="avatar" aria-hidden="true"></div>
      <div>
        <div class="title">Bakery AI</div>
        <div class="subtitle">Ask about pastries, hours & more</div>
      </div>
    </header>

    <div class="messages" id="messages" role="log" aria-live="polite" aria-relevant="additions"></div>

    <form id="form" autocomplete="off">
      <input id="input" type="text" placeholder="Type a message…" aria-label="Chat message" />
      <button class="send" id="send" type="submit">Send</button>
    </form>
  </section>

  <script>
    const chat = document.getElementById('chat');
    const toggle = document.getElementById('toggle');
    const badge = document.getElementById('badge');
    const messages = document.getElementById('messages');
    const form = document.getElementById('form');
    const input = document.getElementById('input');
    const sendBtn = document.getElementById('send');

    function scrollToBottom(){ messages.scrollTop = messages.scrollHeight; }
    function el(tag, cls, text){
      const n = document.createElement(tag);
      if(cls) n.className = cls;
      if(text !== undefined) n.textContent = text;
      return n;
    }
    function addMessage(role, text){
      const css = role === 'user' ? 'msg user' : 'msg bot';
      messages.appendChild(el('div', css, text));
      scrollToBottom();
    }
    function addTyping(){
      const wrap = el('div', 'msg bot typing');
      wrap.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
      messages.appendChild(wrap);
      scrollToBottom();
      return wrap;
    }
    function greetOnce(){
      if(messages.children.length === 0){
        addMessage('bot', "Hi! I’m your pastry helper. Ask about croissants, muffins, baguettes, our hours, or say hi 👋");
      }
    }

    toggle.addEventListener('click', () => {
      chat.classList.toggle('show');
      if(chat.classList.contains('show')){ badge.style.display = 'none'; greetOnce(); input.focus(); }
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if(!text) return;
      addMessage('user', text);
      input.value = '';
      input.focus();
      sendBtn.disabled = true;

      const typing = addTyping();
      try{
        const res = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text })
        });
        const data = await res.json().catch(() => ({}));
        messages.removeChild(typing);
        addMessage('bot', data.reply || "Sorry—couldn't parse a reply.");
      }catch(err){
        messages.removeChild(typing);
        addMessage('bot', "Hmm, I hit a snag talking to the server.");
      }finally{
        sendBtn.disabled = false;
      }
    });

    // Open chat on first load with a gentle nudge
    setTimeout(() => { badge.style.display = 'none'; chat.classList.add('show'); greetOnce(); }, 500);
  </script>
</body>
</html>
"""

def _reply_for(message: str) -> str:
    """Tiny rule-based reply (no external deps)."""
    m = (message or "").strip().lower()
    if not m:
        return "Say something and I’ll help!"
    if "hour" in m or "open" in m or "close" in m:
        return "We’re open daily 7:00 AM – 6:00 PM. Weekend brunch starts 9:00 AM 🕖"
    if "menu" in m or "pastry" in m:
        return "Today’s picks: butter croissant 🥐, blueberry muffin 🫐, and almond biscotti."
    if "croissant" in m:
        return "Our butter croissant is flaky, slow-laminated, and best warmed 5 minutes at 325°F."
    if "muffin" in m:
        return "Blueberry muffins are baked hourly—soft crumb, lemon zest, and turbinado top."
    if "baguette" in m:
        return "Classic baguette: 24h poolish, crackly crust, chewy interior—great with jam!"
    if "hi" in m or "hello" in m or "hey" in m:
        return "Hello! What pastry are you in the mood for?"
    return f"I heard: “{message}”. Ask me about hours, croissants, muffins, baguettes, or our menu."

@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return HTMLResponse(HTML_PAGE)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    return {"reply": _reply_for(message)}

# Optional compatibility endpoint
@app.post("/assistant")
async def assistant(request: Request):
    data = await request.json()
    return {"reply": _reply_for(data.get("message", ""))}

# Simple health check
@app.get("/healthz")
def healthz():
    return {"ok": True, "service": "bakery-ai", "time": datetime.utcnow().isoformat() + "Z"}

# Local dev entrypoint (ignored by Render)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=10000, reload=True)
