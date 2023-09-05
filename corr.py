#!/usr/bin/python3
import os, time, requests
from bottle import route, run, template, response, request
from threading import Thread

@route('/')
def index():
   return "Hello"

def check(cb):
  # check the database if the parts of the rule match any message in the database
  # if we find a message in database
  #   requests.put(cb, data ={'subject': database.line.subject, 'date': database.line.sent, 'sender': database.line.sender, 'text': database.line.text})
  #   database.line.delete
  # else # we store the rule in the database
  #   database.rules.addnewentry senderpattern, subjectpattern, textpattern, datepattern
  #   database.rules.alsoadd cb
  print('test')

@route('/get_matching_message')
def index():
    response.content_type = "text/plain; charset=UTF-8"
    response.headers["CPEE-CALLBACK"] = "true"
    thread = Thread(target=check, args=[request.headers['Cpee-Callback']])
    thread.start()
    return ""

port = int(os.environ.get('PORT', 20147))
run(host='::1', port=port, debug=True)
