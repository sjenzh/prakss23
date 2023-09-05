#!/usr/bin/python3
import os, time, requests
import sqlite3
from pathlib import Path
from threading import Thread

from bottle import route, run, template, response, request
from bottle import TEMPLATE_PATH

TEMPLATE_PATH.append(str(Path('prakss23')/ 'views'))

@route('/')
def index():
   conn = sqlite3.connect('database.db')
   c = conn.cursor()
   c.execute('SELECT title FROM rules')
   rules_res = c.fetchall()
   c.execute('SELECT title FROM messages')
   messages_res = c.fetchall()
   c.close()
   output = template('make_queues', {'rules':rules_res, 'messages':messages_res})
   return output

def check(cb):
  # check the database if the parts of the rule match any message in the database
  # if we find a message in database
  #   requests.put(cb, data ={'subject': database.line.subject, 'date': database.line.sent, 'sender': database.line.sender, 'text': database.line.text})
  #   database.line.delete
  # else # we store the rule in the database
  #   database.rules.addnewentry senderpattern, subjectpattern, textpattern, datepattern
  #   database.rules.alsoadd cb
  print('test')

@route('/test')
def fetch_info():
   return str(request)

@route('/get_matching_message')
def index():
    response.content_type = "text/plain; charset=UTF-8"
    response.headers["CPEE-CALLBACK"] = "true"
    thread = Thread(target=check, args=[request.headers['Cpee-Callback']])
    thread.start()
    return ""

port = int(os.environ.get('PORT', 20147))
run(host='::1', port=port, debug=True)
