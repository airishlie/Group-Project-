# InternAI: response dataset, job flow, and Gemini fallback

The chatbot now routes each message in this order:

1. **Continue an active job flow** when the user is already answering programme, strengths, experience, job-selection, or application questions.
2. **Start the guided job flow** when the user asks to find, recommend, search for, or apply for a job/internship.
3. **Return a saved response** when `data/bot_responses.csv` contains a confident match.
4. **Call Google Gemini** when the question is open-ended and no saved response matches confidently.

This means Gemini does not replace your dataset. It is the final fallback.

## Guided job flow

`Programme/Major -> Top 3 Strengths -> Experience Level -> Show Jobs -> Apply`

Example:

1. `Find jobs for me`
2. `Computer Science`
3. `Python, data analysis, problem-solving`
4. `Beginner`
5. `apply 1`

Commands during the flow:

- `more jobs`
- `back to jobs`
- `restart jobs`
- `cancel jobs`

## Gemini setup on Windows

### 1. Install dependencies

```bat
cd Group-Project-updated
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create the private `.env` file

Copy `.env.example` and rename the copy to `.env`:

```bat
copy .env.example .env
```

Open `.env` and replace the placeholder key:

```env
SECRET_KEY=replace-with-a-long-random-secret
GEMINI_API_KEY=your-real-google-ai-studio-key
GEMINI_MODEL=gemini-2.5-flash
```

Do not add quotation marks around the key. Do not upload `.env` to GitHub. The included `.gitignore` excludes it.

### 3. Start Flask

```bat
python app.py
```

Open:

```text
http://127.0.0.1:5002
```

The terminal should show:

```text
Gemini fallback enabled: gemini-2.5-flash
```

If it says Gemini is disabled, confirm the file is named exactly `.env`, is in the same folder as `app.py`, and then restart Flask.

## Test the routing

### Saved response test

Ask a question that exists in `bot_responses.csv`, such as:

```text
What is an internship stipend?
```

The process badge should say `Response dataset`.

### Gemini fallback test

Ask an open-ended question that is unlikely to be stored exactly, such as:

```text
How can I explain a failed university project positively during an internship interview?
```

The process badge should say `Gemini fallback (gemini-2.5-flash)`.

### Job-flow test

```text
Find a data internship for me
```

The bot should start with the programme/major question instead of giving a generic Gemini answer.

## Diagnostics

After starting the app, open:

```text
http://127.0.0.1:5002/api/ai_status
```

It safely shows whether Gemini is configured, which model is selected, how many response and job rows loaded, and the routing order. It never returns the API key.

## Dataset limitation

The supplied internship dataset does not include full job descriptions or guaranteed current application URLs. The bot ranks matching records and creates focused application content, but the user must verify that the exact vacancy is still active before applying.

## Natural job-question routing

Questions such as the following now start the guided job flow instead of going to Gemini:

```text
Is there any job for computer science?
Are there jobs for accounting?
What jobs can I get with a data science degree?
Computer science jobs
```

When the first message already contains a recognised major, the bot confirms it and moves directly to the strengths question:

```text
I understood your programme/major as Computer Science.
Step 2 of 3: What are your top three strengths?
```

After the experience answer, the bot displays the best matching records from `Dataset/internship_selected_columns.csv`, including the title, company, match explanation, category, location, work mode, start date, duration, and compensation.

These are dataset records rather than a live vacancy feed. To display currently active jobs from the public market, the project would need a separate jobs-provider API or another maintained live-data source.
