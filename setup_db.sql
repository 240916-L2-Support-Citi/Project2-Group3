CREATE DATABASE api_logs;

CREATE TABLE IF NOT EXISTS api_logs (
    id SERIAL PRIMARY KEY,
    log_level VARCHAR(10),
    status_code INT,
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);