<div align="center">

<sub>ASE CP3407 &nbsp;·&nbsp; TR2 2026 &nbsp;·&nbsp; Singapore &nbsp;·&nbsp; Group 4</sub>

# InternAI CareerBot

<sub>Dataset-grounded career guidance, guided job matching, dual-LLM fallback, and focused application support.</sub>

<br>

![Group](https://img.shields.io/badge/Group-4-2563eb?style=flat-square&labelColor=161b22)
![Subject](https://img.shields.io/badge/Subject-ASE_CP3407-0f766e?style=flat-square&labelColor=161b22)
![Progress](https://img.shields.io/badge/Progress-Week_10-58a6ff?style=flat-square&labelColor=161b22&logo=issuu)
![Status](https://img.shields.io/badge/Status-Active_Development-3fb950?style=flat-square&labelColor=161b22&logo=statuspage)
![Project](https://img.shields.io/badge/Project-InternAI-d29922?style=flat-square&labelColor=161b22)
![Backend](https://img.shields.io/badge/Backend-Python_%7C_Flask-3776ab?style=flat-square&labelColor=161b22&logo=flask)
![Language](https://img.shields.io/badge/Language-Python-3776ab?style=flat-square&labelColor=161b22&logo=python&logoColor=white)
![LLMs](https://img.shields.io/badge/LLM_Models-2-bc8cff?style=flat-square&labelColor=161b22&logo=openrouter)

</div>

---

## What This Project Does

InternAI CareerBot is an internship and career support application developed by Group 4 for ASE CP3407.

The system combines a structured response dataset, a guided job-matching workflow, account management, conversation logging, and two large language model providers. It is designed to help university students explore internships, identify compatible opportunities, prepare applications, and ask open-ended career questions.

The current application can:

- Answer known career questions from `bot_responses.csv`
- Detect natural job-search requests
- Collect a user's program or major, top three strengths, and experience level
- Rank internship records from the project dataset
- Display compatible roles and supporting match reasons
- Generate role-focused application guidance
- Answer separate questions without losing the active job workflow
- Use OpenRouter as the primary LLM provider
- Use Google Gemini as an optional secondary fallback
- Save account and conversation information in CSV files for development use

> **Week 10 Status:** The Flask application, account pages, CSV account workflow, response dataset, internship matching, job-selection workflow, application guidance, OpenRouter integration, optional Gemini fallback, and workflow restoration are available. Broader testing, production security, and live vacancy integration remain in progress.

---

## Quick Start

### Requirements

- Python 3.11 or later
- `pip`
- An OpenRouter API key for the primary AI fallback
- An optional Gemini API key for secondary fallback behavior

### Setup

```bash
cd AI

py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS or Linux:

```bash
cd AI

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment Configuration

Create a private `.env` file in the same directory as `app.py`.

```env
SECRET_KEY=your-long-random-flask-secret

OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
OPENROUTER_SITE_URL=
OPENROUTER_APP_TITLE=InternAI CareerBot
OPENROUTER_TIMEOUT_SECONDS=60

GEMINI_API_KEY=your-optional-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash
```

Generate a Flask secret in PowerShell:

```powershell
py -c "import secrets; print(secrets.token_hex(32))"
```

Never commit real API keys to GitHub.

### Run the Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5002
```

A successful startup reports the number of loaded response rows, loaded job rows, and configured LLM providers.

---

## Core Workflow

The guided workflow is:

```text
Program or Major
        ↓
Top Three Strengths
        ↓
Experience Level
        ↓
Compatible Job or Internship Results
        ↓
Focused Application Guidance
```

Example:

```text
User: Is there any job for computer science?

Bot: I understood your program or major as Computer Science.
     What are your top three strengths?

User: Python, data analysis, problem-solving

Bot: What is your experience level?

User: Beginner

Bot: Displays the strongest matching internship records.

User: apply 3

Bot: Generates a focused application message and CV priorities.
```

Supported workflow commands:

```text
apply 1
apply 2
apply 3
apply 4
apply 5
more jobs
back to jobs
restart jobs
cancel jobs
```

The application stores the exact job IDs currently displayed, allowing users to select results 1 through 5 reliably.

---

## Message Routing

Each user message is processed in this order:

1. Detect a separate question during an active job workflow.
2. Answer the separate question without deleting the saved workflow state.
3. Continue the active workflow when the message is a valid answer for the current stage.
4. Start a new workflow when the user asks to find, recommend, search for, or apply for a role.
5. Return a confident response from `bot_responses.csv`.
6. Use OpenRouter for unmatched open-ended career questions.
7. Use Gemini as an optional secondary fallback when OpenRouter is unavailable.
8. Return a safe error or related saved response when no AI provider can respond.

### Workflow Restoration

A separate question does not cancel the job workflow.

```text
Bot: Reply apply 1 through apply 5.

User: How long should an internship normally last?

Bot: Answers the question.

Bot: Your job matches are still available.
     Reply apply 1, apply 2, more jobs, restart jobs, or cancel jobs.

User: apply 4
```

The workflow remains stored in the Flask session and resumes at the same stage.

---

## Main Capabilities

| Capability | Current Implementation |
|---|---|
| Career and internship chat | Response dataset with LLM fallback |
| Natural job-search detection | Pattern and major detection |
| Guided profile collection | Program, strengths, and experience |
| Internship matching | Weighted ranking against the CSV dataset |
| Result selection | Visible results 1 through 5 |
| Application support | Focused message and CV guidance |
| Open questions during workflow | Answered without losing progress |
| Account creation | CSV-based development workflow |
| Sign-in validation | CSV lookup and password comparison |
| Conversation logging | CSV-based logging |
| Primary LLM | OpenRouter |
| Secondary LLM | Google Gemini |
| Live job-market feed | Not implemented |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Primary LLM | OpenRouter |
| Secondary LLM | Google Gemini |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Markdown rendering | marked.js |
| Response storage | CSV |
| Account storage | CSV |
| Conversation logging | CSV |
| Internship dataset | CSV |
| Environment configuration | python-dotenv |
| HTTP requests | requests |
| Version control | Git and GitHub |

---

## Project Structure

```text
AI/
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── bot_responses.csv
├── JOB_FLOW_README.md
├── LATEST_UPDATE.md
│
├── templates/
│   ├── login.html
│   ├── signup.html
│   └── chat.html
│
├── static/
│   ├── css/
│   └── js/
│
├── data/
│   ├── bot_responses.csv
│   ├── users.csv
│   └── conversation_log.csv
│
├── Dataset/
│   └── internship_selected_columns.csv
│
├── iteration-1/
└── iteration-2/
```

Some CSV files are created or updated while the application is running.

---

## Internship Matching

The ranking system considers:

- Program or major
- Top three strengths
- Experience level
- Internship title
- Dataset category
- Search terms
- Skill-related hints
- Record completeness

Displayed results can include:

- Job or internship title
- Company
- Compatibility label
- Match explanation
- Category
- Location
- Work mode
- Start date
- Duration
- Compensation

The supplied internship dataset is a stored project dataset, not a live vacancy feed.

---

## Response Dataset

`bot_responses.csv` provides grounded answers before an LLM is called.

The matcher supports:

- Whole-word and whole-phrase matching
- Query normalization
- Common aliases
- Token overlap
- Similarity scoring
- Specific-keyword prioritization
- Generic-response suppression when a direct explanation is more appropriate

Example CSV structure:

```csv
keyword;category;bot_reply
resume;career preparation;A strong resume should clearly present your skills, education, and relevant experience.
interview;career preparation;Research the organization and prepare examples using the STAR method.
```

---

## LLM Configuration

### OpenRouter

OpenRouter is the primary provider for unmatched open-ended questions.

Default model:

```text
nvidia/nemotron-3-ultra-550b-a55b:free
```

### Google Gemini

Gemini is an optional secondary fallback.

Default model:

```text
gemini-2.5-flash
```

The structured response dataset and guided job workflow always take priority over both LLM providers.

---

## Diagnostics

Open:

```text
http://127.0.0.1:5002/api/ai_status
```

The endpoint reports:

- Whether OpenRouter is configured
- The selected OpenRouter model
- Whether Gemini is configured
- The selected Gemini model
- Number of response rows loaded
- Number of job rows loaded
- Current routing order

The endpoint does not expose API keys.

---

## Testing

### Saved Response

```text
What is an internship stipend?
```

Expected process:

```text
Response dataset
```

### Open-Ended Question

```text
How can I explain a failed university project positively during an interview?
```

Expected process:

```text
OpenRouter fallback
```

If OpenRouter fails and Gemini is configured, Gemini may provide the response.

### Guided Job Flow

```text
Is there any job for computer science?
```

Expected sequence:

```text
Detect Computer Science
→ Ask for three strengths
→ Ask for experience level
→ Display matching records
→ Accept apply 1 through apply 5
```

### Workflow Interruption

```text
Bot: Select a result using apply 1 through apply 5.
User: Do employers care about university grades?
```

Expected behavior:

```text
Answer the question
→ Preserve the displayed results
→ Remind the user how to continue
```

---

## Development Progress

| Iteration | Main Goal | Current Outcome |
|---|---|---|
| Iteration 1 | Basic AI chatbot prototype | Completed |
| Iteration 2 | Account system and dataset preparation | Core work completed |
| Iteration 3 | Internship search and recommendation | Core workflow implemented; testing continues |

### Iteration 1

Main outcomes:

- Flask backend
- Chatbot interface
- AI-generated responses
- Conversation logging
- Shared GitHub repository
- Initial styling and interaction flow

### Iteration 2

Main outcomes:

- Internship dataset cleaning
- Useful-column selection
- Chatbot scope definition
- Sample-question preparation
- Create Account and Sign In interfaces
- CSV-based account storage
- Sign-in validation
- Account-not-found handling

### Iteration 3

Current outcomes:

- Internship dataset connected to Flask
- Natural job-search detection
- Program, strength, and experience collection
- Job ranking and result display
- Result selection
- Focused application guidance
- Reliability notice for stored records
- Open questions during active workflows

Remaining work includes broader testing, production security, and optional live vacancy integration.

---

## Documentation

| Document | Purpose |
|---|---|
| [JOB_FLOW_README.md](JOB_FLOW_README.md) | Detailed routing, workflow, job selection, and interruption behavior |
| [LATEST_UPDATE.md](LATEST_UPDATE.md) | Summary of recent implementation changes |
| [iteration-1](iteration-1/) | Iteration 1 planning and working documentation |
| [iteration-2](iteration-2/) | Iteration 2 planning and working documentation |

---

## Team Responsibilities

| Team Member | Primary Responsibility |
|---|---|
| Pinky | Create Account and Sign In frontend interfaces |
| Airish Yacob Lie | Flask account routes and `users.csv` integration |
| Henry | Dataset preparation, sample questions, testing support, job-flow development, and documentation |

---

## Current Limitations

- The internship CSV is not a live vacancy feed.
- Users must verify whether a listing is still active.
- Some records may not contain complete descriptions or application URLs.
- The CSV account system is not suitable for production use.
- Password storage must be replaced with secure hashing before deployment.
- CSV files are not appropriate for concurrent production traffic.
- Free LLM endpoints may experience rate limits, timeouts, or temporary outages.
- AI-generated answers may contain incomplete or inaccurate information.
- Current public vacancies require a separate maintained job-provider API.

---

## Contributing

Development work should be completed on the assigned branch.

Before pushing:

```bash
git status
git add <changed-files>
git commit -m "Describe the change"
git push origin <branch-name>
```

Do not commit `.env`, active API keys, private account records, or confidential conversation data to a public repository.

---

## Security Notes

- Never commit real API keys.
- Revoke any key exposed in Git history or screenshots.
- Do not use plaintext passwords in production.
- Replace CSV account storage with a database and password hashing before deployment.
- Do not use Flask debug mode in production.
- Apply access controls and data-retention rules before handling real user information.

---

## Educational Disclaimer

This repository is an educational project developed for ASE CP3407. InternAI CareerBot is intended for coursework, demonstration, testing, and educational use only. It does not provide professional career, legal, financial, employment, or immigration advice. Internship and job records may be incomplete, outdated, or no longer available, and users must verify all vacancies, requirements, deadlines, compensation details, and application instructions directly with the relevant employer or official source. AI-generated responses may contain errors or omissions and should not be treated as guaranteed, authoritative, or official information. The development team is not responsible for decisions, applications, losses, privacy incidents, or other outcomes resulting from the use of this software.
