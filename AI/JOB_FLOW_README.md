# InternAI Job Flow

## Current baseline

InternAI combines three separate response systems:

1. A guided job-matching workflow backed by the internship dataset.
2. Grounded saved answers from `bot_responses.csv`.
3. OpenRouter as the fallback for unmatched, open-ended questions.

The default OpenRouter model is:

```text
nvidia/nemotron-3-ultra-550b-a55b:free
```

OpenRouter does not replace the response dataset or the job matcher. It is used only when no confident saved response is available, or when a separate open question interrupts the guided workflow.

---

## Message-routing order

The current `/api/chat` route handles each message in this order:

1. If a job flow is active, determine whether the message is a valid answer or command for the current stage.
2. If it is not a valid flow input, answer it separately through `bot_responses.csv` or OpenRouter while preserving the job flow.
3. If it is a valid flow input, continue the existing job flow.
4. If no flow is active and the message requests jobs, internships, vacancies, recommendations, matching, or application help, start a new job flow.
5. Otherwise, return a confident saved response from `bot_responses.csv`.
6. If no saved response matches confidently, call OpenRouter.

In simplified form:

```text
Active flow + unrelated/open message
→ Answer separately
→ Preserve exact flow stage
→ Remind user how to continue

Active flow + valid stage input
→ Continue flow

No active flow + job-search request
→ Start job flow

No active flow + normal question
→ Response dataset
→ OpenRouter fallback
```

---

## Guided job workflow

```text
Programme/Major
→ Top 3 Strengths
→ Experience Level
→ Show Compatible Jobs
→ Select Job
→ Generate Focused Application
```

### Example

```text
User: Is there any job for computer science?
Bot: I understood your programme/major as Computer Science.
     What are your top three strengths?

User: Python, data analysis, problem-solving
Bot: What is your experience level?

User: Beginner
Bot: Displays five compatible dataset records.

User: apply 4
Bot: Generates a focused application for the fourth visible job.
```

If the first search message already contains a recognised major, the bot skips the programme question and moves directly to strengths.

---

## Flow stages and accepted inputs

### 1. Programme or major

The bot accepts a concise field of study, for example:

```text
Computer Science
Information Technology
Accounting
Marketing
Hospitality
Psychology
```

Question-like sentences are not consumed as a programme answer.

### 2. Top three strengths

The user should provide at least three strengths separated by commas, semicolons, slashes, line breaks, `and`, or `plus`.

Examples:

```text
Python, data analysis, problem-solving
Communication and teamwork and organisation
Research / writing / attention to detail
```

Only the first three detected strengths are stored.

### 3. Experience level

Accepted examples include:

```text
No experience
Beginner
Entry level
Intermediate
Advanced
I have 6 months of experience
2 years of experience
```

A question containing a duration should not be consumed as the user's experience answer.

Example interruption:

```text
Is two years of experience enough for this role?
```

The bot should answer that question separately and then restore the experience stage.

### 4. Job results

The bot shows up to five jobs at a time and stores the exact IDs of those five visible records in the session.

This prevents a selection from being resolved against an outdated result page.

---

## Reliable job selection

The following formats are supported for visible jobs 1–5:

```text
1
2
3
4
5
apply 3
apply for job 4
choose option 5
select the second job
pick the fifth one
the third one
```

The parser uses full-message matching. Numbers inside unrelated sentences are not treated as job selections.

For example, this does not select job 3:

```text
I have 3 years of experience
```

Selections are resolved against `visible_job_ids`, which contains the exact five records currently shown to the user.

---

## Commands during the flow

```text
more jobs
next jobs
back to jobs
show jobs
show matches
restart jobs
start over
cancel jobs
stop
exit
```

### Behaviour

- `more jobs` displays the next five ranked records.
- When the final page is passed, pagination returns to the first page.
- `back to jobs` redisplays the current visible page after an application is generated.
- `restart jobs` clears the current profile and starts again from programme/major.
- `cancel jobs` removes the job-flow session while leaving normal chatbot questions available.

---

## Open questions during an active flow

The flow uses a consume-only-recognised-input approach.

Only inputs that clearly belong to the current stage are consumed. Every other message is treated as a separate open question.

This means the bot does not require every possible open question to be listed as a hard-coded intent.

### Example at the job-selection stage

