# InternAI: response dataset, job flow, and OpenRouter fallback

InternAI now routes each message in this order:

1. Answer a separate explanation question without consuming an active job-flow answer.
2. Continue an active guided job flow.
3. Start the job flow when the user asks to find or apply for a role.
4. Return a confident answer from `bot_responses.csv`.
5. Call OpenRouter for unmatched open-ended career questions.

The OpenRouter fallback uses this model by default:

```text
nvidia/nemotron-3-ultra-550b-a55b:free
```

The saved-response dataset and guided job matcher remain the first priority. OpenRouter does not replace them.

## Install

From the project folder:

```bat
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env .env
```

## Configure `.env`

Create an OpenRouter API key and place it in `.env`:

```env
SECRET_KEY=your-long-random-flask-secret
OPENROUTER_API_KEY=your-real-openrouter-key
OPENROUTER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
OPENROUTER_SITE_URL=
OPENROUTER_APP_TITLE=InternAI CareerBot
OPENROUTER_TIMEOUT_SECONDS=60
```

`OPENROUTER_SITE_URL` is optional. For deployment, set it to the public URL of your application. Do not commit `.env` or paste the API key into Python, HTML, Discord, or GitHub source files.

If you deploy using GitHub Actions or another hosting provider, create an environment secret named:

```text
OPENROUTER_API_KEY
```

Then expose that secret to the Flask process as an environment variable.

## Run

```bat
python app.py
```

Open:

```text
http://127.0.0.1:5002
```

The terminal should show:

```text
OpenRouter fallback enabled: nvidia/nemotron-3-ultra-550b-a55b:free
```

## Test the routing

### Guided job flow

Send:

```text
Is there any job for computer science?
```

The bot should detect Computer Science and ask for the user's top three strengths, followed by experience level. It then ranks roles from `Dataset/internship_selected_columns.csv`.

### Saved response

Send a question confidently covered by `bot_responses.csv`, such as:

```text
What is an internship stipend?
```

The process badge should identify the response dataset.

### OpenRouter fallback

Send an unmatched open-ended question, such as:

```text
How can I explain a failed university project positively during an interview?
```

The process badge should show:

```text
OpenRouter fallback (nvidia/nemotron-3-ultra-550b-a55b:free)
```

## Diagnostics

Visit:

```text
http://127.0.0.1:5002/api/ai_status
```

The endpoint reports whether OpenRouter is configured, the selected model, loaded response rows, loaded job rows, and the routing order. It never returns the API key.

## Common errors

- **OpenRouter not configured:** add `OPENROUTER_API_KEY` to `.env` and restart Flask.
- **401 or 403:** the API key is missing, invalid, disabled, or lacks access.
- **404 / model unavailable:** verify that `OPENROUTER_MODEL` exactly matches the model slug.
- **429:** the free endpoint has reached a rate limit; wait and retry.
- **Timeout or 5xx:** the free provider may be busy; retry later.

## Privacy note

The selected free NVIDIA endpoint warns users not to submit confidential information or personal data. Keep prompts focused on non-sensitive career guidance, and do not send passwords, identity documents, private employer data, or other confidential material.

## Job-market limitation

The included internship CSV is a stored dataset, not a live vacancy feed. Users should verify that a listing is still active before applying. Displaying current public-market vacancies requires a separate maintained jobs-provider API.

## Explanation questions versus job-search questions

The router now separates informational questions from vacancy searches.

- `What is an internship?` and `Can you explain an internship for a university student?` are answered normally through OpenRouter.
- `Find internships for computer science students` starts the guided matching flow.
- `What are available jobs for computer science?` also starts the guided matching flow rather than being mistaken for a definition request.
- If an informational question is asked while the guided flow is active, the bot answers it instead of treating the question as a programme, strength, or experience value. The job flow remains available until the user continues or types `cancel jobs`.

## Archive note

The distributable archive intentionally excludes `.venv`, `.idea`, `.env`, and Python cache files. Recreate the virtual environment locally and keep the real API key only in `.env`.
