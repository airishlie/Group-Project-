# InternAI CareerBot

![Group](https://img.shields.io/badge/Group-4-2563EB)
![Subject](https://img.shields.io/badge/Subject-ASE%20CP3407-0F766E)
![Progress](https://img.shields.io/badge/Progress-Week%2010-7C3AED)
![Framework](https://img.shields.io/badge/Framework-Flask-000000?logo=flask&logoColor=white)
![Project](https://img.shields.io/badge/Project-InternAI-1F2937)
![Language](https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active%20Development-F59E0B)
![LLM Models](https://img.shields.io/badge/LLM%20Models-2-8B5CF6)

InternAI CareerBot is a Flask-based internship and career support application developed for **ASE CP3407** by **Group 4**. The system combines a structured response dataset, a guided internship-matching workflow, account management, conversation logging, and two large language model providers.

The application is designed for university students who need career guidance, internship recommendations, resume and interview support, networking advice, and role-specific application assistance.

## Current Project Status

The project is in **Week 10** and remains under active development.

| Component | Status |
|---|---|
| Flask backend | Implemented |
| Chatbot user interface | Implemented |
| Account creation interface | Implemented |
| Sign-in interface | Implemented |
| CSV-based account storage | Implemented for development use |
| Sign-in validation | Implemented |
| Response dataset integration | Implemented |
| Conversation logging | Implemented |
| Internship dataset cleaning | Implemented |
| Internship dataset connection | Implemented |
| Guided job-matching workflow | Implemented |
| Job ranking and top-result display | Implemented |
| Focused application guidance | Implemented |
| Open-question handling during job flow | Implemented |
| OpenRouter integration | Implemented |
| Gemini fallback support | Implemented as an optional secondary provider |
| Live job-market API | Not implemented |
| Production-grade authentication | Not implemented |
| Automated and cross-device testing | In progress |

## Core Workflow

The primary job workflow is:

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

Example conversation:

```text
User: Is there any job for computer science?

Bot: I understood your program or major as Computer Science.
     What are your top three strengths?

User: Python, data analysis, problem-solving

Bot: What is your experience level?

User: Beginner

Bot: Displays the five strongest matching records from the internship dataset.

User: apply 3

Bot: Generates a role-focused application message and CV priorities.
```

Supported workflow commands include:

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

The application stores the exact five job records currently displayed, allowing users to select any visible result reliably.

## Message Routing

InternAI processes each message in the following order:

1. Detect whether the user has asked a separate question during an active job workflow.
2. Answer that separate question without deleting or consuming the saved workflow state.
3. Continue the active workflow when the message is a valid answer for the current stage.
4. Start a new guided workflow when the user asks to find, recommend, search for, or apply for a job or internship.
5. Return a confident response from `bot_responses.csv`.
6. Use OpenRouter for unmatched open-ended career questions.
7. Use Gemini as an optional secondary fallback when OpenRouter is unavailable and Gemini is configured.
8. Return a safe error or related saved response when no AI provider is available.

This routing keeps the structured job workflow separate from general career guidance.

### Open Questions During an Active Workflow

A user can ask an unrelated career question without losing progress.

Example:

```text
Bot: Reply apply 1 to apply 5.

User: How long should an internship normally last?

Bot: Answers the duration question.

Bot: Your job matches are still available. Reply apply 1, apply 2,
     more jobs, restart jobs, or cancel jobs.

User: apply 4
```

The workflow is preserved in the Flask session and resumes at the same stage.

## Main Features

### Career and Internship Chatbot

The chatbot supports:

- Internship and job discovery
- Resume and CV preparation
- Cover-letter guidance
- Behavioral and technical interview preparation
- Salary and stipend questions
- Networking and alumni engagement
- Professional certification planning
- Career progression and mobility
- Skills development
- Application-focused guidance

### Guided Job Matching

The matcher ranks stored internship records using:

- Program or major
- Top three strengths
- Experience level
- Internship title
- Dataset category
- Search terms
- Relevant skill hints
- Record completeness

The displayed results can include:

- Internship or job title
- Company
- Compatibility label
- Match explanation
- Category
- Location
- Work mode
- Start date
- Duration
- Compensation

### Grounded Response Dataset

`bot_responses.csv` contains predefined career responses. The application checks this dataset before calling an LLM.

The matcher supports:

- Whole-word and whole-phrase matching
- Query normalization
- Common aliases
- Token overlap
- Similarity scoring
- Specific-keyword prioritization
- Generic-response suppression when a direct explanation is more appropriate

### LLM Providers

The system supports two LLM providers:

1. **OpenRouter** as the primary provider
2. **Google Gemini** as an optional secondary fallback

Default OpenRouter model:

```text
nvidia/nemotron-3-ultra-550b-a55b:free
```

Default Gemini model:

```text
gemini-2.5-flash
```

The saved response dataset and guided job workflow always take priority over both LLM providers.

### Account System

The development account system supports:

- Account creation
- Duplicate username validation
- Duplicate email validation
- CSV-based user storage
- Sign-in validation
- Account-not-found responses
- Incorrect-password responses
- Session initialization
- Logout

The CSV account system is intended only for development and coursework demonstration.

### Conversation Logging

Interactions can be stored in `data/conversation_log.csv` with fields such as:

- Conversation number
- Session ID
- Username
- User message
- Matched keyword
- Status
- Processing source
- Bot reply
- Timestamp

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
| Dataset processing | Python |
| Environment configuration | python-dotenv |
| HTTP client | requests |
| Version control | Git and GitHub |

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

Some runtime files may be created or updated automatically when the application runs.

## Installation

### Windows

From the project folder:

```bat
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Configuration

Create a private `.env` file in the same folder as `app.py`.

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

Generate a Flask secret on Windows PowerShell:

```powershell
py -c "import secrets; print(secrets.token_hex(32))"
```

The Gemini configuration is optional. When it is not configured, the application continues to use the response dataset, guided workflow, and OpenRouter.

Never commit real API keys to a public repository.

## Running the Application

```bat
python app.py
```

Open:

```text
http://127.0.0.1:5002
```

A successful startup should report the number of loaded response rows and job rows and identify which LLM providers are configured.

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
- Number of loaded response rows
- Number of loaded job rows
- Current routing order

The endpoint does not return API keys.

## Testing the Application

### Response Dataset

```text
What is an internship stipend?
```

Expected result:

```text
Response dataset
```

### Open-Ended Question

```text
How can I explain a failed university project positively during an interview?
```

Expected result:

```text
OpenRouter fallback
```

If OpenRouter fails and Gemini is configured, Gemini may provide the secondary response.

### Guided Job Flow

```text
Is there any job for computer science?
```

Expected behavior:

```text
Detect Computer Science
→ Ask for three strengths
→ Ask for experience level
→ Display matching dataset records
→ Accept apply 1 through apply 5
```

### Workflow Interruption

```text
Bot: Select a job using apply 1 through apply 5.
User: Do employers care about university grades?
```

Expected behavior:

```text
Answer the question
→ Preserve the visible job results
→ Remind the user how to continue
```

## Development Iterations

### Iteration 1: Basic AI Chatbot Prototype

**Period:** May 19, 2026 to June 6, 2026  
**Capacity:** 45 person-days

Main outcomes:

- Flask backend
- Chatbot interface
- AI-generated responses
- Conversation logging
- Shared GitHub repository
- Initial styling and interaction flow

### Iteration 2: Account System and Dataset Preparation

**Capacity:** 30 person-days

Main outcomes:

- Internship dataset cleaning
- Useful-column selection
- Chatbot scope definition
- Sample-question preparation
- Create Account and Sign In interfaces
- CSV-based account storage
- Sign-in validation
- Account-not-found handling

### Iteration 3: Internship Search and Recommendation

**Capacity:** 30 person-days

Current outcomes:

- Internship dataset connected to the Flask backend
- Natural job-search request detection
- Program, strength, and experience collection
- Job ranking and top-result display
- Result selection
- Focused application guidance
- Reliability notice for stored job records
- Privacy and data-handling considerations
- Open questions during active job workflows

Remaining work includes broader testing, production security improvements, and optional live vacancy integration.

## Team Responsibilities

| Team Member | Primary Responsibility |
|---|---|
| Pinky | Create Account and Sign In frontend interfaces |
| Airish Yacob Lie | Flask account routes and `users.csv` integration |
| Henry | Dataset preparation, sample questions, testing support, job-flow development, and documentation |

## Current Limitations

- The internship CSV is a stored dataset and is not a live vacancy feed.
- Job availability must be verified before applying.
- The dataset may not contain complete descriptions or current application URLs.
- The CSV account system is not appropriate for production deployment.
- Password storage must be replaced with secure hashing before production use.
- CSV files are not suitable for concurrent multi-user production traffic.
- Free LLM endpoints may experience rate limits, timeouts, or temporary unavailability.
- AI responses may contain incomplete or inaccurate information.
- Current public-market vacancies require a separate maintained job-provider API.

## Planned Improvements

- Replace CSV account storage with a database
- Hash and salt passwords
- Add stronger server-side validation
- Expand automated testing
- Add continuous integration
- Improve accessibility and responsive behavior
- Add live job-provider integration
- Improve ranking transparency
- Add administrator tools for reviewing response and job datasets
- Explore retrieval-augmented generation
- Evaluate self-hosted LLM options
- Improve privacy controls and data-retention rules

## Priority Scale

| Priority | Meaning |
|---:|---|
| 50 | Most important |
| 40 | High priority |
| 30 | Medium priority |
| 20 | Low priority |
| 10 | Least important or optional |

## Security Notes

- Do not commit `.env` or real API keys.
- Revoke any key that has been exposed in Git history or screenshots.
- Do not use plaintext passwords in a production system.
- Avoid publishing real user records or conversation history in a public repository.
- Use a database, password hashing, access controls, and secure deployment settings before production use.
- Do not use Flask debug mode in a production deployment.

## Disclaimer

InternAI CareerBot is an academic software project developed for ASE CP3407. It is intended for coursework, demonstration, testing, and educational use only. The application does not provide professional career, legal, financial, employment, or immigration advice. Internship and job records may be incomplete, outdated, or no longer available, and users must verify all vacancies, requirements, deadlines, compensation details, and application instructions directly with the relevant employer or official source. AI-generated responses may contain errors or omissions and should not be treated as guaranteed, authoritative, or official information. The development team is not responsible for decisions, applications, losses, privacy incidents, or other outcomes resulting from the use of this software.
