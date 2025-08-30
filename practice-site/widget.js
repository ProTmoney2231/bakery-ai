(function () {
  const cfg = (window.BIZ_ASSISTANT_CONFIG || {});
  const ENDPOINT = cfg.endpoint || "http://127.0.0.1:8000";
  let ASSISTANT = cfg.assistantId || "coffee_shop";

  // ---- Styles (injected) ----
  const style = document.createElement('style');
  style.textContent = `
    #biz-chat-btn {
      position: fixed; right: 20px; bottom: 20px;
      padding: 12px 16px; border-radius: 999px; border: none; cursor: pointer;
      box-shadow: 0 4px 12px rgba(0,0,0,.15);
    }
    #biz-chat-box {
      position: fixed; right: 20px; bottom: 80px; width: 320px; height: 420px;
      background: #fff; border: 1px solid #ddd; border-radius: 12px;
      box-shadow: 0 8px 24px rgba(0,0,0,.2); display: none; overflow: hidden;
      font-family: system-ui, -apple-system, Arial, sans-serif;
    }
    #biz-chat-header {
      background: #111827; color: white; padding: 10px 12px; display: flex; align-items: center; justify-content: space-between;
    }
    #biz-chat-title { font-weight: 600; }
    #biz-chat-close { background: transparent; color: white; border: none; cursor: pointer; font-size: 16px; }
    #biz-chat-log { height: 300px; overflow-y: auto; padding: 8px 10px; background: #f9fafb; }
    .biz-msg { margin: 6px 0; padding: 8px 10px; border-radius: 8px; }
    .biz-user { background: #dbeafe; align-self: flex-end; }
    .biz-bot { background: #e5e7eb; }
    #biz-chat-inputbar { display: flex; gap: 6px; padding: 8px; border-top: 1px solid #eee; }
    #biz-chat-input { flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 8px; }
    #biz-chat-send { padding: 8px 12px; border: none; border-radius: 8px; cursor: pointer; background: #2563eb; color: white; }
    #biz-chat-select { margin-left: 6px; }
  `;
  document.head.appendChild(style);

  // ---- Elements ----
  const box = document.createElement('div');
  box.id = 'biz-chat-box';
  box.innerHTML = `
    <div id="biz-chat-header">
      <div>
        <span id="biz-chat-title">Assistant</span>
        <select id="biz-chat-select" title="Pick assistant">
          <option value="coffee_shop">coffee_shop</option>
          <option value="dentist">dentist</option>
        </select>
      </div>
      <button id="biz-chat-close" aria-label="Close">✕</button>
    </div>
    <div id="biz-chat-log"></div>
    <div id="biz-chat-inputbar">
      <input id="biz-chat-input" placeholder="Type a message..." />
      <button id="biz-chat-send">Send</button>
    </div>
  `;
  document.body.appendChild(box);

  const btn = document.createElement('button');
  btn.id = 'biz-chat-btn';
  btn.textContent = 'Chat';
  document.body.appendChild(btn);

  // Select current assistant
  const select = box.querySelector('#biz-chat-select');
  select.value = ASSISTANT;
  select.addEventListener('change', () => {
    ASSISTANT = select.value;
    title.textContent = `Assistant: ${ASSISTANT}`;
    log.innerHTML = '';
    addMsg('bot', `Switched to ${ASSISTANT}. Ask me anything!`);
  });

  const log = box.querySelector('#biz-chat-log');
  const input = box.querySelector('#biz-chat-input');
  const send = box.querySelector('#biz-chat-send');
  const close = box.querySelector('#biz-chat-close');
  const title = box.querySelector('#biz-chat-title');

  title.textContent = `Assistant: ${ASSISTANT}`;

  function addMsg(role, text) {
    const div = document.createElement('div');
    div.className = 'biz-msg ' + (role === 'user' ? 'biz-user' : 'biz-bot');
    div.textContent = (role === 'user' ? 'You: ' : 'Bot: ') + text;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
  }

  async function ask() {
    const msg = (input.value || '').trim();
    if (!msg) return;
    addMsg('user', msg);
    input.value = '';
    try {
      const r = await fetch(`${ENDPOINT}/chat/${ASSISTANT}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      const data = await r.json();
      addMsg('bot', data.reply || '(no reply)');
    } catch (e) {
      addMsg('bot', 'Error reaching server.');
    }
  }

  // Events
  btn.onclick = () => { box.style.display = 'block'; addMsg('bot', `Hi! You are chatting with ${ASSISTANT}.`); };
  close.onclick = () => { box.style.display = 'none'; };
  send.onclick = ask;
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') ask(); });
})();
