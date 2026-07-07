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

===========================================

## Iteration 1 - Completed User Stories

### Core Infrastructure (Priority 50)

| # | User Story | Description | Effort |
|---|-----------|-------------|--------|
|  **#1** | **Access Chatbot Website** | As a JCU student, I want to open the chatbot website so that I can access career and internship support online. | 1 day |
|  **#2** | **Send Chat Message** | As a JCU student, I want to type and send a message so that I can interact with the chatbot. | 1 day |
|  **#3** | **Receive AI Chatbot Reply** | As a JCU student, I want to receive a relevant response to my career or internship question so that I can obtain guidance quickly. | 2 days |
|  **#4** | **Integrate Gemini API** | As a development team, we want to connect the chatbot backend to the Gemini API so that the chatbot can generate flexible responses. | 3 days |
|  **#5** | **Record Conversation Data** | As a development team, we want each user interaction to be automatically saved so that we can review user questions and improve the chatbot later. | 2 days |
|  **#7** | **Create Flask Backend** | As a development team, we want a Flask backend to receive user messages, call the chatbot model, return replies, and save interaction data. | 2 days |

## Unfinished Iteration : 

1. Clean Internship Dataset
2. Select Useful Internship Columns
3. Define Chatbot Scope
4. Prepare Sample User Questions
5. Design Create Account and Sign In Pages
6. Save New User Account to CSV
7. Validate User Sign In from CSV
8. Show Account Not Found Message
9. Redirect User After Account Creation
10. Test Chatbot on Different Devices

## Iteration 2 Backlog

| # | User Story Title | Priority | Duration | Status | Assigned To |
|---|------------------|----------|----------|--------|-------------|
|  **#11** | **Clean Internship Dataset** | 50 | 3 days | **Completed** |  
|  **#12** | **Select Useful Internship Columns** | 50 | 2 days | **Working** | Airishlie |
|  **#13** | **Define Chatbot Scope** | 40 | 1 day | **Working** | Henry |
|  **#14** | **Prepare Sample User Questions** | 40 | 2 days | **Working** | Pinky |

###  TODO Stories - Account System

| # | User Story Title | Priority | Duration | Status |
|---|------------------|----------|----------|--------|
|  **#15** | **Design Create Account and Sign In Pages** | 50 | 3 days | **TODO** |  
|  **#16** | **Save New User Account to CSV** | 50 | 2 days | **TODO** | 
|  **#17** | **Validate User Sign In from CSV** | 50 | 2 days | **TODO** | 
|  **#18** | **Show Account Not Found Message** | 40 | 1 day | **TODO** | 
|  **#19** | **Redirect User After Account Creation** | 40 | 1 day | **TODO** | 
|  **#20** | **Test Chatbot on Different Devices** | 40 | 2 days | **TODO** | 
