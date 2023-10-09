#!/usr/bin/python3
import os, requests, re
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
   c.execute('SELECT id,subject,persistent FROM rules')
   rules_res = c.fetchall()
   c.execute('SELECT id,subject FROM messages')
   messages_res = c.fetchall()
   conn.close()
   output = template('make_queues', {'rules':rules_res, 'messages':messages_res})
   return output

@route('/toggle_persistence', method='POST')
def togglePersistency():
    print('request.json', request.json, type(request.json))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    print(request.json.values(), type(request.json.values()))
    c.execute('UPDATE rules SET persistent = ? WHERE id = ?',list(request.json.values()))
    conn.commit()
    conn.close()
    response.body = ''
    response.status = 200
    response.headers.content_type =  'text/plain; charset=UTF-8'
    return response

def is_persistent(params):
  #TODO: check if rule already exists as such in database. if yes, set persistent to 1,
  # if no, set persistent to 0/continue operation as intended
  values = list(params.values())
  columns = list(params.keys())
  placeholders = ', '.join(['?'] * len(values))
  print(type(values), 'values',values, type(columns), 'columns', columns)
  sql_stmt = f'SELECT id FROM rules WHERE '
  sql_stmt += " AND ".join([f"{key} = ?" for key in columns])
  conn = sqlite3.connect('database.db')
  c = conn.cursor()
  c.execute(sql_stmt, values)
  req_ids = c.fetchall()
  conn.close()
  print(type(req_ids), 'req_ids')
  if len(req_ids) > 0:
    for id in req_ids:
      conn = sqlite3.connect('database.db')
      c = conn.cursor()
      stmt = 'UPDATE rules SET persistent = 1 WHERE id = ?'
      c.execute(stmt, id)
      conn.commit()
      conn.close()
      print('Duplicate, alter old rule to persistent')
    return True
  else:
    print('no dupe, proceeding to process rule')
    return False
def check(cb,params):
  print(cb)
  print(params)
  if not is_persistent(params):
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
    conn.close()
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

def check_is_date(date):
    try:
        datetime.datetime.fromisoformat(date)
        return True
    except:
        print('The given input was not a valid date according to ISO 8601.')
        #TODO: fetch detailed error message
        return False

def check_is_regex(pattern):
    try:
        re.compile(pattern)
        return True
    except re.error:
        print('The given input was not a regex.')
        return False

def check_is_bool(input):
    return input == 0 or input or isinstance(input, bool)

def valid_input(params):
    print('in validity check', type(params), params, params.items(), params.keys(), params.values())
    for k,v in params.items():
        if v != '':
            if k == 'subject' or k == 'content' or k == 'sender':
                print('perform regex check', v)
                if not check_is_regex(v):
                    return False
                print(check_is_regex(v))
            elif k == 'after' or k == 'before':
                print('perform date iso check',v)
                if not check_is_date(v): 
                    return False
                print(check_is_date(v))
            elif k == 'has_attachment':
                print('perform bool check',v)
                if not check_is_bool(v):
                    return False
                print(check_is_bool(v))
            else:
                print('throw exception for wrong keys')
                return False
        else:
            if k not in ('subject','content','sender','after','before','has_attachment'):
                print('throw exception for wrong keys')
                return False
    return True

@route('/get_matching_message')
def index():
    print(request.params,request.params.items())
    if not valid_input(request.params):
        print(request.params.values(), type(request.params.values))
        response.status = 400
        response.headers.content_type = 'text/plain; charset=UTF-8'
        response.headers['cpee-callback'] = 'false'
        response.body = 'Please check that your input complies with the provided format: TODO lorem ipsum...'
        return response
    else: #send back 400 and cpee-callback false
        response.headers.content_type =  'text/plain; charset=UTF-8'
        response.headers['CPEE-CALLBACK'] = 'true'
        response.status = 200
        response.body = ''
        thread = Thread(target=check, args=[request.headers['Cpee-Callback'],request.params])
        thread.start()
        return response

port = int(os.environ.get('PORT', 20147))
run(host='::1', port=port, debug=True)
