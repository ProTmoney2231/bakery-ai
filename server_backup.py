from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os, datetime, json, glob, csv, tempfile, zipfile

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise HTTPException(status_code=500, detail="Missing OPENAI_API_KEY in .env file")

client = OpenAI(api_key=api_key)

app = FastAPI()

# Allow local HTML/JS to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message: str

# Ensure logs folder exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_conversation(user_msg, bot_reply):
    today = datetime.date.today().isoformat()
    filename = os.path.join(LOG_DIR, f"{today}.jsonl")
    with open(filename, "a") as f:
        record = {
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "user": user_msg,
            "bot": bot_reply,
        }
        f.write(json.dumps(record) + "\n")

@app.post("/assistant")
async def chat_with_assistant(msg: Message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a friendly assistant for Sweet Treats Bakery. Be warm and concise."},
                {"role": "user", "content": msg.message},
            ],
            max_tokens=200,
        )
        reply = response.choices[0].message.content
        log_conversation(msg.message, reply)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Download logs as JSONL
@app.get("/download-logs")
async def download_logs():
    today = datetime.date.today().isoformat()
    filename = os.path.join(LOG_DIR, f"{today}.jsonl")
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="No logs found for today.")
    return FileResponse(filename, media_type="application/json", filename=f"{today}-logs.jsonl")

# Download logs as CSV
@app.get("/download-logs-csv")
async def download_logs_csv():
    today = datetime.date.today().isoformat()
    jsonl_file = os.path.join(LOG_DIR, f"{today}.jsonl")
    if not os.path.exists(jsonl_file):
        raise HTTPException(status_code=404, detail="No logs found for today.")

    tmp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    with open(jsonl_file) as infile, open(tmp_csv.name, "w", newline="") as csvfile:
        import csv
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "user", "bot"])
        for line in infile:
            rec = json.loads(line)
            writer.writerow([rec["timestamp"], rec["user"], rec["bot"]])

    return FileResponse(tmp_csv.name, media_type="text/csv", filename=f"{today}-logs.csv")

# Download ALL logs as ZIP
@app.get("/download-all-logs")
async def download_all_logs():
    zip_path = tempfile.NamedTemporaryFile(delete=False, suffix=".zip").name
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in glob.glob(os.path.join(LOG_DIR, "*.jsonl")):
            zipf.write(file, os.path.basename(file))
    return FileResponse(zip_path, media_type="application/zip", filename="all-logs.zip")

# Clear today’s logs
@app.post("/clear-logs")
async def clear_logs():
    today = datetime.date.today().isoformat()
    filename = os.path.join(LOG_DIR, f"{today}.jsonl")
    if os.path.exists(filename):
        os.remove(filename)
        return {"status": "success", "message": f"Logs for {today} cleared."}
    else:
        return {"status": "info", "message": "No logs to clear today."}

# Pretty logs page with search + date filter + clear logs button
@app.get("/logs", response_class=HTMLResponse)
async def view_logs():
    # Collect available dates
    log_files = sorted(glob.glob(os.path.join(LOG_DIR, "*.jsonl")))
    dates = [os.path.basename(f).replace(".jsonl", "") for f in log_files]

    html = """
    <html>
    <head>
        <title>Chat Logs</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f9f9f9; padding: 20px; }
            h1 { color: #333; }
            h2 { background: #eee; padding: 8px; border-radius: 8px; }
            .chat-container { max-width: 900px; margin: auto; }
            .message { padding: 10px 15px; margin: 10px; border-radius: 12px; max-width: 70%; }
            .user { background: #d1e7ff; margin-left: auto; text-align: right; }
            .bot { background: #e8f5e9; margin-right: auto; text-align: left; }
            small { display: block; color: #777; font-size: 11px; margin-top: 4px; }
            li { list-style: none; }
            .btn {
                display: inline-block;
                margin: 10px 10px 20px 0;
                padding: 10px 20px;
                background: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
            }
            .btn:hover { background: #45a049; }
            .btn-danger { background: #e53935; }
            .btn-danger:hover { background: #c62828; }
            #searchBar, #dateFilter {
                margin: 15px 10px 15px 0;
                padding: 10px;
                font-size: 16px;
                border: 1px solid #ccc;
                border-radius: 8px;
            }
            mark { background: yellow; font-weight: bold; }
        </style>
        <script>
            function filterLogs() {
                let input = document.getElementById('searchBar').value.toLowerCase();
                let items = document.getElementsByClassName('log-entry');

                for (let i = 0; i < items.length; i++) {
                    let text = items[i].innerText.toLowerCase();
                    if (text.includes(input)) {
                        items[i].style.display = "";
                        highlight(items[i], input);
                    } else {
                        items[i].style.display = "none";
                    }
                }
            }

            function highlight(element, query) {
                let innerHTML = element.innerHTML;
                let regex = new RegExp("("+query+")", "gi");
                element.innerHTML = innerHTML.replace(/<mark>|<\/mark>/g, "");
                if (query.length > 0) {
                    element.innerHTML = innerHTML.replace(regex, "<mark>$1</mark>");
                }
            }

            function filterByDate() {
                let selectedDate = document.getElementById('dateFilter').value;
                let sections = document.getElementsByClassName('log-section');

                for (let i = 0; i < sections.length; i++) {
                    if (selectedDate === "all" || sections[i].id === selectedDate) {
                        sections[i].style.display = "";
                    } else {
                        sections[i].style.display = "none";
                    }
                }
            }

            async function clearLogs() {
                if (!confirm("⚠️ Are you sure you want to clear today’s logs?")) return;
                let response = await fetch("/clear-logs", { method: "POST" });
                let result = await response.json();
                alert(result.message);
                location.reload();
            }
        </script>
    </head>
    <body>
        <div class="chat-container">
        <h1>📜 Chat Logs</h1>
        <input type="text" id="searchBar" onkeyup="filterLogs()" placeholder="🔍 Search logs...">
        <select id="dateFilter" onchange="filterByDate()">
            <option value="all">📅 Show All Dates</option>
    """
    # Add dates to dropdown
    for d in dates:
        html += f'<option value="{d}">{d}</option>'
    html += "</select><br>"

    html += """
        <a href="/download-logs" class="btn">⬇️ Today JSONL</a>
        <a href="/download-logs-csv" class="btn">⬇️ Today CSV</a>
        <a href="/download-all-logs" class="btn">⬇️ ALL Logs (ZIP)</a>
        <button onclick="clearLogs()" class="btn btn-danger">🗑️ Clear Today’s Logs</button>
    """

    # Show logs grouped by date
    for file in log_files:
        date = os.path.basename(file).replace(".jsonl", "")
        html += f"<div class='log-section' id='{date}'><h2>{date}</h2><ul>"
        with open(file) as f:
            for line in f:
                rec = json.loads(line)
                html += f"""
                <li class="log-entry">
                    <div class="message user">{rec['user']}<small>{rec['timestamp']}</small></div>
                    <div class="message bot">{rec['bot']}</div>
                </li>
                """
        html += "</ul></div>"

    html += "</div></body></html>"
    return html
