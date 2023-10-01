#receiving e-mail app: to receive them, we use IMAP (RFC 3501) or POP (RFCs 918 e 1081) protocols.
#https://humberto.io/blog/sending-and-receiving-emails-with-python/
import email #python email package https://docs.python.org/3.8/library/email.html
from email import policy
from email import headerregistry
import imaplib
import base64
import sqlite3
import datetime

#TODO encoding
ENCODING = None

#email python lib covers: RFC5322, RFC6532, RFC2045,RFC2046,RFC2047,RFC2183,RFC2231
EMAIL = 'prakss23@gmail.com'
PASSWORD = 'flbycwtypcqgszjd'
SERVER = 'imap.gmail.com'

# server connection, inbox selection
mail = imaplib.IMAP4_SSL(SERVER)
mail.login(EMAIL, PASSWORD)
mail.select('inbox')

# search criteria keywords and what params it expects: https://datatracker.ietf.org/doc/html/rfc3501#section-6.4.4 
recent_date = "1-Sep-2023"
status, data = mail.search(None, "SENTSINCE "+recent_date)
# status, data = mail.search(None, 'ALL') #can be used for matching TODO

# the list returned is a list of bytes separated
# by white spaces on this format: [b'1 2 3', b'4 5 6']
# so, to separate it first we create an empty list

mail_ids = []

# then we go through the list splitting its blocks
# of bytes and appending to the mail_ids list

for block in data:

    # the split function called without parameter
    # transforms the text or bytes into a list using
    # as separator the white spaces:

    # b'1 2 3'.split() => [b'1', b'2', b'3']
    mail_ids += block.split()
    print("Current Mail IDs: ")
    print(mail_ids, type(mail_ids))
    # i = mail_ids.index(b'6',0,len(mail_ids))
    # print(mail_ids[i:]) #pass last id to indexing operation -> cut off from last id TODO: filtering
    # mail_ids = mail_ids[i:]


# now for every id we'll fetch the email to extract its content

for i in mail_ids:

    # the fetch function fetch the email given its id
    # and format that you want the message to be

    status, data = mail.fetch(i, '(RFC822)')

    # the content data at the '(RFC822)' format comes on
    # a list with a tuple with header, content, and the closing byte b')'

    for response_part in data:

        # so if its a tuple...

        if isinstance(response_part, tuple):

            # we go for the content at its second element
            # skipping the header at the first and the closing
            # at the third

            # message_from_bytes with no specific policy defaults to https://docs.python.org/3/library/email.policy.html#email.policy.Compat32,
            # limiting the amount of retrieval methods. Now converted to EmailMessage object.
            # select & specify policy here: https://docs.python.org/3.8/library/email.policy.html
            message = email.message_from_bytes(response_part[1], policy=policy.HTTP)

            # information extraction using parsed content
            print('Details, Message:',type(message))
            print(message)

            # print('get_unixfrom()', message.getunixfrom()) # only possible with email.message, not email.message.EmailMessage
            print('is_multipart()', message.is_multipart())
            # print('len', len(message))
            # print('keys()', message.keys())
            # print('values()', message.values())
            # print('items()', message.items())
            # print('is_attachemnt()', message.is_attachment())
            # print('get_content_disposition()', message.get_content_disposition())
            # print('contains?')
            # print('walk() and printing is_attachment()')
            # for part in message.walk():
            #     print(part.get_content_type(), part.is_attachment(), part.get_content_disposition if part.is_attachment() else "None")
            
            #TODO prelim email decoding method; see https://stackoverflow.com/questions/27037816/can-an-email-header-have-different-character-encoding-than-the-body-of-the-email

            mail_has_attachment = any(True for _ in message.iter_attachments())
            num_of_attachment = sum(1 for _ in message.iter_attachments()) if mail_has_attachment else 0

            # print('iter_attachments()', message.iter_attachments()) <- similar for inline possible?
            for x in message.iter_attachments():
                print('full',x)
                print('content-disposition', x['content-disposition'])
                print(x.get_filename()) #fetches fileName/attachmentName TODO: return as list and append to previous filenames, TODO: check for inline distinction
                print('get_content_disposition()', x.get_content_disposition())
                print('content-transfer-encoding', x['content-transfer-encoding'])
                ENCODING = x['content-transfer-encoding'] if x['content-transfer-encoding'] != None else None
            mail_from = message['from']
            mail_subject = message['subject']
            mail_date = message['date']

            # then for the text we have a little more work to do
            # because it can be in plain text or multipart
            # if its not plain text we need to separate the message
            # from its annexes to get the text

            if message.is_multipart():

                mail_content = ''

                # on multipart we have the text message and
                # another things like annex, and html version
                # of the message, in that case we loop through
                # the email payload

                for part in message.get_payload():

                    # if the content type is text/plain

                    # we extract it

                    if part.get_content_type() == 'text/plain':

                        mail_content += part.get_payload()

            else:

                # if the message isn't multipart, just extract it

                mail_content = message.get_payload()


            # no match possible
            no_match = True
            # and then let's show its result

            print(f'From: {mail_from}')
            print(f'Subject: {mail_subject}')
            print(f'Date: {mail_date}')
            print(f'Converted Date: {mail_date[5:25].replace(" ", "-")}')
            print(f'DateType: {type(mail_date)}')
            print(f'E-mail has attachments: {mail_has_attachment}')
            print(f'Number of attachments: {num_of_attachment}')
            

            content = mail_content
            # only decode when base64 encoding, datatype: https://docs.python.org/3/library/email.headerregistry.html
            if (ENCODING.cte == 'base64' if isinstance(ENCODING,headerregistry.ContentTransferEncodingHeader) else False):
                decoded_content = base64.b64decode(mail_content).decode('utf-8')
                print(f'Decoded Content: {decoded_content}')
                content = decoded_content
            else:
                print(f'Content: {mail_content}')

            #save email in database only if email not matched + not in db already
            # if(no_match):
            # conn = sqlite3.connect('database.db')
            # cur = conn.cursor()
            # cur.execute("INSERT INTO messages (title, content) VALUES (?, ?)", (mail_subject, content))
            # conn.commit()
            # conn.close()
            # def start(EMAIL, PASSWORD,SERVER):
            #     mail = imaplib.IMAP4_SSL(SERVER)
            #     mail.login(EMAIL, PASSWORD)
            #     mail.select('inbox')
            #     status, data = mail.search(None, 'SENTSINCE'+recent_date)