```text
Bot: Reply apply 1 to apply 5.

User: Do employers care about university grades?

Bot: Answers the question through the response dataset or OpenRouter.

Bot: Your job matches are still available. Reply apply 1, apply 2,
     etc., or use more jobs, restart jobs, or cancel jobs.

User: apply 4

Bot: Continues from the same five visible jobs.
```

### Flow preservation

When a separate question is answered:

- `session["job_flow"]` is not deleted.
- The current stage remains unchanged.
- Existing programme, strengths, experience, ranked job IDs, pagination offset, and visible job IDs remain available.
- The bot appends a stage-specific resume reminder.

### Reducing AI drift

Interruption questions are sent to OpenRouter without the active questionnaire conversation history.

The request includes an explicit instruction to:

- answer only the current message;
- not continue the job questionnaire;
- not select a job;
- not restart or modify the workflow.

Flask, rather than the language model, controls job-flow state.

---

## Starting a job search

Natural search requests start the guided matcher, for example:

```text
Find jobs for me
Show internships for computer science students
Is there any job for accounting?
What jobs can I get with a data science degree?
Recommend a suitable role for me
Help me apply for an internship
Computer science jobs
```

Informational requests should not start the matcher:

```text
What is an internship?
Explain what a software engineer does.
What is a job description?
How should I prepare for an interview?
```

---

## Saved-response matching

The bot loads saved answers from:

```text
data/bot_responses.csv
```

If that file is unavailable, it falls back to:

```text
bot_responses.csv
```

Matching includes:

- text normalisation;
- query aliases;
- whole-word and whole-phrase matching;
- token overlap;
- sequence similarity;
- confidence ranking;
- preference for specific keywords over broad keywords.

Examples of aliases include:

```text
allowance → stipend
salary → stipend
how long → duration
CV → resume
WFH → remote internship
rejected → internship rejection
```

The broad keyword `internship` is intentionally prevented from overriding a complete open-ended question. Questions such as `What is an internship?` are answered naturally rather than returning a generic internship-search tip.

---

## OpenRouter fallback

OpenRouter handles messages that do not confidently match the saved-response dataset.

The request includes:

- the configured system prompt;
- up to ten recent turns for normal conversations;
- related saved-response examples when useful;
- the current user message.

For interruptions during a job flow, recent workflow history is intentionally excluded to reduce drift.

### Supported error handling

- Missing API key
- HTTP 401 or 403 authentication failure
- HTTP 402 credit or access issue
- HTTP 404 or unavailable model
- HTTP 429 rate limit
- HTTP 500, 502, 503, or 504 provider failure
- Network failure
- Timeout
- Invalid JSON response
- Empty model response

When related saved-response examples are available and OpenRouter fails, the bot may return the closest grounded dataset response instead.

---

## Job recommendation logic

Jobs are loaded from:

```text
Dataset/internship_selected_columns.csv
```

The recommendation score considers:

- programme/major tokens in the title;
- programme/major tokens in the category;
- programme/major tokens in the searchable record text;
- strength tokens in the title and record text;
- mapped job categories for the major;
- strength-to-role hints;
- experience level;
- listing completeness;
- paid-listing status as a small tie-breaker.

Duplicate records with the same title, company, and location are removed from the result set.

The bot ranks up to 15 records and displays five at a time.

### Compatibility labels

```text
Strong match
Good match
Potential match
```

The displayed explanation can include:

- major-to-category alignment;
- matched strengths;
- closest available title or category match.

---

## Displayed job information

Each result can include:

- internship title;
- company;
- compatibility label;
- reason for the match;
- category;
- location;
- work mode;
- start date;
- duration;
- compensation.

The displayed records come from the uploaded CSV dataset. They are not guaranteed to be active vacancies.

---

## Focused application output

After selecting a visible job, the bot generates:

- the selected title and company;
- why it matches the user's profile;
- programme/major and strengths to emphasise;
- a focused application message;
- CV focus points based on the job category;
- instructions for locating and verifying the exact vacancy.

The dataset does not currently provide a guaranteed application URL, so the bot instructs the user to search for the exact title and company and verify that the listing is still active.

---

## Installation

### Windows

