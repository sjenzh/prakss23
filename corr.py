#!/usr/bin/python3
import os, time, requests
import sqlite3
import json

from pathlib import Path
from threading import Thread

from bottle import route, run, template, response, request
from bottle import TEMPLATE_PATH

TEMPLATE_PATH.append(str(Path('prakss23')/ 'views'))

@route('/')
def index():
   conn = sqlite3.connect('database.db')
   c = conn.cursor()
   c.execute('SELECT subject FROM rules')
   rules_res = c.fetchall()
   c.execute('SELECT subject FROM messages')
   messages_res = c.fetchall()
   c.close()
   output = template('make_queues', {'rules':rules_res, 'messages':messages_res})
   return output

def check(cb,params):
  # check the database if the parts of the rule match any message in the database
  # if we find a message in database
  #   requests.put(cb, data ={'subject': database.line.subject, 'date': database.line.sent, 'sender': database.line.sender, 'text': database.line.text})
  #   database.line.delete
  # else # we store the rule in the database
  #   database.rules.addnewentry senderpattern, subjectpattern, textpattern, datepattern
  #   database.rules.alsoadd cb
  print(cb)
  print(params)
  print(params.keys())
  print(params.items())
  print(type(params.items()))
  for x in params.items():
      print(x, type(x))
  json_dict = { x[0] : x[1] for x in params.items()}
  print(json_dict, type(json_dict)) #json_dict is a dict
  dump = json.dumps(json_dict)
  print(dump, type(dump)) #dump = str
  fin = json.JSONEncoder().encode(json_dict)
  print(fin, type(fin)) #fin is a str
  requests.put(cb,data=dump, headers={'content-type': 'application/json'})
  
@route('/test')
def fetch_info():
   return template("Test result: {{result}}", result=request)

@route('/get_matching_message')
def index():
    response.headers.content_type =  'text/plain; charset=UTF-8'
    response.headers['CPEE-CALLBACK'] = 'true'
    response.status = 200
    response.body = ''
    thread = Thread(target=check, args=[request.headers['Cpee-Callback'],request.params])
    thread.start()
    return response

port = int(os.environ.get('PORT', 20147))
run(host='::1', port=port, debug=True)
