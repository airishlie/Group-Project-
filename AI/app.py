# ============================================================
#  InternAI — Flask Backend
#  - Uses bot_responses.csv for grounded career answers
#  - Uses the internship dataset for guided job matching
#  - Uses OpenRouter (NVIDIA Nemotron) as an optional fallback
#  - Logs conversations to data/conversation_log.csv
# ============================================================

from __future__ import annotations

from flask import Flask, render_template, request, jsonify, session
import requests
from dotenv import load_dotenv
import csv
from datetime import datetime
from difflib import SequenceMatcher
import os
import re
import uuid

# ── File paths and environment ─────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "internai-secret-2026")

DATA_DIR = os.path.join(BASE_DIR, "data")
DATASET_DIR = os.path.join(BASE_DIR, "Dataset")

os.makedirs(DATA_DIR, exist_ok=True)

BOT_DATA_FILE = os.path.join(DATA_DIR, "bot_responses.csv")
BOT_DATA_FALLBACK = os.path.join(BASE_DIR, "bot_responses.csv")
JOB_DATA_FILE = os.path.join(DATASET_DIR, "internship_selected_columns.csv")
LOG_FILE = os.path.join(DATA_DIR, "conversation_log.csv")
USER_FILE = os.path.join(DATA_DIR, "users.csv")

# ── OpenRouter client configuration ──────────────────────────
# Put secrets in .env or operating-system environment variables.
# Never commit a real API key to GitHub.
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.environ.get(
    "OPENROUTER_MODEL",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
).strip()
OPENROUTER_API_URL = os.environ.get(
    "OPENROUTER_API_URL",
    "https://openrouter.ai/api/v1/chat/completions",
).strip()
OPENROUTER_SITE_URL = os.environ.get("OPENROUTER_SITE_URL", "").strip()
OPENROUTER_APP_TITLE = os.environ.get(
    "OPENROUTER_APP_TITLE",
    "InternAI CareerBot",
).strip()

try:
    OPENROUTER_TIMEOUT_SECONDS = max(10, min(120, int(
        os.environ.get("OPENROUTER_TIMEOUT_SECONDS", "60")
    )))
except ValueError:
    OPENROUTER_TIMEOUT_SECONDS = 60

SYSTEM_PROMPT = """You are CareerBot, a friendly and knowledgeable career and internship
support assistant for university students in Singapore and beyond.

Your expertise covers internships, resumes, cover letters, interviews, salary and
stipend expectations, networking, career planning, and skill development.

Important rules:
- Be concise, warm, and actionable.
- Use markdown formatting when helpful.
- Answer unmatched open-ended career questions naturally and directly.
- Ground answers in the supplied response examples when examples are provided.
- Do not invent official deadlines, application links, job requirements, vacancies, or dataset records.
- When information is uncertain or current availability must be checked, say so clearly.
- Keep answers focused and under 300 words unless more detail is requested.
"""

# ── Text helpers ─────────────────────────────────────────────
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "can", "do", "for", "from",
    "how", "i", "in", "is", "it", "me", "my", "of", "on", "or", "please",
    "the", "to", "what", "when", "where", "which", "with", "you", "your"
}

# Broad keywords should not outrank a more specific keyword in the same question.
GENERIC_RESPONSE_KEYWORDS = {"internship"}

QUERY_ALIASES = {
    "internships": "internship",
    "allowance": "stipend",
    "allowances": "stipend",
    "salary": "stipend",
    "pay": "stipend",
    "paid": "stipend",
    "compensation": "stipend",
    "how long": "duration",
    "last": "duration",
    "length": "duration",
    "cv": "resume",
    "curriculum vitae": "resume",
    "work from home": "remote internship",
    "wfh": "remote internship",
    "partly remote": "hybrid internship",
    "connections": "networking",
    "connection": "networking",
    "reject": "internship rejection",
    "rejected": "internship rejection",
    "accepted": "internship acceptance",
}


def normalise_text(text: str) -> str:
    value = (text or "").lower().strip()
    for source, target in QUERY_ALIASES.items():
        value = re.sub(rf"\b{re.escape(source)}\b", target, value)
    value = re.sub(r"[^a-z0-9+#./ -]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def tokenise(text: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-z0-9+#.]+", normalise_text(text))
        if len(token) > 1 and token not in STOP_WORDS
    }


