# ============================================================
#  InternAI — Flask Backend
#  Uses Google Gemini 2.5 Flash for AI responses
#  Logs all conversations to data/conversation_log.csv
# ============================================================

from flask import Flask, render_template, request, jsonify, session
from google import genai
from google.genai import types
import csv
from datetime import datetime
import os
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "internai-secret-2025")

# ── File paths ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Create data folder automatically if it does not exist
os.makedirs(DATA_DIR, exist_ok=True)

BOT_DATA_FILE = os.path.join(DATA_DIR, "bot_responses.csv")
LOG_FILE      = os.path.join(DATA_DIR, "conversation_log.csv")
USER_FILE     = os.path.join(DATA_DIR, "users.csv")
EDA_SCRIPT    = os.path.join(DATA_DIR, "our_first_internship_sgd.py")

# ── Google Gemini client ─────────────────────────────────────
# Store the key in an environment variable. Never hard-code API keys here.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

SYSTEM_PROMPT = """You are CareerBot, a friendly and knowledgeable career and internship 
support assistant for university students in Singapore and beyond.

Your expertise covers:
- Finding and applying for internships (local and overseas)
- Resume and CV writing tailored for students
- Cover letter crafting
- Interview preparation (behavioral and technical)
- Salary and stipend expectations (especially SGD rates)
- Networking and LinkedIn tips
- Career planning and skill development
- Understanding internship data and trends

Important rules:
- Be concise, warm, and actionable
- Use markdown formatting: **bold**, bullet lists, headers when helpful
- Do NOT invent official university deadlines, specific job links, or active vacancies
- When official info is needed, advise checking the university's career portal
- If asked about Singapore internship stipends, typical ranges are S$800–S$1,500/month
  for most fields; tech roles often S$1,000–S$2,000+/month
- Keep answers focused and under 300 words unless a detailed breakdown is requested
"""


# ── Load keyword responses from CSV ─────────────────────────
def load_bot_responses():
    """Load keyword→reply mappings from bot_responses.csv."""
    responses = []
    if not os.path.exists(BOT_DATA_FILE):
        return responses
    try:
        with open(BOT_DATA_FILE, "r", newline="", encoding="utf-8-sig") as f:
            first_line = f.readline()
            delimiter = ";" if ";" in first_line else ","
            f.seek(0)
            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                clean = {k.strip(): (v.strip() if v else "") for k, v in row.items() if k}
                responses.append(clean)
    except Exception as e:
        print(f"[WARN] Could not load bot_responses.csv: {e}")
    return responses


BOT_RESPONSES = load_bot_responses()


def match_keyword(user_message: str):
    """Try to match user message against keyword CSV. Returns (reply, keyword) or (None, None)."""
    msg_lower = user_message.lower()
    for row in BOT_RESPONSES:
        keyword = row.get("keyword", "").lower()
        if keyword and keyword in msg_lower:
            return row.get("bot_reply", ""), row.get("keyword", "")
    return None, None


# ── Gemini AI response ───────────────────────────────────────
def get_gemini_reply(user_message: str, history: list):
    """Call Gemini 2.5 Flash with full conversation history."""
    if not client:
        return (
            "⚠️ Gemini API key not configured. Set the `GEMINI_API_KEY` environment variable to enable AI responses.",
            "error",
            "No API key"
        )

    try:
        # Build contents list from history + current message
        contents = []
        for turn in history[-10:]:   # keep last 10 turns for context
            contents.append(types.Content(
                role="user",
                parts=[types.Part(text=turn["user"])]
            ))
            if turn.get("bot"):
                contents.append(types.Content(
                    role="model",
                    parts=[types.Part(text=turn["bot"])]
                ))
        # Add current message
        contents.append(types.Content(
            role="user",
            parts=[types.Part(text=user_message)]
        ))

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=600,
            )
        )
        return response.text, "answered", "Gemini 2.5 Flash"

    except Exception as e:
        print(f"[ERROR] Gemini API: {e}")
        return (
            "Sorry, I couldn't generate a response right now. Please try again in a moment.",
            "error",
            f"Gemini error: {str(e)[:80]}"
        )


# ── Conversation logger ──────────────────────────────────────
def get_next_conversation_no():
    if not os.path.exists(LOG_FILE):
        return 1
    with open(LOG_FILE, "r", newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f)) + 1


