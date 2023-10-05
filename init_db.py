import sqlite3
import datetime
connection = sqlite3.connect('database.db')

with open('rule_schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Rule
# date_after?: datetime, date_before?: datetime
# subject?: text (regex)
# sender?: text (regex)
# content?: text (regex)
# has_attachment?: boolean
# callback: text
# persistent? bool : default 0
cur.execute("INSERT INTO rules (subject, callback) VALUES (?,?)", ('regex for subject 1', 'http://thisisacallback.com'))
# cur.execute("INSERT INTO rules (date_after, date_before, subject, sender, content, has_attachment, callback) VALUES (?, ?,?,?)", ('Rule 1', 'Content of rule 1'))
# cur.execute("INSERT INTO rules (title, content) VALUES (?, ?)", ('Rule 2', 'Content of rule 2'))
# cur.execute("INSERT INTO rules (title, content) VALUES (?, ?)", ('Rule 3', 'Content of rule 3'))

connection.commit()
connection.close()

connection = sqlite3.connect('database.db')
#MESSAGES

 # datearrived DATETIME NOT NULL,
 # sender TEXT NOT NULL,
 # title TEXT NOT NULL,
 # content TEXT NOT NULL
with open('email_schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Message: received_date: datetime, subject: varchar(998), sender:varchar(254) /maxlen of an e-mail address, content:text, hasattachment:boolean
# Date has to comply with ISO 8601
cur.execute("INSERT INTO messages (mail_id, received_date, subject, sender, content, has_attachment) VALUES (?, ?, ?, ?, ?, ?)", (129038901, "2023-10-03T17:16:33+00:00", 'Subject of message 1', 'thisisanemail@email.com', 'content of message 1', 1))
# cur.execute("INSERT INTO messages (title, content) VALUES (?, ?)", ('Message 2', 'Content of message 2'))
# cur.execute("INSERT INTO messages (title, content) VALUES (?, ?)", ('Message 3', 'Content of message 3'))

connection.commit()
connection.close()