def phrase_in_text(phrase: str, text: str) -> bool:
    """Whole-word/whole-phrase match, so 'hi' does not match 'this'."""
    phrase = normalise_text(phrase)
    text = normalise_text(text)
    if not phrase:
        return False
    return re.search(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", text) is not None


def is_explanation_request(message: str) -> bool:
    """Detect definition/explanation questions that should receive a direct answer.

    These questions must not accidentally start the guided job-search flow just
    because they contain words such as "internship" or "job". Conversely, a
    vacancy question such as "What are available jobs for computer science?"
    must still enter the guided matcher.
    """
    text = normalise_text(message)

    # Search/availability wording takes priority over the broad "what are" form.
    vacancy_patterns = [
        r"\b(?:find|show|search|recommend|suggest|match)\b.{0,40}\b(?:jobs?|internships?|roles?|vacanc(?:y|ies)|openings?|opportunities)\b",
        r"^what (?:jobs?|internships?|roles?|vacanc(?:y|ies)|openings?|opportunities)\b",
        r"^what are (?:some|any|the|available|open|current|best|top|suitable|matching)?\s*(?:jobs?|internships?|roles?|vacanc(?:y|ies)|openings?|opportunities)\b",
        r"\b(?:any|some|available|open|current|best|top|suitable|matching)\s+(?:jobs?|internships?|roles?|vacanc(?:y|ies)|openings?|opportunities)\b",
        r"\b(?:is|are) there\s+(?:any|some|available|open)?\s*(?:jobs?|internships?|roles?|vacanc(?:y|ies)|openings?|opportunities)\b",
    ]
    if any(re.search(pattern, text) for pattern in vacancy_patterns):
        return False

    explanation_patterns = [
        r"^what (?:is|are|does)\b",
        r"^what do you mean\b",
        r"^define\b",
        r"^explain\b",
        r"^tell me (?:about|what)\b",
        r"^(?:can|could|would) (?:you|u) explain\b",
        r"^(?:can|could|would) (?:you|u) tell me\b",
        r"^how (?:does|do|is|are|can)\b",
        r"^why (?:does|do|is|are|can)\b",
        r"\bwhat does .{0,50} mean\b",
        r"\bmeaning of\b",
        r"\bdifference between\b",
    ]
    return any(re.search(pattern, text) for pattern in explanation_patterns)


# ── Load grounded bot responses ──────────────────────────────
def load_bot_responses() -> list[dict]:
    """Load keyword/category/reply mappings from CSV."""
    responses: list[dict] = []
    source = BOT_DATA_FILE if os.path.exists(BOT_DATA_FILE) else BOT_DATA_FALLBACK
    if not os.path.exists(source):
        print("[WARN] bot_responses.csv was not found.")
        return responses

    try:
        with open(source, "r", newline="", encoding="utf-8-sig") as file:
            first_line = file.readline()
            delimiter = ";" if ";" in first_line else ","
            file.seek(0)
            reader = csv.DictReader(file, delimiter=delimiter)
            for row in reader:
                clean = {key.strip(): (value.strip() if value else "") for key, value in row.items() if key}
                if clean.get("keyword") and clean.get("bot_reply"):
                    clean["_keyword_normalised"] = normalise_text(clean["keyword"])
                    clean["_tokens"] = tokenise(clean["keyword"] + " " + clean.get("category", ""))
                    responses.append(clean)
    except (OSError, csv.Error) as exc:
        print(f"[WARN] Could not load bot_responses.csv: {exc}")
    return responses


BOT_RESPONSES = load_bot_responses()


def find_response_matches(user_message: str, limit: int = 3) -> list[tuple[float, dict]]:
    """Return exact and semantically related response rows first."""
    normalised = normalise_text(user_message)
    query_tokens = tokenise(normalised)
    ranked: list[tuple[float, dict]] = []

    for row in BOT_RESPONSES:
        keyword = row.get("_keyword_normalised", "")
        row_tokens = row.get("_tokens", set())

        if phrase_in_text(keyword, normalised):
            # Longer phrases are more specific than short words. Broad terms such
            # as "internship" are reduced when the question contains a more
            # specific topic such as stipend, rejection, or networking.
            score = 1.0 + min(len(keyword) / 100, 0.15)
            if keyword in GENERIC_RESPONSE_KEYWORDS and len(query_tokens) > 1:
                score -= 0.35
        else:
            overlap = len(query_tokens & row_tokens)
            union = len(query_tokens | row_tokens) or 1
            jaccard = overlap / union
            sequence = SequenceMatcher(None, normalised, keyword).ratio()
            score = (jaccard * 0.75) + (sequence * 0.25)

        if score >= 0.20:
            ranked.append((score, row))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked[:limit]


def resolve_grounded_response(user_message: str):
    """Return an exact dataset reply or related examples for the AI fallback."""
    matches = find_response_matches(user_message)
    if not matches:
        return None, None, []

    best_score, best_row = matches[0]
    exact = best_score >= 1.0
    high_confidence = best_score >= 0.48
    best_keyword = best_row.get("_keyword_normalised", "")

    # The generic "internship" row in the CSV is a search tip, not a
    # definition. For questions such as "What is an internship?" or
    # "Can you explain an internship?", let OpenRouter generate the direct
    # explanation instead of returning a keyword-only but irrelevant answer.
    bypass_generic_reply = (
        (is_explanation_request(user_message) or looks_like_general_question(user_message))
        and best_keyword in GENERIC_RESPONSE_KEYWORDS
    )

    if (exact or high_confidence) and not bypass_generic_reply:
        return best_row.get("bot_reply", ""), best_row.get("keyword", ""), []

    # Do not send an irrelevant generic CSV answer as grounding context for a
    # definition request. OpenRouter should answer the question naturally.
    if bypass_generic_reply:
        return None, best_row.get("keyword", ""), []

    references = [
        {
            "keyword": row.get("keyword", ""),
            "category": row.get("category", ""),
            "reply": row.get("bot_reply", ""),
        }
        for _, row in matches
    ]
    return None, best_row.get("keyword", ""), references


# ── Load job/internship dataset ──────────────────────────────
def load_jobs() -> list[dict]:
    jobs: list[dict] = []
    if not os.path.exists(JOB_DATA_FILE):
        print(f"[WARN] Job dataset not found: {JOB_DATA_FILE}")
        return jobs

    try:
        with open(JOB_DATA_FILE, "r", newline="", encoding="utf-8-sig") as file:
            for index, row in enumerate(csv.DictReader(file), start=1):
                clean = {key: (value or "").strip() for key, value in row.items()}
                clean["_job_id"] = index
                clean["_title_tokens"] = tokenise(clean.get("internship_title", ""))
                clean["_category_tokens"] = tokenise(clean.get("category", ""))
                clean["_tokens"] = tokenise(
                    " ".join([
                        clean.get("internship_title", ""),
                        clean.get("company_name", ""),
                        clean.get("category", ""),
                        clean.get("search_text", ""),
                    ])
                )
                jobs.append(clean)
    except (OSError, csv.Error) as exc:
        print(f"[WARN] Could not load job dataset: {exc}")
    return jobs


JOBS = load_jobs()
JOBS_BY_ID = {job["_job_id"]: job for job in JOBS}

MAJOR_CATEGORY_MAP = {
    "Technology / Data": {
        "computer", "computing", "software", "technology", "information", "it",
        "data", "analytics", "artificial", "intelligence", "ai", "cyber",
        "engineering", "programming", "developer", "development"
    },
    "Marketing / Sales": {
        "marketing", "sales", "commerce", "advertising", "digital", "business"
    },
    "Finance / Accounting": {
        "finance", "financial", "accounting", "accountancy", "economics", "banking"
    },
    "Design / Creative": {
        "design", "creative", "animation", "graphic", "multimedia", "ux", "ui",
        "architecture", "fashion"
    },
    "Writing / Content": {
        "writing", "journalism", "communication", "communications", "media",
        "english", "content", "public", "relations"
    },
    "HR / Admin / Operations": {
        "human", "resources", "hr", "management", "operations", "administration",
        "logistics", "supply", "hospitality", "tourism"
    },
    "Education / Training": {
        "education", "teaching", "training", "psychology"
    },
    "Legal": {"law", "legal", "jurisprudence"},
    "NGO / Social Impact": {
        "social", "sociology", "environment", "environmental", "sustainability",
        "community", "development", "nonprofit", "ngo"
    },
}

STRENGTH_HINTS = {
    "communication": {"marketing", "sales", "content", "human", "resources", "telecalling", "business"},
    "writing": {"writing", "content", "copywriting", "journalism", "social", "media"},
    "creative": {"design", "creative", "graphic", "video", "animation", "marketing"},
    "creativity": {"design", "creative", "graphic", "video", "animation", "marketing"},
    "coding": {"development", "developer", "programming", "software", "web", "java", "python"},
    "python": {"python", "data", "machine", "learning", "development"},
    "java": {"java", "development", "software"},
    "analysis": {"data", "analytics", "research", "finance", "accounting", "market"},
    "analytical": {"data", "analytics", "research", "finance", "accounting", "market"},
    "leadership": {"operations", "management", "business", "development", "sales"},
    "teamwork": {"operations", "human", "resources", "business", "sales"},
    "organisation": {"operations", "administration", "human", "resources"},
    "organization": {"operations", "administration", "human", "resources"},
    "problem": {"technology", "data", "operations", "research", "finance"},
    "research": {"research", "data", "market", "content", "legal"},
    "detail": {"accounting", "finance", "legal", "data", "quality"},
}

JOB_INTENT_PATTERNS = [
    # Direct search/recommendation requests.
    r"\b(find|show|recommend|search|suggest|match)\b.{0,40}\b(jobs?|internships?|roles?|vacanc(?:y|ies)|openings?|opportunities)\b",
    r"\b(looking|look)\b.{0,20}\b(for|at)\b.{0,20}\b(jobs?|internships?|roles?|vacanc(?:y|ies)|openings?)\b",
    r"\b(i need|i want|get me|help me find)\b.{0,25}\b(a job|an internship|work|a role)\b",
    r"\bapply\b.{0,30}\b(job|internship|role|vacancy|opening)\b",

    # Natural questions such as: "Is there any job for computer science?"
    r"\b(is|are)\s+there\s+(?:any|some|available|open)?\s*(jobs?|internships?|roles?|vacanc(?:y|ies)|openings?|opportunities)\b",
    r"\b(any|available|open|current)\s+(jobs?|internships?|roles?|vacanc(?:y|ies)|openings?|opportunities)\b",
    # Require availability/search wording before treating "internship for X"
    # as a search. This prevents explanation requests from matching this rule.
    r"\b(?:available|open|current|find|show|search|recommend|suggest|match)\b.{0,30}\b(jobs?|internships?|roles?|vacanc(?:y|ies)|openings?|opportunities)\b.{0,35}\b(for|in|related to|matching|suitable for)\b",
    r"\bwhat\s+(jobs?|internships?|roles?)\s+(can|could|should|would)\s+i\b",
    r"\b(can|could|should)\s+i\s+(get|find|apply for)\s+(?:a|an|any)?\s*(job|internship|role)\b",
    r"\b(job|career)\s+opportunit(?:y|ies)\b",
]

# These are used only to pre-fill the programme/major from the first job-search
# message. The user can still type "restart jobs" to enter a different major.
MAJOR_PHRASE_ALIASES = {
    "computer science": "Computer Science",
    "information technology": "Information Technology",
    "software engineering": "Software Engineering",
    "data science": "Data Science",
    "artificial intelligence": "Artificial Intelligence",
    "cyber security": "Cybersecurity",
    "cybersecurity": "Cybersecurity",
    "business analytics": "Business Analytics",
    "business administration": "Business Administration",
    "human resources": "Human Resources",
    "accounting": "Accounting",
    "finance": "Finance",
    "marketing": "Marketing",
    "hospitality": "Hospitality",
    "tourism": "Tourism",
    "psychology": "Psychology",
    "law": "Law",
    "design": "Design",
    "communications": "Communications",
    "communication": "Communication",
    "engineering": "Engineering",
}


def is_job_search_intent(message: str) -> bool:
    """Return True when the user is asking to find, view, or apply for a role."""
    text = normalise_text(message)

    # Definition/explanation requests are normal questions, not vacancy searches.
    # Example: "Can you explain an internship for a university student?"
    if is_explanation_request(message):
        return False

    # Do not redirect informational questions about a role into job matching.
    if re.search(r"\b(job description|job duties|job responsibilities)\b", text):
        return False
    if re.search(r"\bwhat does\b.{0,35}\b(do|mean)\b", text):
        return False

    if any(re.search(pattern, text) for pattern in JOB_INTENT_PATTERNS):
        return True

    # Also catch concise searches such as "computer science jobs".
    has_job_noun = re.search(
        r"\b(jobs?|internships?|roles?|vacanc(?:y|ies)|openings?|opportunities)\b",
        text,
    )
    has_known_major = any(phrase_in_text(phrase, text) for phrase in MAJOR_PHRASE_ALIASES)
    return bool(has_job_noun and has_known_major)


def extract_major_from_job_query(message: str) -> str | None:
    """Extract an obvious programme/major from the first job-search message."""
    text = normalise_text(message)

    # Prefer specific multi-word majors over broad one-word fields.
    for phrase in sorted(MAJOR_PHRASE_ALIASES, key=len, reverse=True):
        if phrase_in_text(phrase, text):
            return MAJOR_PHRASE_ALIASES[phrase]

    # Fallback for phrases such as "jobs for biotechnology" when the major is
    # not in the alias list. Keep only a short, safe tail after for/in/with.
    match = re.search(
        r"\b(?:jobs?|internships?|roles?|vacanc(?:y|ies)|openings?|opportunities)\b"
        r".{0,20}\b(?:for|in|related to)\s+([a-z][a-z0-9 +#./&-]{1,60})$",
        text,
    )
    if match:
        candidate = re.sub(
            r"\b(me|students?|graduates?|people|university|college|school|freshers?)\b",
            " ",
            match.group(1),
        )
        candidate = re.sub(r"\s+", " ", candidate).strip(" .-?")
        generic_candidates = {
            "student", "university student", "college student", "graduate",
            "fresh graduate", "people", "me", "anyone",
        }
        if len(candidate) >= 2 and normalise_text(candidate) not in generic_candidates:
            return candidate.title()
    return None


def split_strengths(message: str) -> list[str]:
    # Keep separators until after splitting; normalise_text intentionally removes punctuation.
    value = (message or "").lower().strip()
    value = re.sub(r"\b(and|plus)\b", ",", value)
    raw_parts = re.split(r"[,;/\n]+", value)
    parts = [normalise_text(part).strip(" .-•") for part in raw_parts]
    return [part for part in parts if part][:3]


def normalise_experience(message: str) -> str:
    text = normalise_text(message)
    if any(term in text for term in ["no experience", "none", "zero", "never worked"]):
        return "No experience"
    if any(term in text for term in ["beginner", "entry", "fresh", "student", "less than 1", "under 1"]):
        return "Beginner / entry level"
    if any(term in text for term in ["intermediate", "1 year", "2 year", "some experience"]):
        return "Intermediate"
    if any(term in text for term in ["advanced", "senior", "3 year", "4 year", "5 year", "experienced"]):
        return "Advanced"
    return message.strip()[:80]


def target_categories_for_major(major: str) -> set[str]:
    major_tokens = tokenise(major)
    targets = set()
    for category, keywords in MAJOR_CATEGORY_MAP.items():
        if major_tokens & keywords:
            targets.add(category)
    return targets


def score_job(job: dict, major: str, strengths: list[str], experience: str) -> float:
    major_tokens = tokenise(major)
    strength_tokens = tokenise(" ".join(strengths))
    job_tokens = job.get("_tokens", set())
    title_tokens = job.get("_title_tokens", set())
    category_tokens = job.get("_category_tokens", set())
    category = job.get("category", "")

    score = 0.0
    # Matches in the actual title are more useful than matches elsewhere in search_text.
    score += len(major_tokens & title_tokens) * 7.0
    score += len(major_tokens & category_tokens) * 4.0
    score += len(major_tokens & job_tokens) * 1.5
    score += len(strength_tokens & title_tokens) * 5.0
    score += len(strength_tokens & job_tokens) * 1.5

    target_categories = target_categories_for_major(major)
    if category in target_categories:
        score += 12.0

    for strength in strength_tokens:
        hinted_terms = STRENGTH_HINTS.get(strength, set())
        score += len(hinted_terms & job_tokens) * 1.3

    title_lower = job.get("internship_title", "").lower()
    exp_lower = experience.lower()
    specialised = {"machine learning", "data science", "java", "python", "ui/ux", "legal", "finance"}
    if "no experience" in exp_lower or "beginner" in exp_lower or "entry" in exp_lower:
        if any(term in title_lower for term in ["business development", "social media", "content", "operations", "assistant"]):
            score += 1.0
    elif "advanced" in exp_lower or "intermediate" in exp_lower:
        if any(term in title_lower for term in specialised):
            score += 1.5

    # Small preference for complete, paid listings when relevance is otherwise equal.
    if job.get("stipend_type") == "Paid Amount":
        score += 0.15
    if job.get("company_name"):
        score += 0.05
    return score


def recommend_jobs(major: str, strengths: list[str], experience: str, limit: int = 15) -> list[dict]:
    ranked = [(score_job(job, major, strengths, experience), job) for job in JOBS]
    ranked.sort(
        key=lambda item: (
            item[0],
            float(item[1].get("stipend_average") or 0),
            item[1].get("internship_title", ""),
        ),
        reverse=True,
    )

    results = []
    seen = set()
    for score, job in ranked:
        identity = (
            job.get("internship_title", "").lower(),
            job.get("company_name", "").lower(),
            job.get("location", "").lower(),
        )
        if identity in seen:
            continue
        seen.add(identity)
        copy = dict(job)
        copy["_match_score"] = round(score, 2)
        results.append(copy)
        if len(results) >= limit:
            break
    return results


def compatibility_label(score: float) -> str:
    """Turn the internal ranking score into a readable, non-statistical label."""
    if score >= 20:
        return "Strong match"
    if score >= 12:
        return "Good match"
    return "Potential match"


def job_match_reasons(job: dict, flow: dict) -> list[str]:
    """Explain the main profile signals used to rank one dataset record."""
    reasons: list[str] = []
    major = flow.get("major", "")
    strengths = flow.get("strengths", [])
    category = job.get("category", "")
    job_tokens = job.get("_tokens", set())

    if category in target_categories_for_major(major):
        reasons.append(f"{major} aligns with the {category} category")

    matched_strengths = []
    for strength in strengths:
        strength_tokens = tokenise(strength)
        hinted_tokens = set()
        for token in strength_tokens:
            hinted_tokens |= STRENGTH_HINTS.get(token, set())
        if (strength_tokens & job_tokens) or (hinted_tokens & job_tokens):
            matched_strengths.append(strength)
    if matched_strengths:
        reasons.append("strength match: " + ", ".join(matched_strengths[:3]))

    if not reasons:
        reasons.append("closest available title/category match in the dataset")
    return reasons[:2]


def format_job_matches(flow: dict, offset: int = 0) -> str:
    job_ids = flow.get("job_ids", [])
    selected_ids = job_ids[offset:offset + 5]
    if not selected_ids:
        return "I do not have more matching jobs in this result set. Type **restart jobs** to create a new profile."

    lines = [
        "### Compatible jobs from the job-market dataset",
        f"Profile used: **{flow['major']}** · strengths: **{', '.join(flow['strengths'])}** · experience: **{flow['experience']}**",
        "",
    ]

    for number, job_id in enumerate(selected_ids, start=1):
        job = JOBS_BY_ID.get(job_id)
        if not job:
            continue
        title = job.get("internship_title") or "Untitled role"
        company = job.get("company_name") or "Company not listed"
        location = job.get("location") or "Location not listed"
        mode = job.get("work_mode") or "Mode not listed"
        start_date = job.get("start_date") or "Start date not listed"
        duration = job.get("duration") or "Duration not listed"
        stipend = job.get("stipend") or "Compensation not listed"
        category = job.get("category") or "Other"
        match_score = score_job(job, flow["major"], flow["strengths"], flow["experience"])
        match_label = compatibility_label(match_score)
        reasons = "; ".join(job_match_reasons(job, flow))
        lines.extend([
            f"**{number}. {title} — {company}**",
            f"- **{match_label}** · {reasons}",
            f"- Market details: {category} · {location} · {mode}",
            f"- Start: {start_date} · Duration: {duration} · Compensation: {stipend}",
            "",
        ])

    lines.append("Reply **apply 1**, **apply 2**, etc. to create a focused application for that role, or type **more jobs**.")
    lines.append("\n*These are records from your uploaded job dataset, not a live vacancy feed. Verify that each listing is still active before applying.*")
    return "\n".join(lines)


def application_focus_points(job: dict, strengths: list[str]) -> list[str]:
    category = job.get("category", "")
    title = job.get("internship_title", "the role")
    strengths_text = ", ".join(strengths)
    category_focus = {
        "Technology / Data": "projects, technical tools, debugging, data work, and measurable technical outcomes",
        "Marketing / Sales": "campaigns, customer communication, content performance, sales support, and measurable engagement",
        "Finance / Accounting": "accuracy, Excel, analysis, reconciliation, reporting, and attention to detail",
        "Design / Creative": "portfolio work, design tools, visual decisions, user needs, and completed creative outputs",
        "Writing / Content": "published writing, research, editing, content planning, and audience-focused communication",
        "HR / Admin / Operations": "coordination, scheduling, records, stakeholder communication, and process improvement",
        "Education / Training": "teaching, facilitation, lesson support, learner communication, and patience",
        "Legal": "research, document review, accuracy, confidentiality, and structured written analysis",
        "NGO / Social Impact": "community work, volunteering, stakeholder engagement, research, and mission alignment",
    }.get(category, "relevant projects, measurable results, responsibilities, and tools used")

    return [
        f"Lead with evidence related to **{title}**, not a general career objective.",
        f"Use examples that demonstrate **{strengths_text}**.",
        f"Prioritise {category_focus}.",
    ]


def build_application_pack(job: dict, flow: dict) -> str:
    title = job.get("internship_title") or "the advertised role"
    company = job.get("company_name") or "your company"
    major = flow.get("major", "student")
    strengths = flow.get("strengths", [])
    experience = flow.get("experience", "student-level")
    strengths_text = ", ".join(strengths)

    if "no experience" in experience.lower():
        experience_sentence = "Although I am at the beginning of my professional experience, I have been building relevant capability through my studies, projects, and practical activities."
    else:
        experience_sentence = f"My current experience level is {experience.lower()}, supported by relevant study, projects, and practical work."

    focus_points = application_focus_points(job, strengths)
    lines = [
        f"### Application: {title} — {company}",
        "",
        "**Why this role matches your profile**",
        f"- Programme/major: {major}",
        f"- Strengths to prove: {strengths_text}",
        f"- Dataset category: {job.get('category') or 'Not listed'}",
        "",
        "**Focused application message**",
        "",
        f"Dear Hiring Team at {company},",
        "",
        f"I am applying for the {title} opportunity. I am studying {major}, and my strongest relevant qualities are {strengths_text}. {experience_sentence}",
        "",
        f"The role's focus on {title.lower()} aligns with my background in {major} and my strengths in {strengths_text}. In my CV, I would support this with the most relevant coursework, projects, or work examples rather than unrelated experience. I would welcome the opportunity to discuss how these capabilities could support the team at {company}.",
        "",
        "Kind regards,  ",
        "[Your name]",
        "",
        "**CV focus for this application**",
    ]
    lines.extend([f"- {point}" for point in focus_points])
    lines.extend([
        "",
        "**How to apply**",
        f"The dataset does not contain an application URL. Search the exact listing **\"{title}\" at \"{company}\"**, verify that it is active, then submit the tailored message with your CV.",
        "",
        "Type **back to jobs** to choose another match or **restart jobs** to change your profile.",
    ])
    return "\n".join(lines)


def start_job_flow(initial_message: str | None = None) -> tuple[str, str, str]:
    """Start the guided job flow and pre-fill an obvious major when available."""
    detected_major = extract_major_from_job_query(initial_message or "")
    if detected_major:
        session["job_flow"] = {
            "stage": "strengths",
            "major": detected_major,
            "initial_query": (initial_message or "")[:250],
        }
        return (
            f"Yes — I can match you with roles from the job dataset. "
            f"I understood your **programme/major as {detected_major}**.\n\n"
            "**Step 2 of 3: What are your top three strengths?** "
            "Separate them with commas.\n\n"
            "Example: Python, data analysis, problem-solving.\n\n"
            "Type **restart jobs** if the detected programme/major is incorrect.",
            "job_flow",
            "Job flow: major detected → top three strengths",
        )

    session["job_flow"] = {"stage": "major"}
    return (
        "Yes — I can match you with compatible roles from the job dataset. "
        "**Step 1 of 3: What is your programme or major?**\n\n"
        "Example: Computer Science, Business, Accounting, Psychology, or Hospitality.",
        "job_flow",
        "Job flow: programme/major",
    )


def parse_job_selection(message: str) -> int | None:
    """Parse only an explicit result choice such as ``apply 2`` or ``2``.

    A full-string match is intentional. It prevents unrelated messages such as
    ``I have 2 years of experience`` from accidentally selecting job number 2.
    """
    text = normalise_text(message)
    match = re.fullmatch(
        r"(?:(?:apply|job|option|number|choose)\s*)?([1-5])",
        text,
    )
    return int(match.group(1)) if match else None


GENERAL_QUESTION_PREFIXES = (
    "what", "why", "how", "when", "where", "who", "which",
    "can", "could", "would", "should", "will",
    "do", "does", "did", "is", "are", "am", "has", "have",
    "explain", "describe", "define", "tell me",
    "i want to know", "i would like to know", "help me understand",
)


def looks_like_general_question(message: str) -> bool:
    """Recognise a normal informational question during a guided flow."""
    raw = (message or "").strip()
    text = normalise_text(raw)
    if not text:
        return False
    if raw.endswith("?"):
        return True
    return any(text == prefix or text.startswith(prefix + " ") for prefix in GENERAL_QUESTION_PREFIXES)


def is_job_flow_command(message: str) -> bool:
    """Return True only for commands that deliberately control job matching."""
    text = normalise_text(message)
    if text in {
        "cancel", "cancel jobs", "stop", "exit",
        "restart", "restart job", "restart jobs", "start over",
        "more", "more job", "more jobs", "next", "next jobs",
        "back", "back to jobs", "show jobs", "show matches",
    }:
        return True
    return parse_job_selection(message) is not None


def is_valid_experience_answer(message: str) -> bool:
    """Check whether a message can safely be consumed as experience level."""
    text = normalise_text(message)
    if not text:
        return False

    recognised_terms = (
        "no experience", "none", "zero", "never worked", "novice",
        "beginner", "entry level", "entry", "fresh graduate", "fresher",
        "student", "intermediate", "some experience", "advanced",
        "senior", "experienced",
    )
    if any(term in text for term in recognised_terms):
        return True

    number = r"(?:\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten)"
    return bool(re.search(rf"\b{number}\s*(?:months?|years?)\b", text))


def should_pause_job_flow_for_question(user_message: str, flow: dict) -> bool:
    """Pause job matching when the user asks an unrelated normal question.

    Valid answers for the current stage still continue the questionnaire. A
    separate question is answered through the response dataset/OpenRouter while
    the existing job-flow state remains in the session.
    """
    stage = flow.get("stage")
    if stage not in {"major", "strengths", "experience", "jobs"}:
        return False

    if is_job_flow_command(user_message):
        return False

    # Accept valid form answers before checking for question-like wording.
    if stage == "strengths" and len(split_strengths(user_message)) >= 3:
        return False
    if stage == "experience" and is_valid_experience_answer(user_message):
        return False

    # A major normally consists of a short field value, not a question.
    if stage == "major" and not looks_like_general_question(user_message):
        return False

    return is_explanation_request(user_message) or looks_like_general_question(user_message)


def job_flow_resume_message(flow: dict) -> str:
    """Tell the user how to continue after a temporary question interruption."""
    stage = flow.get("stage")
    reminders = {
        "major": (
            "Your job-matching flow is still open. Please enter your "
            "**programme or major**, or type **cancel jobs**."
        ),
        "strengths": (
            "Your job-matching flow is still open. Please provide your "
            "**top three strengths**, separated by commas, or type **cancel jobs**."
        ),
        "experience": (
            "Your job-matching flow is still open. Please provide your "
            "**experience level**: no experience, beginner, intermediate, or advanced."
        ),
        "jobs": (
            "Your job matches are still available. Reply **apply 1**, **apply 2**, "
            "etc., or use **more jobs**, **restart jobs**, or **cancel jobs**."
        ),
    }
    return reminders.get(stage, "Your job-matching flow is still open.")


def answer_standard_question(user_message: str, history: list):
    """Answer through CSV grounding first, then OpenRouter fallback."""
    grounded_reply, matched_kw, references = resolve_grounded_response(user_message)
    if grounded_reply:
        return (
            grounded_reply,
            "response_dataset",
            f"Response dataset: '{matched_kw}'",
            matched_kw,
        )

    bot_reply, status, process = get_openrouter_reply(user_message, history, references)
    return bot_reply, status, process, matched_kw


def handle_job_flow(user_message: str):
    flow = session.get("job_flow") or {}
    stage = flow.get("stage")
    text = normalise_text(user_message)

    if text in {"cancel", "cancel jobs", "stop", "exit"}:
        session.pop("job_flow", None)
        return "Job matching cancelled. You can still ask a normal career question.", "job_flow", "Job flow: cancelled"

    if text in {"restart", "restart job", "restart jobs", "start over"}:
        return start_job_flow()

    if stage == "major":
        if len(user_message.strip()) < 2:
            return "Please enter your programme or major.", "job_flow", "Job flow: programme/major"
        flow["major"] = user_message.strip()[:120]
        flow["stage"] = "strengths"
        session["job_flow"] = flow
        return (
            "What are your **top three strengths**? Separate them with commas.\n\nExample: Python, data analysis, problem-solving.",
            "job_flow",
            "Job flow: top three strengths",
        )

    if stage == "strengths":
        strengths = split_strengths(user_message)
        if len(strengths) < 3:
            return (
                "Please provide **three distinct strengths**, separated by commas.\n\nExample: communication, teamwork, organisation.",
                "job_flow",
                "Job flow: top three strengths",
            )
        flow["strengths"] = strengths[:3]
        flow["stage"] = "experience"
        session["job_flow"] = flow
        return (
            "What is your **experience level**?\n\nYou can answer: no experience, beginner/entry level, intermediate, or advanced.",
            "job_flow",
            "Job flow: experience level",
        )

    if stage == "experience":
        if not is_valid_experience_answer(user_message):
            return (
                "Please enter a valid **experience level**: no experience, "
                "beginner/entry level, intermediate, advanced, or a duration "
                "such as 6 months or 2 years.",
                "job_flow",
                "Job flow: experience level",
            )
        flow["experience"] = normalise_experience(user_message)
        matches = recommend_jobs(flow["major"], flow["strengths"], flow["experience"], limit=15)
        if not matches:
            session.pop("job_flow", None)
            return (
                "I could not load matching jobs from the dataset. Please check that the dataset file exists and contains records.",
                "error",
                "Job dataset unavailable",
            )
        flow["job_ids"] = [job["_job_id"] for job in matches]
        flow["offset"] = 0
        flow["stage"] = "jobs"
        session["job_flow"] = flow
        return format_job_matches(flow, 0), "job_flow", "Job flow: dataset matches"

    if stage == "jobs":
        if text in {"more", "more job", "more jobs", "next", "next jobs"}:
            next_offset = int(flow.get("offset", 0)) + 5
            if next_offset >= len(flow.get("job_ids", [])):
                next_offset = 0
            flow["offset"] = next_offset
            session["job_flow"] = flow
            return format_job_matches(flow, next_offset), "job_flow", "Job flow: more dataset matches"

        if text in {"back", "back to jobs", "show jobs", "show matches"}:
            return format_job_matches(flow, int(flow.get("offset", 0))), "job_flow", "Job flow: dataset matches"

        selection = parse_job_selection(user_message)
        if selection is None:
            return (
                "Choose a result by replying **apply 1**, **apply 2**, etc. You can also type **more jobs**, **restart jobs**, or **cancel jobs**.",
                "job_flow",
                "Job flow: choose a job",
            )

        offset = int(flow.get("offset", 0))
        visible_ids = flow.get("job_ids", [])[offset:offset + 5]
        if selection > len(visible_ids):
            return "That job number is not shown. Choose a number from 1 to 5.", "job_flow", "Job flow: choose a job"
        job = JOBS_BY_ID.get(visible_ids[selection - 1])
        if not job:
            return "That dataset record could not be loaded. Please choose another job.", "error", "Job flow: missing record"

        flow["selected_job_id"] = job["_job_id"]
        session["job_flow"] = flow
        return build_application_pack(job, flow), "job_flow", "Job flow: focused application"

    session.pop("job_flow", None)
    return start_job_flow()


# ── OpenRouter AI response ───────────────────────────────────
def _extract_openrouter_text(payload: dict) -> str:
    """Extract assistant text from an OpenRouter chat-completion response."""
    choices = payload.get("choices") or []
    if not choices:
        return ""

    message = choices[0].get("message") or {}
    content = message.get("content", "")

    if isinstance(content, str):
        return content.strip()

    # Some OpenAI-compatible providers return content as typed parts.
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(part.strip() for part in parts if part.strip()).strip()

    return ""


def get_openrouter_reply(user_message: str, history: list, references: list | None = None):
    """Generate an answer for questions not confidently covered by the CSV dataset."""
    if not OPENROUTER_API_KEY:
        if references:
            best = references[0]
            return best["reply"], "response_dataset", f"Related response: '{best['keyword']}'"
        return (
            "I could not find a matching saved response, and OpenRouter is not configured yet. "
            "Add `OPENROUTER_API_KEY` to the project's `.env` file, restart Flask, and try again.",
            "error",
            "OpenRouter not configured",
        )

    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    for turn in history[-10:]:
        user_text = (turn.get("user") or "").strip()
        bot_text = (turn.get("bot") or "").strip()
        if user_text:
            messages.append({"role": "user", "content": user_text})
        if bot_text:
            messages.append({"role": "assistant", "content": bot_text})

    if references:
        examples = "\n".join(
            f"- Topic: {item['keyword']} | Category: {item['category']} | Saved answer: {item['reply']}"
            for item in references
        )
        final_message = (
            f"User question: {user_message}\n\n"
            "No saved response matched with enough confidence. Use the related examples below "
            "only as grounding context. Answer the user's actual question directly, and do not "
            "copy irrelevant details.\n"
            f"{examples}"
        )
    else:
        final_message = (
            f"User question: {user_message}\n\n"
            "This question did not match the saved response dataset. Generate a helpful, "
            "career-focused answer using the system rules."
        )

    messages.append({"role": "user", "content": final_message})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    if OPENROUTER_SITE_URL:
        headers["HTTP-Referer"] = OPENROUTER_SITE_URL
    if OPENROUTER_APP_TITLE:
        headers["X-OpenRouter-Title"] = OPENROUTER_APP_TITLE

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.35 if references else 0.65,
        "max_tokens": 700,
    }

    try:
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=OPENROUTER_TIMEOUT_SECONDS,
        )

        if not response.ok:
            try:
                error_payload = response.json()
                error_obj = error_payload.get("error") or {}
                if isinstance(error_obj, dict):
                    error_message = error_obj.get("message") or str(error_obj)
                else:
                    error_message = str(error_obj)
            except (ValueError, AttributeError):
                error_message = response.text.strip() or "Unknown OpenRouter error"
            raise RuntimeError(f"HTTP {response.status_code}: {error_message}")

        try:
            result = response.json()
        except ValueError as exc:
            raise RuntimeError("OpenRouter returned invalid JSON") from exc

        reply = _extract_openrouter_text(result)
        if not reply:
            raise RuntimeError("OpenRouter returned an empty response")

        process = (
            f"OpenRouter fallback ({OPENROUTER_MODEL}) · related dataset context"
            if references
            else f"OpenRouter fallback ({OPENROUTER_MODEL})"
        )
        return reply, "answered", process

    except requests.Timeout:
        print("[ERROR] OpenRouter API: request timed out")
        if references:
            return references[0]["reply"], "response_dataset", "Response dataset fallback"
        return (
            "OpenRouter took too long to respond. Please try again in a moment.",
            "error",
            "OpenRouter timeout",
        )
    except requests.RequestException as exc:
        print(f"[ERROR] OpenRouter network error: {exc}")
        if references:
            return references[0]["reply"], "response_dataset", "Response dataset fallback"
        return (
            "The bot could not connect to OpenRouter. Check your internet connection and try again.",
            "error",
            f"OpenRouter network error: {str(exc)[:80]}",
        )
    except Exception as exc:
        print(f"[ERROR] OpenRouter API: {exc}")
        if references:
            return references[0]["reply"], "response_dataset", "Response dataset fallback"

        error_text = str(exc).lower()
        if "http 401" in error_text or "http 403" in error_text or "api key" in error_text:
            message = "OpenRouter could not authenticate. Check `OPENROUTER_API_KEY` in `.env`, then restart Flask."
        elif "http 402" in error_text or "credits" in error_text:
            message = "OpenRouter rejected the request because the account has insufficient credits or access. Check your OpenRouter account and API-key limits."
        elif "http 404" in error_text or "no endpoints found" in error_text or "model" in error_text and "not found" in error_text:
            message = "The selected OpenRouter model is unavailable. Confirm `OPENROUTER_MODEL` in `.env` and try again."
        elif "http 429" in error_text or "rate limit" in error_text:
            message = "The OpenRouter free-model rate limit has been reached. Please wait and try again later."
        elif any(code in error_text for code in ["http 500", "http 502", "http 503", "http 504"]):
            message = "The OpenRouter model provider is temporarily unavailable. Please try again shortly."
        else:
            message = "Sorry, OpenRouter could not generate a response right now. Please try again."

        return message, "error", f"OpenRouter error: {str(exc)[:80]}"


