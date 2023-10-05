#https://humberto.io/blog/sending-and-receiving-emails-with-python/
import email
from email import policy
import datetime, imaplib, sqlite3, re, requests, json
import calendar

EMAIL = 'prakss23@gmail.com'
PASSWORD = 'flbycwtypcqgszjd'
SERVER = 'imap.gmail.com'

def drules(params, target, cur):
    res_ids = []
    cur.execute('SELECT id, '+ target + ' FROM rules')
    date_res = cur.fetchall()
    res_ids.append([])
    for id, date in date_res:
        if date == None:
            res_ids.append(id)
        elif target == 'date_after' and params['date'] > date:
            res_ids.append(id)
            print('paramsdate', type(params['date']), 'date', type(date))
        elif target == 'date_before' and params['date'] < date:
            print('paramsdate', type(params['date']), 'date', type(date))
            res_ids.append(id)
    return res_ids

def crules(params,target, cur):
    res_ids = []
    cur.execute('SELECT id, ' + target + ' FROM rules')
    regex_results = cur.fetchall()
    res_ids.append([])
    for id, pattern in regex_results:
        if re.search(pattern, params[target]) or pattern == None:
              res_ids.append(id)
    return res_ids


def check(params):
    # checks if inc. e-mail fits any of the rules in the database.
    # if null, it automatically applies
    date_after_stmt = 'SELECT id, subject, sender, content FROM rules WHERE date_after < ? AND date_after IS NOT NULL'
    date_after_none_stmt = 'SELECT id FROM rules WHERE date_after IS NULL'
    date_after_union_stmt = date_after_stmt + ' UNION ' + date_after_none_stmt
    date_before_stmt = 'SELECT id, subject, sender, content FROM rules WHERE date_before > ? AND date_before IS NOT NULL'
    date_before_none_stmt = 'SELECT id FROM rules WHERE date_before IS NULL'
    date_before_union_stmt = date_before_stmt + ' UNION ' + date_before_none_stmt
    regex_stmt = 'SELECT A.id, A.subject, A.sender, A.content FROM ('+date_after_union_stmt + ') AS A INNER JOIN (' + date_before_union_stmt + ') AS B ON A.id = B.id'

    # TODO rewrite everything
    # date_sql_stmt = 'SELECT id FROM rules WHERE date_after < ? AND date_before > ? UNION SELECT id from rules WHERE date_after IS NULL OR WHERE date_before IS NULL'
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    # cur.execute(date_after_stmt, params['date'])
    res_ids = []

    res_ids.append(drules(params,'date_after', cur))
    res_ids.append(drules(params,'date_before', cur))
    res_ids.append(crules(params,'subject', cur))
    res_ids.append(crules(params,'content', cur))
    res_ids.append(crules(params,'sender', cur))
    intersec = list(set(res_ids[0]) & set(res_ids[1]) & set(res_ids[2]) & set(res_ids[3]) & set(res_ids[4]))

    if len(intersec) > 0:
      id = intersec[0]

    # if re.search(subject_pattern, params['subject']) or subject_pattern == None:
    #     print(f"Pattern '{subject_pattern}' matches the target string.")
    #     if re.search(sender_pattern, params['sender']) or sender_pattern == None:
    #         print(f"Pattern '{sender_pattern}' matches the target string.")
    #         if re.search(content_pattern, params['content']) or content_pattern == None:
    #             res_ids.append(id)
    #             print(f"Pattern '{content_pattern}' matches the target string.")


    cur.execute(regex_stmt)
    regex_results = cur.fetchall()

    #Regex match
    for id, subject_pattern, sender_pattern, content_pattern in regex_results:
        if re.search(subject_pattern, params['subject']) or subject_pattern == None:
            print(f"Pattern '{subject_pattern}' matches the target string.")
            if re.search(sender_pattern, params['sender']) or sender_pattern == None:
                print(f"Pattern '{sender_pattern}' matches the target string.")
                if re.search(content_pattern, params['content']) or content_pattern == None:
                    res_ids.append(id)
                    print(f"Pattern '{content_pattern}' matches the target string.")
    
    conn.close()
    #TODO: TESTING minimize if available, return nothing if there is none
    if len(res_ids) >0:
        resulting_id = min(res_ids)
        #TEST select statement using resulting_id and using the callback to perform a PUT request
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT callback FROM rules WHERE id = ?', resulting_id)
        cb_res = c.fetchone()
        c.close()
        dict_result = {}
        dict_result['received_date'] = params['date']
        dict_result['subject'] = params['subject']
        dict_result['sender'] = params['sender']
        dict_result['content'] = params['content']
        dict_result['has_attachment'] = params['has_attachment']
        dict_result = json.dumps(dict_result)
        requests.put(cb_res,data=dict_result, headers={'content-type': 'application/json'})
        #TODO remove e-mail and rule from database
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
    # b'1 2 3'.split() => [b'1', b'2', b'3']
    mail_ids += block.split()
    print("Current Mail IDs: ")
    print(mail_ids, type(mail_ids))
    if date_id != None: 
       i = mail_ids.index(bytes(date_id[1]),0,len(mail_ids))
       if i+1 >= len(mail_ids):
            break #stop when there are no new e-mails
       else:
            print(mail_ids[i:]) #pass last id to indexing operation -> cut off from last id TODO: filtering   
            mail_ids = mail_ids[(i+1):]

for id in mail_ids:
    status, data = mail.fetch(id, '(RFC822)')
    for response_part in data:
        if isinstance(response_part, tuple):
            message = email.message_from_bytes(response_part[1], policy=policy.HTTP)
            mail_has_attachment = any(True for _ in message.iter_attachments())
            # num_of_attachment = sum(1 for _ in message.iter_attachments()) if mail_has_attachment else 0
            mail_from = message['from']
            mail_subject = message['subject']
            mail_date = message['date']

            if message.is_multipart():
                mail_content = ''
                for part in message.iter_parts():
                    if part.get_content_type() == 'text/plain':
                        mail_content += part.get_content()
            else:
                mail_content = message.get_payload()

            params = {'date': mail_date.datetime.astimezone(datetime.timezone.utc).isoformat(),
                      'sender': mail_from,
                      'subject': mail_subject, 
                      'content': mail_content, 
                      'has_attachment': mail_has_attachment,
                      'mail_id': id}
            check(params)
            # print(f'From: {mail_from}')
            # print(f'Subject: {mail_subject}')
            # print(f'Date: {mail_date}')
            # print(f'DateTimeDate: {mail_date.datetime}')
            # print(f'iso8601-format: {datetime.datetime.fromisoformat(str(mail_date.datetime))}')
            # print(f'isoformatunified timezone:', mail_date.datetime.astimezone(datetime.timezone.utc).isoformat())
            # print('localized time:', '2023-10-03T17:16:33+00:00'< mail_date.datetime.astimezone(datetime.timezone.utc).isoformat())
            # print(f'E-mail has attachments: {mail_has_attachment}')
            # print(f'Content: {mail_content}')