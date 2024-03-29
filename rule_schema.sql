DROP TABLE IF EXISTS rules;

CREATE TABLE rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_after DATETIME DEFAULT NULL,
    date_before DATETIME DEFAULT NULL,
    subject TEXT DEFAULT NULL,
    sender TEXT DEFAULT NULL,
    content TEXT DEFAULT NULL,
    has_attachment BOOLEAN DEFAULT 0,
    callback TEXT NOT NULL,
    persistent BOOLEAN NOT NULL DEFAULT 0
);