def save_conversation(username, session_id, user_message, matched_keyword, status, process, bot_reply):
    os.makedirs(DATA_DIR, exist_ok=True)

    conversation_no = get_next_conversation_no()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.exists(LOG_FILE)
    fieldnames = [
        "conversation_no", "session_id", "username",
        "user_message", "matched_keyword", "status",
        "process", "bot_reply", "timestamp"
    ]
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "conversation_no": conversation_no,
            "session_id": session_id,
            "username": username,
            "user_message": user_message,
            "matched_keyword": matched_keyword or "",
            "status": status,
            "process": process,
            "bot_reply": bot_reply,
            "timestamp": timestamp
        })

# ── User account CSV ──────────────────────────────────────────
def ensure_user_file():
    os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)

    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w", newline="", encoding="utf-8") as f:
            f.write("firstName;lastName;email;username;password;agree\n")


def user_exists(username, email):
    ensure_user_file()

    with open(USER_FILE, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")

        for row in reader:
            existing_username = (row.get("username") or "").strip().lower()
            existing_email = (row.get("email") or "").strip().lower()

            if existing_username == username.lower():
                return "Username already exists."
            if existing_email == email.lower():
                return "Email already exists."

    return None


def save_user_account(first_name, last_name, email, username, password, agree):
    ensure_user_file()

    with open(USER_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["firstName", "lastName", "email", "username", "password", "agree"],
            delimiter=";"
        )

        writer.writerow({
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "username": username,
            "password": password,
            "agree": agree
        })

# ── Routes ───────────────────────────────────────────────────
@app.route("/")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/chat")
def chat_page():
    if "username" not in session:
        return render_template("login.html")
    return render_template("chat.html", username=session["username"])

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()

    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    # Simple demo login for now.
    # User Story 17 will later validate this from users.csv.
    session["username"] = username
    session["session_id"] = str(uuid.uuid4())
    session["history"] = []

    return jsonify({"success": True, "username": username})

@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json()

    first_name = (data.get("firstName") or "").strip()
    last_name  = (data.get("lastName") or "").strip()
    name       = (data.get("name") or "").strip()

    username = (data.get("username") or "").strip()
    email    = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()
    agree    = str(data.get("agree") or "yes").strip()

    # If frontend sends full name instead of firstName/lastName
    if name and not first_name:
        name_parts = name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

    if not first_name or not username or not email or not password:
        return jsonify({"error": "All fields are required."}), 400

    existing_error = user_exists(username, email)
    if existing_error:
        return jsonify({"error": existing_error}), 400

    save_user_account(first_name, last_name, email, username, password, agree)

    session["username"] = username
    session["session_id"] = str(uuid.uuid4())
    session["history"] = []

    return jsonify({"success": True, "username": username})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"success": True})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    username    = (data.get("username") or session.get("username", "guest")).strip()
    user_message = (data.get("message") or "").strip()
    session_id  = session.get("session_id", str(uuid.uuid4()))

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    history = session.get("history", [])

    # 1. Try keyword match first
    keyword_reply, matched_kw = match_keyword(user_message)

    if keyword_reply:
        bot_reply = keyword_reply
        status    = "keyword_match"
        process   = f"Matched keyword: '{matched_kw}'"
    else:
        # 2. Fall back to Gemini AI
        matched_kw = None
        bot_reply, status, process = get_gemini_reply(user_message, history)

    # Update history
    history.append({"user": user_message, "bot": bot_reply})
    session["history"] = history[-20:]   # keep last 20 turns

    # Log to CSV
    save_conversation(username, session_id, user_message, matched_kw, status, process, bot_reply)

    return jsonify({
        "reply": bot_reply,
        "process": process,
        "status": status
    })


@app.route("/api/history")
def api_history():
    """Return last 50 log entries for the dashboard."""
    entries = []
    if not os.path.exists(LOG_FILE):
        return jsonify(entries)
    with open(LOG_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append(row)
    return jsonify(entries[-50:])


@app.route("/api/clear_history", methods=["POST"])
def clear_history():
    session["history"] = []
    return jsonify({"success": True})


if __name__ == "__main__":
    print("=" * 55)
    print("  InternAI CareerBot — Flask Server")
    print(" http://127.0.0.1:5002")
    if not GEMINI_API_KEY:
        print("  ⚠  GEMINI_API_KEY not set — AI responses disabled")
    print("=" * 55)
    app.run(debug=True, port=5002)
