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
   c.execute('SELECT subject FROM rules')
   rules_res = c.fetchall()
   c.execute('SELECT subject FROM messages')
   messages_res = c.fetchall()
   c.close()
   output = template('make_queues', {'rules':rules_res, 'messages':messages_res})
   return output

def check(cb,params):
  print(cb)
  print(params)
  stmt = ""
  stmt_params = []
  rule_columns = []
  for (k,v) in params.items():
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
  sql = "SELECT id FROM messages WHERE "+stmt
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
      insert_into_stmt = f'INSERT INTO rules ({", ".join(rule_columns)}) VALUES ({placeholders})'
      conn = sqlite3.connect('database.db')
      c = conn.cursor()
      c.execute(insert_into_stmt, rule_values)
      conn.commit()
      conn.close()
      print('No matches found, adding rule to database')
  else:
      matched_email_stmt = 'SELECT * FROM messages WHERE id = ?'
      conn = sqlite3.connect('database.db')
      c = conn.cursor()
      to_delete = min(res)
      c.execute(matched_email_stmt, to_delete)
      res = c.fetchone()
      print('Match found:', res)
      print('res removing id', res[2:]) #removes the id and the mail_id
      res_dict_vals = list(res[2:])
      res_dict_keys = ['date','subject','sender','content', 'has_attachment']
      dict_result = {}
      for k, v in zip(res_dict_keys, res_dict_vals):
          dict_result[k] = v
      result = json.dumps(dict_result)
      requests.put(cb,data=result, headers={'content-type': 'application/json'})
      c.execute('DELETE FROM messages WHERE id = ?', to_delete)
      conn.commit()
      conn.close()

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
