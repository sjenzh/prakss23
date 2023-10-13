#/usr/bin/python3
#https://humberto.io/blog/sending-and-receiving-emails-with-python/
import email
from email import policy

import os 
import datetime
import imaplib
import re
import sqlite3
import requests
import json
import calendar

EMAIL = 'prakss23@gmail.com'
PASSWORD = 'flbycwtypcqgszjd'
SERVER = 'imap.gmail.com'

def drules(params, target, cur):
    res_ids = []
    cur.execute('SELECT id, '+ target + ' FROM rules')
    date_res = cur.fetchall() #date is a string so we need to convert it into a datetime object to compare
    for id, date in date_res:
        if date == None:
            res_ids.append(id)
        else:
            #TODO convert date(str) into datetime utc object 
            date = datetime.datetime.fromisoformat(date).astimezone(datetime.timezone.utc) 
            if target == 'date_after' and params['date'] > date:
                res_ids.append(id)
            elif target == 'date_before' and params['date'] < date:
                res_ids.append(id)
    return res_ids

def crules(params, target, cur):
    res_ids = []
    cur.execute('SELECT id, ' + target + ' FROM rules')
    regex_results = cur.fetchall()
    for id, pattern in regex_results:
        if pattern == None or re.search(pattern, params[target]):
              res_ids.append(id)
    return res_ids

def brules(params, target, cur):
    res_ids = []
    cur.execute('SELECT id, ' + target + ' FROM rules')
    bool_results = cur.fetchall()
    print(bool_results, type(bool_results))
    for id, boolean in bool_results:
      print(boolean, type(boolean), params[target], type(params[target]))
      if boolean == None or bool(boolean) == params[target]:
        res_ids.append(id)
    print(res_ids)
    return res_ids

def check(params):
    curdir = os.path.dirname(__file__)
    conn = sqlite3.connect(curdir + '/database.db')
    cur = conn.cursor()
    res_ids = [
       drules(params,'date_after', cur),
       drules(params,'date_before', cur),
       crules(params,'subject', cur),
       crules(params,'content', cur),
       crules(params,'sender', cur),
       brules(params, 'has_attachment', cur)
    ]
    conn.close()
    
    intersec = list(set(res_ids[0]) & set(res_ids[1]) & set(res_ids[2]) & set(res_ids[3]) & set(res_ids[4])& set(res_ids[5]))
    if len(intersec) > 0:
      resulting_id = min(intersec)
      curdir = os.path.dirname(__file__)
      conn = sqlite3.connect(curdir + '/database.db')
      c = conn.cursor()
      c.execute('SELECT callback FROM rules WHERE id = ?', (resulting_id,))
      cb_res = c.fetchone()
      c.execute('SELECT persistent FROM rules WHERE id = ?', (resulting_id,))
      is_persistent = c.fetchone()[0]
      
      dict_result = {
        'received_date': str(params['date']),
        'subject': params['subject'],
        'sender': params['sender'],
        'content': params['content'],
        'has_attachment': params['has_attachment']
      }

      dict_result = json.dumps(dict_result)
      if(cb_res!=None):
        requests.put(cb_res[0],data=dict_result, headers={'content-type': 'application/json', 'cpee-callback': 'true'})
        c.execute('DELETE FROM rules WHERE id = ?', (resulting_id,))
        conn.commit()
        #TODO what to do if rule is persistent?
        print('persistency', is_persistent)
        if (is_persistent):
          print('Rule was persistent. Saving e-mail into database')
          c.execute('INSERT INTO messages (received_date, subject, sender, content, has_attachment, mail_id) VALUES (?,?,?,?,?,?)', 
                (params['date'], params['subject'], params['sender'], params['content'], params['has_attachment'], params['mail_id']))
          conn.commit()
        conn.close()
        print('E-mail matched, rule is deleted from database')
    else:
      print('No match found, inserting e-mail into database')
      curdir = os.path.dirname(__file__)
      conn = sqlite3.connect(curdir + '/database.db')
      c = conn.cursor()
      c.execute('INSERT INTO messages (received_date, subject, sender, content, has_attachment, mail_id) VALUES (?,?,?,?,?,?)', 
                (params['date'], params['subject'], params['sender'], params['content'], params['has_attachment'], params['mail_id']))
      conn.commit()
      conn.close()

def convert_date(date):
  res= date[8:10]+'-'+calendar.month_name[int(date[5:7])][:3]+'-'+date[0:4]
  return res

def process_email(mail, mail_id):
    status, data = mail.fetch(mail_id, '(RFC822)')
    for response_part in data:
        if isinstance(response_part, tuple):
            message = email.message_from_bytes(response_part[1], policy=policy.HTTP)
            mail_has_attachment = any(True for _ in message.iter_attachments())
            mail_from = message['from'].addresses[0].username +'@'+ message['from'].addresses[0].domain
            mail_subject = str(message['subject'])
            mail_date = datetime.datetime.fromisoformat(message['date'].datetime.astimezone(datetime.timezone.utc).isoformat())
            
            if message.is_multipart():
                mail_content = ''
                for part in message.iter_parts():
                    if part.get_content_type() == 'text/plain':
                        mail_content += part.get_content()
            else:
                mail_content = message.get_payload()
            
            params = {
                'date': mail_date,
                'sender': mail_from,
                'subject': mail_subject, 
                'content': mail_content, 
                'has_attachment': mail_has_attachment,
                'mail_id': mail_id
            }
            check(params)


def main():
    mail = imaplib.IMAP4_SSL(SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')
    
    status, data = mail.search(None, '(UNSEEN)')    
    mail_ids = []
    
    for block in data:
        mail_ids += block.split()

    if len(mail_ids) == 0:
        print('No new emails')
    for mail_id in mail_ids:
       process_email(mail, mail_id)
    
    mail.logout()

if __name__ == '__main__':
    main()