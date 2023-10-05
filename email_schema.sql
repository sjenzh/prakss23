DROP TABLE IF EXISTS messages;

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mail_id INTEGER NOT NULL,
    received_date DATETIME NOT NULL, 
    subject VARCHAR(998),
    sender VARCHAR(254) NOT NULL,
    content TEXT,
    has_attachment BOOLEAN DEFAULT 0
);