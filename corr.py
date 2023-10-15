#!/usr/bin/python3
import datetime
import json
import os
import requests
import re
import sqlite3

from pathlib import Path
from threading import Thread
from bottle import (
    request,
    response, 
    route, 
    run, 
    template, 
    TEMPLATE_PATH
)

TEMPLATE_PATH.append(str(Path('prakss23')/ 'views'))

def set_persistence(ids):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    query = 'UPDATE rules SET persistent = 1 WHERE id = ?'
    for id in ids:    
        cur.execute(query, id)        
    conn.commit()
    conn.close()
    
def is_persistent(params):
    values = list(params.values())
    columns = list(params.keys())
    query = f'SELECT id FROM rules WHERE '+ ' AND '.join([f'{key} = ?' for key in columns])
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute(query, values)
    req_ids = cur.fetchall()
    conn.close()

    if len(req_ids) > 0:
        set_persistence(req_ids)
        return True
    else:
        return False

def convert_iso_str_to_utc_datetime (str_date):
    return datetime.datetime.fromisoformat(str_date).astimezone(datetime.timezone.utc)

def check(cb,params):
    if not is_persistent(params):
        query = ''
        query_params = []
        rule_columns = []
        for (key,value) in params.items():
            if len(value) != 0: #field is not empty
                rule_columns.append(key)
                if key in ['subject', 'content', 'sender']:#regex
                    query = query + key + ' REGEXP \"' + value + '\" AND '
                elif key == 'before': #datetime 
                    query = query + 'received_date < ? AND '
                    query_params.append(convert_iso_str_to_utc_datetime(value))
                elif key=='after': #datetime
                    query = query + 'received_date > ? AND '
                    query_params.append(convert_iso_str_to_utc_datetime(value))
                elif key=='has_attachment': #bool
                    query = query + 'has_attachment = '+str(bool(value))+' AND '
        if len(query)>1:
            query = query[:-5] #removes last AND
        final_sql_query = 'SELECT id FROM messages WHERE '+query

        conn = sqlite3.connect('database.db')
        conn.enable_load_extension(True)
        cur = conn.cursor()
        cur.execute('SELECT load_extension("/usr/lib/sqlite3/pcre.so")')
        cur.execute(final_sql_query, query_params)
        res = cur.fetchall()
        conn.close()

        if len(res) == 0:
            rule_columns.append('callback')
            rule_values = list(params.values())
            rule_values.append(cb)
            rule_values = [x for x in rule_values if x != '']
            for x in rule_columns:
                if x == 'after':
                    rule_columns[rule_columns.index(x)] = 'date_after'
                elif x == 'before':
                    rule_columns[rule_columns.index(x)] = 'date_before'
            placeholders = ', '.join(['?'] * len(rule_values))
            insert_into_stmt = f'INSERT INTO rules ({", ".join(rule_columns)}) VALUES ({placeholders})'
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            cur.execute(insert_into_stmt, rule_values)
            conn.commit()
            conn.close()
            print('No matches found, adding rule to database')
        else:
            matched_email_query = 'SELECT * FROM messages WHERE id = ?'
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            to_delete = min(res)
            cur.execute(matched_email_query, to_delete)
            result = cur.fetchone()
            print('Match found:', result)

            res_dict_vals = list(result[1:]) #removes the id
            res_dict_keys = ['date','subject','sender','content', 'has_attachment']

            dict_result = {}
            for key, value in zip(res_dict_keys, res_dict_vals):
                dict_result[key] = value
            result = json.dumps(dict_result)
            requests.put(cb,data=result, headers={'content-type': 'application/json'})
            
            cur.execute('DELETE FROM messages WHERE id = ?', to_delete)
            conn.commit()
            conn.close()

def check_is_date(date):
    try:
        datetime.datetime.fromisoformat(date)
        return True
    except Exception as e:
        print('The given input was not a valid date according to ISO 8601.')
        print(f'{e}')
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
    for key, value in params.items():
        if value != '':
            if key in ['subject', 'content', 'sender']:
                if not check_is_regex(value):
                    return False
            elif key in ['after', 'before']:
                if not check_is_date(value): 
                    return False
            elif key == 'has_attachment':
                if not check_is_bool(value):
                    return False
            else:
                print(key+ 'is an invalid key. Please provide only one of the following keys: after, before, subject, sender, content, has_attachment')
                return False
        else:
            if key not in ('subject','content','sender','after','before','has_attachment'):
                print(key + 'is an invalid key. Please provide only one of the following keys: after, before, subject, sender, content, has_attachment')
                return False
    return True

@route('/')
def index():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT id, sender, subject, date_after, date_before, has_attachment, content, persistent FROM rules')
    rules_res = cur.fetchall()
    cur.execute('SELECT id, sender, subject, received_date, has_attachment, content FROM messages')
    messages_res = cur.fetchall()
    conn.close()
    output = template('make_queues', {'rules': rules_res, 'messages': messages_res})
    return output

@route('/toggle_persistence', method='POST')
def togglePersistence():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('UPDATE rules SET persistent = ? WHERE id = ?', list(request.json.values()))
    conn.commit()
    conn.close()
    response.headers.content_type =  'text/plain; charset=UTF-8'
    response.status = 200
    response.body = ''
    return response

@route('/get_matching_message')
def match_message():
    if not valid_input(request.params):
        response.headers.content_type = 'text/plain; charset=UTF-8'
        response.headers['CPEE-CALLBACK'] = 'false'
        response.status = 400
        response.body = 'Please check that your input complies with the provided format: subject, sender, content: regex, after, before: iso8601 compliant date, has_attachment: boolean'
        return response
    else:
        response.headers.content_type =  'text/plain; charset=UTF-8'
        response.headers['CPEE-CALLBACK'] = 'true'
        response.status = 200
        response.body = ''
        thread = Thread(target=check, args= [request.headers['Cpee-Callback'], request.params])
        thread.start()
        return response

port = int(os.environ.get('PORT', 20147))
run(host='::1', port=port, debug=True)
