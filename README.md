# prakss23
SS23 TUM Praktikum

Notes/References
- E-mail SEARCH criteria  keywords and what params it expects: https://datatracker.ietf.org/doc/html/rfc3501#section-6.4.4 
- email (https://docs.python.org/3.8/library/email.html) python lib covers: RFC5322, RFC6532, RFC2045,RFC2046,RFC2047,RFC2183,RFC2231; 
- the content data at the '(RFC822)' format comes on a list with a tuple with header, content, and the closing byte b')'

# message_from_bytes with no specific policy defaults to https://docs.python.org/3/library/email.policy.html#email.policy.Compat32, limiting the amount of retrieval methods. Now converted to EmailMessage object. select & specify policy here: https://docs.python.org/3.8/library/email.policy.html
can be in plain text or multipart, if its not plain text we need to separate the message from its annexes to get the text
on multipart we have the text message and other things like annex, and html version of the message, in that case we loop through the email payload
if the content type is text/plain #TODO what other content types are there to consider? we extract it
if the message isn't multipart, just extract it
