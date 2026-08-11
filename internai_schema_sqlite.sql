PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL DEFAULT '',
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    agreed_to_terms BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_username ON users(username);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id VARCHAR(100) NOT NULL,
    user_id INTEGER,
    username_snapshot VARCHAR(100) NOT NULL,
    user_message TEXT NOT NULL,
    matched_keyword VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    process VARCHAR(500),
    bot_reply TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS ix_conversations_conversation_id ON conversations(conversation_id);
CREATE INDEX IF NOT EXISTS ix_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS ix_conversations_username_snapshot ON conversations(username_snapshot);
CREATE INDEX IF NOT EXISTS ix_conversations_created_at ON conversations(created_at);

CREATE TABLE IF NOT EXISTS bot_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL DEFAULT '',
    bot_reply TEXT NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'csv',
    updated_at DATETIME NOT NULL,
    CONSTRAINT uq_bot_response_keyword_category UNIQUE(keyword, category)
);
CREATE INDEX IF NOT EXISTS ix_bot_responses_keyword ON bot_responses(keyword);

CREATE TABLE IF NOT EXISTS job_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL UNIQUE,
    source_type VARCHAR(30) NOT NULL DEFAULT 'csv',
    base_url TEXT,
    enabled BOOLEAN NOT NULL DEFAULT 1,
    last_synced_at DATETIME,
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    external_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL DEFAULT '',
    category VARCHAR(150) NOT NULL DEFAULT '',
    location VARCHAR(255) NOT NULL DEFAULT '',
    work_mode VARCHAR(100) NOT NULL DEFAULT '',
    start_date VARCHAR(100) NOT NULL DEFAULT '',
    duration VARCHAR(100) NOT NULL DEFAULT '',
    compensation VARCHAR(255) NOT NULL DEFAULT '',
    currency VARCHAR(20) NOT NULL DEFAULT '',
    stipend_type VARCHAR(100) NOT NULL DEFAULT '',
    payment_period VARCHAR(100) NOT NULL DEFAULT '',
    has_incentives BOOLEAN NOT NULL DEFAULT 0,
    stipend_min REAL,
    stipend_max REAL,
    stipend_average REAL,
    description TEXT NOT NULL DEFAULT '',
    search_text TEXT NOT NULL DEFAULT '',
    source_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    first_seen_at DATETIME NOT NULL,
    last_seen_at DATETIME NOT NULL,
    CONSTRAINT uq_job_source_external_id UNIQUE(source_id, external_id),
    FOREIGN KEY(source_id) REFERENCES job_sources(id)
);
CREATE INDEX IF NOT EXISTS ix_jobs_source_id ON jobs(source_id);
CREATE INDEX IF NOT EXISTS ix_jobs_title ON jobs(title);
CREATE INDEX IF NOT EXISTS ix_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS ix_jobs_category ON jobs(category);
CREATE INDEX IF NOT EXISTS ix_jobs_is_active ON jobs(is_active);
CREATE INDEX IF NOT EXISTS ix_jobs_last_seen_at ON jobs(last_seen_at);

CREATE TABLE IF NOT EXISTS scrape_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    records_found INTEGER NOT NULL DEFAULT 0,
    records_created INTEGER NOT NULL DEFAULT 0,
    records_updated INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    started_at DATETIME NOT NULL,
    completed_at DATETIME,
    FOREIGN KEY(source_id) REFERENCES job_sources(id)
);
CREATE INDEX IF NOT EXISTS ix_scrape_runs_source_id ON scrape_runs(source_id);

CREATE TABLE IF NOT EXISTS job_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    job_id INTEGER,
    conversation_id VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'generated',
    application_text TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS ix_job_applications_user_id ON job_applications(user_id);
CREATE INDEX IF NOT EXISTS ix_job_applications_job_id ON job_applications(job_id);
CREATE INDEX IF NOT EXISTS ix_job_applications_conversation_id ON job_applications(conversation_id);
