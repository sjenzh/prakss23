#https://humberto.io/blog/sending-and-receiving-emails-with-python/
import email
from email import policy
import datetime, imaplib, sqlite3, re, requests, json
import calendar
from dateutil import parser

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

def check(params):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    res_ids = []
    res_ids.append(drules(params,'date_after', cur))
    res_ids.append(drules(params,'date_before', cur))
    res_ids.append(crules(params,'subject', cur))
    res_ids.append(crules(params,'content', cur))
    res_ids.append(crules(params,'sender', cur))
    intersec = list(set(res_ids[0]) & set(res_ids[1]) & set(res_ids[2]) & set(res_ids[3]) & set(res_ids[4]))
    conn.close()
    if len(intersec) > 0:
        resulting_id = min(intersec)
        #TEST select statement using resulting_id and using the callback to perform a PUT request
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT callback FROM rules WHERE id = ?', (resulting_id,))
        cb_res = c.fetchone()
        
        dict_result = {}
        dict_result['received_date'] = str(params['date'])
        dict_result['subject'] = params['subject']
        dict_result['sender'] = params['sender']
        dict_result['content'] = params['content']
        dict_result['has_attachment'] = params['has_attachment']
        dict_result = json.dumps(dict_result)
        requests.put(cb_res[0],data=dict_result, headers={'content-type': 'application/json', 'cpee-callback': 'true'})
        c.execute('DELETE FROM rules WHERE id = ?', (resulting_id,))
        conn.commit()
        conn.close()
        print('E-mail matched, rule is deleted from database')
    else:
        #TEST no match: e-mail needs to be saved into the DB
        print('No match found, inserting e-mail into database')
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO messages (received_date, subject, sender, content, has_attachment, mail_id) VALUES (?,?,?,?,?,?)', 
                  (params['date'], params['subject'], params['sender'], params['content'], params['has_attachment'], params['mail_id']))
        conn.commit()
        conn.close()

def convert_date(date):
    res= date[8:10]+'-'+calendar.month_name[int(date[5:7])][:3]+'-'+date[0:4]
    return res

mail = imaplib.IMAP4_SSL(SERVER)
mail.login(EMAIL, PASSWORD)
mail.select('inbox')

conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('SELECT received_date, mail_id FROM messages WHERE id = (SELECT MAX(id) FROM messages)')
date_id = c.fetchone()
conn.close()
if date_id == None:
    status, data = mail.search(None, 'ALL')
else:
    result = convert_date(date_id[0])
    status, data = mail.search(None, 'SENTSINCE '+result)

mail_ids = []

for block in data:
    mail_ids += block.split()
    if date_id != None: 
       i = mail_ids.index(bytes(date_id[1]),0,len(mail_ids))
       if i+1 >= len(mail_ids):
            print('No new emails')
            mail_ids=[]
            break #stop when there are no new e-mails
       else:
            mail_ids = mail_ids[(i+1):]

for id in mail_ids:
    status, data = mail.fetch(id, '(RFC822)')
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

            params = {'date': mail_date,
                      'sender': mail_from,
                      'subject': mail_subject, 
                      'content': mail_content, 
                      'has_attachment': mail_has_attachment,
                      'mail_id': id}
            check(params)