```bat
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Dependencies currently required:

```text
Flask
python-dotenv
requests>=2.31,<3
```

---

## Environment configuration

Create `.env` beside `app.py`:

```env
SECRET_KEY=your-long-random-flask-secret
OPENROUTER_API_KEY=your-real-openrouter-key
OPENROUTER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
OPENROUTER_SITE_URL=
OPENROUTER_APP_TITLE=InternAI CareerBot
OPENROUTER_TIMEOUT_SECONDS=60
```

`OPENROUTER_SITE_URL` is optional during local development.

Never commit the real `.env` file or expose the API key in Python, HTML, screenshots, chat messages, Discord, or GitHub.

---

## Running the application

```bat
python app.py
```

Open:

```text
http://127.0.0.1:5002
```

Expected terminal output includes:

```text
Loaded response rows: 53
Loaded job rows: 6449
OpenRouter fallback enabled: nvidia/nemotron-3-ultra-550b-a55b:free
```

The exact row counts may change if either CSV is updated.

---

## Diagnostics

Open:

```text
http://127.0.0.1:5002/api/ai_status
```

The endpoint safely reports:

- whether OpenRouter is configured;
- the selected OpenRouter model;
- loaded response-row count;
- loaded job-row count;
- current routing order.

It never returns the API key.

---

## Test checklist

### Start a flow with a detected major

```text
Is there any job for computer science?
```

Expected: Computer Science is detected and the bot asks for strengths.

### Start a flow without a detected major

```text
Find jobs for me
```

Expected: the bot asks for programme or major.

### Saved response

```text
What is an internship stipend?
```

Expected process badge:

```text
Response dataset
```

### OpenRouter fallback

```text
How can I explain a failed university project positively during an interview?
```

Expected process badge:

```text
OpenRouter fallback (nvidia/nemotron-3-ultra-550b-a55b:free)
```

### Open question during strengths

```text
Are Python, Java, and C++ useful for software internships?
```

Expected: answer the question, preserve the strengths stage, and ask the user to provide three strengths afterward.

### Open question during experience

```text
Is two years of experience enough for this role?
```

Expected: answer the question and preserve the experience stage.

### Direct experience answer

```text
I have 2 years of experience
```

Expected: consume it as the experience answer and show jobs.

### Select every visible result

```text
apply 1
apply 2
apply 3
apply 4
apply 5
```

Expected: each command selects the corresponding currently visible record.

### Number safety

```text
I have 3 years of experience
```

Expected: it must not select job 3 while the jobs stage is active; it should be treated as a separate message unless it is being entered at the experience stage.

### Restore after interruption

```text
How long should an internship last?
apply 4
```

Expected: the first message is answered independently, and `apply 4` still selects the fourth previously displayed result.

---

## Known limitations

1. The internship CSV is a stored dataset, not a live vacancy feed.
2. Application URLs are not guaranteed to be present.
3. Job ranking is heuristic rather than a trained recommendation model.
4. The free OpenRouter endpoint may be rate-limited or temporarily unavailable.
5. Natural-language flow classification is deliberately conservative. Ambiguous inputs may be answered as open questions rather than consumed by the flow.
6. Only five results are displayed at once.
7. The current application pack is generated from title, category, company, profile, and available dataset fields rather than a full job description.
8. Truly current public-market vacancies require a maintained jobs-provider API or another live-data source.

---

## Security and privacy

- Keep `.env` outside Git tracking.
- Revoke any API key exposed in a screenshot, commit, or push attempt.
- Do not submit passwords, identity documents, private employer data, or confidential personal information to a free external model endpoint.
- Use a long random Flask `SECRET_KEY`.
- Conversation logs are written locally to `data/conversation_log.csv`.
- User records are stored locally in `data/users.csv` when account saving is enabled.

---

## Current project files used by the flow

```text
app.py
bot_responses.csv
data/bot_responses.csv
Dataset/internship_selected_columns.csv
.env
requirements.txt
templates/chat.html
static/css/style.css
data/conversation_log.csv
data/users.csv
```

Runtime-created or private files should normally remain untracked:

```text
.env
.venv/
__pycache__/
data/conversation_log.csv
data/users.csv
```

---

## Baseline for the next update

This document describes the current implementation with:

- OpenRouter/Nemotron fallback;
- saved-response grounding;
- programme → strengths → experience → jobs → application flow;
- reliable selection of visible jobs 1–5;
- universal handling of non-flow messages during an active workflow;
- isolated interruption answers to reduce AI drift;
- preserved session state and stage-specific resume reminders.

Future fixes should be compared against this baseline before updating the code and documentation.
