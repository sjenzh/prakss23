#!/usr/bin/python3
import os, requests
import datetime
from dateutil import parser
import sqlite3
import json
import datetime

from pathlib import Path
from threading import Thread

from bottle import route, run, template, response, request
from bottle import TEMPLATE_PATH

TEMPLATE_PATH.append(str(Path('prakss23')/ 'views'))

@route('/')
def index():
   conn = sqlite3.connect('database.db')
   conn.enable_load_extension(True)
   c = conn.cursor()
   c.execute('SELECT load_extension("/usr/lib/sqlite3/pcre.so")')
   c.execute('SELECT subject FROM rules WHERE id REGEXP "\d"')
   rules_res = c.fetchall()
  #  print('2023-10-03T15:16:33+0000')
  #  print(parser.parse('2023-10-03T15:16:33+0000'))
  #  parsed_date = parser.parse('2023-10-03T15:16:33+0000')
  #  print(type(parsed_date))
   #localizing timezones
   c.execute('SELECT received_date FROM messages WHERE received_date > ?', (datetime.datetime.fromisoformat('2023-10-03 17:16:33+01:00').astimezone(datetime.timezone.utc),))
   messages_res = c.fetchall()
  #  for x in messages_res:
  #     print(x,type(x))
  #     if type(x) is tuple:
  #        print(x[0], type(x[0]))
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
  stmt = ""
  stmt_params = []
  rule_columns = []
  #print(params.keys())
  #print(params.items())
  #print(type(params.items()))
  for (k,v) in params.items():
      print(k, type(k),v, type(v))
      if len(v) != 0: #field is not empty
          rule_columns.append(k)
          if((k=='subject') or (k=='content') or (k=='sender')):#regex
              stmt = stmt+k+" REGEXP \""+v+"\" AND "
          elif((k=='before')): #datetime 
              stmt = stmt+"received_date < ?"+" AND "
              stmt_params.append(datetime.datetime.fromisoformat(v).astimezone(datetime.timezone.utc))
          elif((k=='after')): #datetime
              stmt = stmt+"received_date > ?"+" AND "
              stmt_params.append(datetime.datetime.fromisoformat(v).astimezone(datetime.timezone.utc))
  if len(stmt)>1:
      stmt = stmt[:-5] #removes last AND
  print(stmt)
  sql = "SELECT id FROM messages WHERE "+stmt
  print(sql, stmt_params)
  conn = sqlite3.connect('database.db')
  conn.enable_load_extension(True)
  c = conn.cursor()
  c.execute('SELECT load_extension("/usr/lib/sqlite3/pcre.so")')
  c.execute(sql, stmt_params)
  res = c.fetchall()
  c.close()
  if len(res) == 0:
      rule_columns.append('callback')
      rule_values = list(params.values())
      rule_values.append(cb)
      rule_values = [x for x in rule_values if x != ""]
      for x in rule_columns:
          if x == 'after':
              rule_columns[rule_columns.index(x)] = 'date_after'
          elif x == 'before':
              rule_columns[rule_columns.index(x)] = 'date_before'
      placeholders = ', '.join(['?'] * len(rule_values))
      print(rule_columns, rule_values)
      insert_into_stmt = f'INSERT INTO rules ({", ".join(rule_columns)}) VALUES ({placeholders})'
      print(insert_into_stmt)
      conn = sqlite3.connect('database.db')
      c = conn.cursor()
      c.execute(insert_into_stmt, rule_values)
      conn.commit()
      conn.close()
      print('No matches found, TODO: add rule to database')
  else:
      print('res:', res, min(res))
      matched_email_stmt = 'SELECT * FROM messages WHERE id = ?'
      conn = sqlite3.connect('database.db')
      c = conn.cursor()
      c.execute(matched_email_stmt, min(res))
      res = c.fetchone()
      c.close()
      print('Match found:', res)
      print('res removing id', res[2:]) #removes the id and the created date
      res_dict_vals = list(res[2:])
      res_dict_keys = ['date','subject','sender','content', 'has_attachment']
      dict_result = {}
      for k in res_dict_keys:
          for v in res_dict_vals:
              dict_result[k] = v
              res_dict_vals.remove(v)
              break
      print(dict_result)
      dict_result = json.dumps(dict_result)
      #requests.put(cb,data=json.dumps(dict_result), headers={'content-type': 'application/json'})
  #dummy request/immediate sendback instead of checking whether it is valid or n
  json_dict = json.dumps({ x[0] : x[1] for x in params.items()})
  print(json_dict, type(json_dict))
  requests.put(cb,data=json_dict, headers={'content-type': 'application/json'})
  
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
