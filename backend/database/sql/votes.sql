CREATE TABLE IF NOT EXISTS votes (
    report_id    INTEGER REFERENCES reports(id),
    user_id      INTEGER REFERENCES users(id),
    is_upvoted   BOOLEAN DEFAULT FALSE,
    is_downvoted BOOLEAN DEFAULT FALSE,
    timestamp    TIMESTAMP NOT NULL,
    PRIMARY KEY (report_id, user_id)
);
