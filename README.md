# InternAI CareerBot 🎓

A full-stack AI-powered internship and career assistant prototype built with **Flask** and **Google Gemini 2.5 Flash**.

The current version supports AI chat, keyword-based responses, conversation logging, and account-page interfaces. The account backend and dataset-powered internship search are still under development.

## Project Status

| Area | Current Status |
|---|---|
| AI chatbot prototype | Completed |
| Gemini API integration | Completed |
| Conversation logging | Completed |
| Internship dataset cleaning | Completed |
| Chatbot scope and sample questions | Completed |
| Create Account and Sign In pages | Completed |
| CSV-based account backend | In progress |
| Internship search and filtering | Planned for Iteration 3 |

---

## Project Structure

```text
InternAI/
├── app.py                          # Flask backend, routes, Gemini AI, and CSV logging
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
│
├── templates/
│   ├── login.html                 # Sign In page
│   ├── signup.html                # Create Account page
│   └── chat.html                  # Main chatbot interface
│
├── static/
│   ├── css/
│   │   └── style.css              # Shared design system
│   └── js/
│       └── utils.js               # Shared JavaScript utilities
│
└── data/
    ├── bot_responses.csv           # Keyword-to-response mapping
    ├── conversation_log.csv        # Automatically generated conversation log
    ├── internship_sgd.csv          # Cleaned Singapore internship dataset
    ├── users.csv                   # Account data storage; backend integration in progress
    └── our_first_internship_sgd.py # Dataset cleaning and exploratory analysis script
```

> Some files, such as `conversation_log.csv` and `users.csv`, may be created or updated automatically when the relevant features run.

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set the Gemini API key

Create a Gemini API key through Google AI Studio.

**Option A — `.env` file (recommended):**

```bash
cp .env.example .env
```

Then add the key to `.env`:

```env
GEMINI_API_KEY=your_key_here
```

**Option B — Environment variable:**

```bash
# Windows Command Prompt
set GEMINI_API_KEY=your_key_here

# Windows PowerShell
$env:GEMINI_API_KEY="your_key_here"

# macOS or Linux
export GEMINI_API_KEY=your_key_here
```

### 3. Run the server

```bash
python app.py
```

Open the application in a browser:

```text
http://127.0.0.1:5002
```

---

## How It Works

1. A user opens the website and accesses the chatbot.
2. The user enters a career- or internship-related question.
3. The Flask backend checks `data/bot_responses.csv` for a matching keyword.
4. When a suitable keyword response is found, the predefined reply is returned.
5. When no suitable keyword is found, the question is sent to **Google Gemini 2.5 Flash** with the available conversation history.
6. The interaction is recorded in `data/conversation_log.csv`.
7. The Create Account and Sign In interfaces are available, while CSV account storage and sign-in validation are being completed in Iteration 2.
8. Dataset-powered internship search, ranking, and filtering will be added in Iteration 3.

The conversation log can include:

- `conversation_no`
- `session_id`
- `username`
- `user_message`
- `matched_keyword`
- `status`
- `process`
- `bot_reply`
- `timestamp`

---

## Chatbot Scope

The chatbot is focused on internship discovery and career preparation. The current scope follows this user journey:

```text
Programme or Major
        ↓
Top Three Strengths
        ↓
Experience Level
        ↓
Recommended Job or Internship
        ↓
Application Guidance
```

Supported topics include:

- Internship and job opportunities
- Resume and cover-letter preparation
- Interview preparation
- Skills and career readiness
- Networking and alumni access
- Professional certifications
- Long-term career progression
- Career mobility within the Asia-Pacific region

Questions outside the project scope should receive a clear response explaining that the chatbot supports internship and career-related topics only.

---

## Customising Keyword Responses

Edit `data/bot_responses.csv` to add or update keyword-based quick replies.

```csv
keyword;category;bot_reply
resume;career preparation;A strong resume should clearly present your skills, education, and relevant experience.
interview;career preparation;Start by researching the organisation and preparing examples using the STAR method.
```

Use a semicolon (`;`) as the delimiter. Keyword responses are checked before the Gemini API is called.

---

## Internship Dataset

The internship dataset is prepared for use by the chatbot.

The cleaned dataset should retain these useful fields:

- Job title
- Company
- Location
- Duration
- Salary
- Work mode
- Application link

The cleaning process covers:

- Removing duplicate records
- Handling missing values
- Removing unnecessary spaces
- Standardising inconsistent text
- Removing unnecessary columns
- Checking that all required columns are available

`data/our_first_internship_sgd.py` contains the dataset-cleaning and exploratory-analysis workflow for Singapore internship data.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, Flask 3.x |
| AI | Google Gemini 2.5 Flash |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Markdown rendering | marked.js |
| Conversation storage | CSV |
| Account storage | CSV-based account system in progress |
| Dataset processing | Python and pandas |
| Version control | Git and GitHub |

---

# Development Iterations

## Iteration 1 — Basic AI Chatbot Prototype

**Period:** 19 May 2026 to 6 June 2026  
**Duration:** Approximately 15 working days  
**Team capacity:** 45 person-days  
**Goal:** Build a working chatbot where users can ask career and internship questions, receive AI-generated responses, and have conversations recorded automatically.

