import sqlite3

def import_sql_file(filename, database):
  connection = sqlite3.connect(database)
  with open(filename) as f:
    connection.executescript(f.read())
  connection.commit()
  connection.close()

import_sql_file('email_schema.sql', 'database.db')
import_sql_file('rule_schema.sql', 'database.db')