# ── Conversation logger ──────────────────────────────────────
def get_next_conversation_no():
    if not os.path.exists(LOG_FILE):
        return 1
    with open(LOG_FILE, "r", newline="", encoding="utf-8") as file:
        return sum(1 for _ in csv.DictReader(file)) + 1


def save_conversation(username, session_id, user_message, matched_keyword, status, process, bot_reply):
    os.makedirs(DATA_DIR, exist_ok=True)
    fieldnames = [
        "conversation_no", "session_id", "username", "user_message",
        "matched_keyword", "status", "process", "bot_reply", "timestamp"
    ]
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "conversation_no": get_next_conversation_no(),
            "session_id": session_id,
            "username": username,
            "user_message": user_message,
            "matched_keyword": matched_keyword or "",
            "status": status,
            "process": process,
            "bot_reply": bot_reply,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })


# ── User account CSV ─────────────────────────────────────────
def ensure_user_file():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w", newline="", encoding="utf-8") as file:
            file.write("firstName;lastName;email;username;password;agree\n")


def user_exists(username, email):
    ensure_user_file()
    with open(USER_FILE, "r", newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file, delimiter=";"):
            if (row.get("username") or "").strip().lower() == username.lower():
                return "Username already exists."
            if (row.get("email") or "").strip().lower() == email.lower():
                return "Email already exists."
    return None