| # | User Story | Priority | Duration | Status |
|---|---|---:|---:|---|
| **1** | Access Chatbot Website | 50 | 1 day | Completed |
| **2** | Send Chat Message | 50 | 1 day | Completed |
| **3** | Receive AI Chatbot Reply | 50 | 2 days | Completed |
| **4** | Integrate Gemini API | 50 | 3 days | Completed |
| **5** | Create Flask Backend | 50 | 2 days | Completed |
| **6** | Create Chatbot Interface | 40 | 2 days | Completed |
| **7** | Apply Website Styling | 30 | 2 days | Completed |
| **8** | Record Conversation Data | 50 | 2 days | Completed |
| **9** | Store Conversation Details | 40 | 1 day | Completed |
| **10** | Create Shared GitHub Repository | 40 | 1 day | Completed |

---

## Iteration 2 — Account System and Dataset Preparation

**Duration:** 10 working days  
**Team capacity:** 30 person-days  
**Goal:** Allow users to create accounts and sign in through CSV-based storage, while preparing the internship dataset for chatbot integration.

| # | User Story | Priority | Duration | Status |
|---|---|---:|---:|---|
| **11** | Clean Internship Dataset | 50 | 3 days | Completed |
| **12** | Select Useful Internship Columns | 50 | 2 days | Completed |
| **13** | Define Chatbot Scope | 40 | 1 day | Completed |
| **14** | Prepare Sample User Questions | 40 | 2 days | Completed |
| **15** | Design Create Account and Sign In Pages | 50 | 3 days | Completed |
| **16** | Save New User Account to CSV | 50 | 2 days | In progress |
| **17** | Validate User Sign In from CSV | 50 | 2 days | In progress |
| **18** | Show Account Not Found Message | 40 | 1 day | In progress |
| **19** | Redirect User After Account Creation | 40 | 1 day | TODO |
| **20** | Test Chatbot on Different Devices | 40 | 2 days | TODO |

### Iteration 2 Testing Focus

Iteration 2 uses test-driven development for the following areas:

- Duplicate, missing-value, and text-format handling in the internship dataset
- Required-column selection and missing-column handling
- In-scope and out-of-scope chatbot questions
- Exact, differently worded, and unclear sample questions
- Account-field validation and password confirmation
- Navigation between the Create Account and Sign In pages
- CSV account creation and sign-in validation
- Account-not-found error handling

### Current Team Responsibilities

| Team Member | Main Responsibility |
|---|---|
| Pinky | Create Account and Sign In frontend pages — completed |
| Airish Yacob Lie | Flask account routes and `users.csv` integration - completed |
| Henry | Dataset preparation, test questions, testing support, and documentation - complted |

---

## Iteration 3 — Internship Search Feature

**Duration:** 10 working days  
**Team capacity:** 30 person-days  
**Goal:** Connect the cleaned internship dataset to the chatbot so it can find, rank, filter, and display relevant internship opportunities.

| # | User Story | Priority | Duration | Status |
|---|---|---:|---:|---|
| **21** | Connect Internship Dataset to Backend | 50 | 4 days | TODO |
| **22** | Search Internship Opportunities | 50 | 3 days | TODO |
| **23** | Display Relevant Internship Results | 50 | 2 days | TODO |
| **24** | Return Top Matching Results | 40 | 2 days | TODO |
| **25** | Filter Internship Results | 40 | 3 days | TODO |
| **26** | Add Reliable Information Notice | 40 | 1 day | TODO |
| **27** | Add Privacy Notice | 40 | 1 day | TODO |
| **28** | Add Password Visibility Icon | 30 | 1 day | Optional |
| **29** | Add Password Strength Indicator | 30 | 2 days | Optional |
| **30** | Explore RAG or a Self-Hosted LLM | 10 | 4 days | Optional |
| **31** | Redirect User After Account Creation | 40 | 1 day | TODO |
| **32** | Test Chatbot on Different Devices | 40 | 2 days | TODO |

### Recommended Iteration 3 Team Split

| Role | Main Responsibility |
|---|---|
| Person 1 | Internship-results display interface |
| Person 2 | Backend search and filtering functions |
| Person 3 | Dataset validation, testing, privacy notice, reliability notice, and documentation |

---

## Current Limitations

- Account creation is not fully connected to CSV storage yet.
- Sign-in validation and account-not-found handling are still in progress.
- The internship dataset is not yet connected to the Flask chatbot backend.
- Internship search, ranking, and filtering are planned for Iteration 3.
- Authentication remains a development-stage CSV solution and is not intended for production use.
- AI-generated career guidance should be reviewed by users before they make important decisions.

---

## Priority Scale

| Priority | Meaning |
|---:|---|
| 50 | Most important |
| 40 | High priority |
| 30 | Medium priority |
| 20 | Low priority |
| 10 | Least important or optional |

---

## Future Improvements

After Iteration 3, possible improvements include:

- Replacing CSV account storage with a database
- Hashing passwords securely
- Adding stronger input validation and error handling
- Improving internship ranking and recommendation quality
- Adding automated tests and continuous integration
- Exploring retrieval-augmented generation
- Evaluating a self-hosted language model
- Improving accessibility and mobile responsiveness

---

## Security Notes

- Never commit the `.env` file or Gemini API key to GitHub.
- Add generated account and conversation data to `.gitignore` when appropriate.
- Do not use plain-text password storage in a production environment.
- Replace the CSV account system with a secure database and password hashing before deployment.
