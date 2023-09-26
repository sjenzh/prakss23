#receiving e-mail app: to receive them, we use IMAP (RFC 3501) or POP (RFCs 918 e 1081) protocols.
#https://humberto.io/blog/sending-and-receiving-emails-with-python/
import email
import imaplib
import base64
import sqlite3

EMAIL = 'prakss23@gmail.com'
PASSWORD = 'flbycwtypcqgszjd'
SERVER = 'imap.gmail.com'

# connect to the server and go to its inbox

mail = imaplib.IMAP4_SSL(SERVER)

mail.login(EMAIL, PASSWORD)

# we choose the inbox but you can select others

mail.select('inbox')

# we'll search using the ALL criteria to retrieve

# every message inside the inbox

# it will return with its status and a list of ids

status, data = mail.search(None, 'ALL')

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



# now for every id we'll fetch the email

# to extract its content

for i in mail_ids:

    # the fetch function fetch the email given its id

    # and format that you want the message to be

    status, data = mail.fetch(i, '(RFC822)')



    # the content data at the '(RFC822)' format comes on

    # a list with a tuple with header, content, and the closing

    # byte b')'

    for response_part in data:

        # so if its a tuple...

        if isinstance(response_part, tuple):

            # we go for the content at its second element

            # skipping the header at the first and the closing

            # at the third

            message = email.message_from_bytes(response_part[1])



            # with the content we can extract the info about

            # who sent the message and its subject

            print('Details, Message:')
            # print(message['content-transfer-encoding'])

            mail_from = message['from']

            mail_subject = message['subject']
            
            mail_date = message['date']

            mail_attachment = message['attachment']


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


            # and then let's show its result

            # print(f'From: {mail_from}')

            # print(f'Subject: {mail_subject}')

            # print(f'Date: {mail_date}')
            # print(f'ShortDate: {mail_date[5:25]}')
            # print(f'DateType: {type(mail_date)}')

            # print(f'Attachment: {mail_attachment}')

            content = mail_content
            # print(f'Content: {mail_content}')
            if (message['content-transfer-encoding'] == None): #only decode when there is base64 encoding... in case of google mail, the encoding isn't given/kept as None
                decoded_content = base64.b64decode(mail_content)
                print(f'Decoded: {decoded_content}')
                content = decoded_content
            else:
                print(f'Content: {mail_content}')

            #save email in database
            # conn = sqlite3.connect('database.db')
            # cur = conn.cursor()
            # cur.execute("INSERT INTO messages (title, content) VALUES (?, ?)", (mail_subject, content))
            # conn.commit()
            # conn.close()