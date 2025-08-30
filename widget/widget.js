(function () {
  // Floating button
  const button = document.createElement("button");
  button.innerText = "Chat";
  Object.assign(button.style, {
    position: "fixed", bottom: "20px", right: "20px",
    padding: "10px 14px", borderRadius: "999px", border: "0",
    boxShadow: "0 6px 16px rgba(0,0,0,.15)", cursor: "pointer"
  });
  document.body.appendChild(button);

  // Chat window
  const box = document.createElement("div");
  Object.assign(box.style, {
    position: "fixed", bottom: "70px", right: "20px",
    width: "320px", height: "420px", background: "#fff",
    border: "1px solid #ddd", borderRadius: "12px",
    boxShadow: "0 8px 24px rgba(0,0,0,.18)", display: "none",
    fontFamily: "system-ui, sans-serif", overflow: "hidden",
    display: "flex", flexDirection: "column"
  });

  const header = document.createElement("div");
  header.textContent = "Assistant";
  Object.assign(header.style, { padding: "10px", fontWeight: "600", borderBottom: "1px solid #eee" });
  box.appendChild(header);

  const log = document.createElement("div");
  Object.assign(log.style, { flex: "1", padding: "10px", overflowY: "auto", fontSize: "14px" });
  box.appendChild(log);

  const input = document.createElement("input");
  Object.assign(input, { type: "text", placeholder: "Type a message..." });
  Object.assign(input.style, { border: "0", borderTop: "1px solid #eee", padding: "10px" });
  box.appendChild(input);

  document.body.appendChild(box);

  function add(role, text) {
    const el = document.createElement("div");
    el.style.margin = "6px 0";
    el.innerHTML = `<strong>${role}:</strong> ${text}`;
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
  }

  button.onclick = () => { box.style.display = (box.style.display === "none" ? "flex" : "none"); input.focus(); };

  input.addEventListener("keypress", async (e) => {
    if (e.key === "Enter") {
      const q = input.value.trim();
      if (!q) return;
      add("You", q);
      input.value = "";

      try {
        const res = await fetch("http://127.0.0.1:8000/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: q })
        });
        const data = await res.json();
        add("AI", data.reply || "(no reply)");
      } catch (err) {
        add("AI", "Could not reach the server. Is it running?");
      }
    }
  });
})();