def save_user_account(first_name, last_name, email, username, password, agree):
    ensure_user_file()
    with open(USER_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["firstName", "lastName", "email", "username", "password", "agree"],
            delimiter=";",
        )
        writer.writerow({
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "username": username,
            "password": password,
            "agree": agree,
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
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    session["username"] = username
    session["session_id"] = str(uuid.uuid4())
    session["history"] = []
    session.pop("job_flow", None)
    return jsonify({"success": True, "username": username})


@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json(silent=True) or {}
    first_name = (data.get("firstName") or "").strip()
    last_name = (data.get("lastName") or "").strip()
    name = (data.get("name") or "").strip()
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()
    agree = str(data.get("agree") or "yes").strip()

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
    session.pop("job_flow", None)
    return jsonify({"success": True, "username": username})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"success": True})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or session.get("username", "guest")).strip()
    user_message = (data.get("message") or "").strip()
    session_id = session.get("session_id", str(uuid.uuid4()))

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    history = session.get("history", [])
    matched_kw = None

    active_flow = session.get("job_flow") or {}
    job_flow_paused = False

    # 1. A separate normal question temporarily pauses, but does not cancel or
    #    consume, the active questionnaire. The saved profile can continue next.
    if active_flow and should_pause_job_flow_for_question(user_message, active_flow):
        bot_reply, status, process, matched_kw = answer_standard_question(
            user_message, history
        )
        bot_reply += f"\n\n---\n{job_flow_resume_message(active_flow)}"
        process += " · job flow paused for separate question"
        job_flow_paused = True

    # 2. Continue an active guided job flow.
    elif active_flow:
        bot_reply, status, process = handle_job_flow(user_message)
        matched_kw = "job_flow"

    # 3. Start the guided job flow only for an actual search/application request.
    elif is_job_search_intent(user_message):
        bot_reply, status, process = start_job_flow(user_message)
        matched_kw = "job_search"

    # 4. Answer known questions through CSV grounding, then use OpenRouter for
    #    unmatched or open-ended questions.
    else:
        bot_reply, status, process, matched_kw = answer_standard_question(
            user_message, history
        )

    history.append({"user": user_message, "bot": bot_reply})
    session["history"] = history[-20:]

    try:
        save_conversation(
            username, session_id, user_message, matched_kw, status, process, bot_reply
        )
    except OSError as exc:
        print(f"[WARN] Could not save conversation log: {exc}")

    return jsonify({
        "reply": bot_reply,
        "process": process,
        "status": status,
        "job_flow_paused": job_flow_paused,
        "job_flow_stage": active_flow.get("stage") if job_flow_paused else None,
    })


