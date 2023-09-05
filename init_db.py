import sqlite3
connection = sqlite3.connect('database.db')

with open('rule_schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Rule 
cur.execute("INSERT INTO rules (title, content) VALUES (?, ?)", ('Rule 1', 'Content of rule 1'))
cur.execute("INSERT INTO rules (title, content) VALUES (?, ?)", ('Rule 2', 'Content of rule 2'))
cur.execute("INSERT INTO rules (title, content) VALUES (?, ?)", ('Rule 3', 'Content of rule 3'))

connection.commit()
connection.close()

# connection = sqlite3.connect('database.db')
# #MESSAGES

#  # datearrived DATETIME NOT NULL,
#  # sender TEXT NOT NULL,
#  # title TEXT NOT NULL,
#  # content TEXT NOT NULL
# with open('email_schema.sql') as f:
#     connection.executescript(f.read())

# cur = connection.cursor()

# # Message
# cur.execute("INSERT INTO messages (title, content) VALUES (?, ?)", ('Message 1', 'Content of message 1'))
# cur.execute("INSERT INTO messages (title, content) VALUES (?, ?)", ('Message 2', 'Content of message 2'))
# cur.execute("INSERT INTO messages (title, content) VALUES (?, ?)", ('Message 3', 'Content of message 3'))

# connection.commit()
# connection.close()

