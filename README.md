# InternAI CareerBot 🎓

A full-stack AI-powered internship assistant chatbot built with **Flask** + **Google Gemini 2.5 Flash**.

## Project Structure

```
InternAI/
├── app.py                          ← Flask backend (routes, Gemini AI, CSV logging)
├── requirements.txt                ← Python dependencies
├── .env.example                    ← Environment variables template
│
├── templates/
│   ├── login.html                  ← Sign-in page
│   ├── signup.html                 ← Create account page
│   └── chat.html                   ← Main chatbot UI (ChatGPT-style)
│
├── static/
│   ├── css/
│   │   └── style.css               ← Shared design system
│   └── js/
│       └── utils.js                ← Shared JS utilities
│
└── data/
    ├── bot_responses.csv           ← Keyword → reply mapping
    ├── conversation_log.csv        ← Auto-generated conversation log
    └── our_first_internship_sgd.py ← EDA script for internship dataset
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your Gemini API key

Get a free key from: https://aistudio.google.com/app/apikey

**Option A — `.env` file (recommended):**
```bash
cp .env.example .env
# Edit .env and add your key:
# GEMINI_API_KEY=your_key_here
```

**Option B — Environment variable:**
```bash
# Windows
set GEMINI_API_KEY=your_key_here

# macOS / Linux
export GEMINI_API_KEY=your_key_here
```

### 3. Run the server

```bash
python app.py
```

Open your browser at: **http://127.0.0.1:5002**

---

## How It Works

1. **Login / Signup** → session stored server-side (Flask session)
2. **User sends a message** → backend checks `bot_responses.csv` for keyword matches first
3. **No keyword match** → message sent to **Google Gemini 2.5 Flash** with full conversation history
4. **Every conversation** is logged to `data/conversation_log.csv` with:
   - conversation_no, session_id, username
   - user_message, matched_keyword, status, process
   - bot_reply, timestamp

## Customising Bot Responses

Edit `data/bot_responses.csv` to add keyword-based quick replies:

```csv
keyword;category;bot_reply
resume;career preparation;A great resume should be...
interview;preparation;Here are 5 key interview tips...
```

Use `;` as delimiter. The bot checks these first before calling Gemini.

## EDA Script

`data/our_first_internship_sgd.py` — Jupyter/Colab notebook script for exploratory data analysis of Singapore internship data (stipends, locations, durations). Run in Google Colab with your `internship_sgd.csv` dataset.

---

## Tech Stack

| Layer     | Technology                    |
|-----------|-------------------------------|
| Backend   | Python 3.11+, Flask 3.x       |
| AI        | Google Gemini 2.5 Flash       |
| Frontend  | HTML5, CSS3, Vanilla JS       |
| Markdown  | marked.js (CDN)               |
| Logging   | CSV (conversation_log.csv)    |
| Auth      | Flask session (demo mode)     |
