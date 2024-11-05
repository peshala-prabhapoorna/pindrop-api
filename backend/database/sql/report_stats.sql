CREATE TABLE IF NOT EXISTS report_stats (
    report_id      INTEGER PRIMARY KEY REFERENCES reports(id),
    view_count     INTEGER DEFAULT 0,
    upvote_count   INTEGER DEFAULT 0,
    downvote_count INTEGER DEFAULT 0,
    comment_count  INTEGER DEFAULT 0
);