@app.route("/api/ai_status")
def api_ai_status():
    """Small diagnostics endpoint; never exposes the API key."""
    return jsonify({
        "openrouter_configured": bool(OPENROUTER_API_KEY),
        "openrouter_model": OPENROUTER_MODEL,
        "response_rows": len(BOT_RESPONSES),
        "job_rows": len(JOBS),
        "routing": [
            "separate normal question during an active job flow",
            "active job flow",
            "new job-search flow",
            "confident response-dataset match",
            "OpenRouter fallback for unmatched open-ended questions",
        ],
    })


@app.route("/api/history")
def api_history():
    entries = []
    if not os.path.exists(LOG_FILE):
        return jsonify(entries)
    with open(LOG_FILE, "r", newline="", encoding="utf-8") as file:
        entries.extend(csv.DictReader(file))
    return jsonify(entries[-50:])


@app.route("/api/clear_history", methods=["POST"])
def clear_history():
    session["history"] = []
    session.pop("job_flow", None)
    return jsonify({"success": True})


if __name__ == "__main__":
    print("=" * 60)
    print("  InternAI CareerBot — Flask Server")
    print("  http://127.0.0.1:5002")
    print(f"  Loaded response rows: {len(BOT_RESPONSES)}")
    print(f"  Loaded job rows: {len(JOBS)}")
    if not OPENROUTER_API_KEY:
        print("  OpenRouter fallback disabled: add OPENROUTER_API_KEY to .env")
    else:
        print(f"  OpenRouter fallback enabled: {OPENROUTER_MODEL}")
    print("=" * 60)
    app.run(debug=True, port=5002)