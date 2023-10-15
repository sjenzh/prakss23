# SS23 TUM Advanced Practical Course - Message Correlation and Inter-Instance/Process Communication in Process Aware Information Systems 

## Abstract
Coordination and communication in automated process-oriented systems are essential for their performance and efficiency in task execution. To be effective in its operations, a system must be capable of asynchronous reactions and interactions with various external systems and communication media. One widely adopted communication medium is electronic mail (e-mail), facilitating asynchronous information exchange. In the context of this TUM lab course, we have developed a custom e-mail message correlator synchronizing asynchronous communication between a cocktail robot, its users, and potential external systems. This report provides an overview of its implementation and functionality.

## Motivation
Message correlators play a crucial role in process aware information systems (PAIS), synchronizing inter- and intra-process communication and supporting process instance choreography scenarios. Their purpose is to address the challenges of coordinating asynchronous messages, ensuring they reach the right destination at the right time given the right conditions. With a message correlator, it is possible to align incoming and outgoing messages based on a set of predefined rules, offering a structured approach that contributes to security, maintainability, efficiency, and reliability of asynchronicity in PAIS.

Message correlators can differ in their implementations, but each correlator has to comply with and consider certain points in order to execute its task:
- Message reception behavior
    - Message analysis
    - Target identification
- Data retention policy
Data flow/ action flow: The process engine will ask an external service for results, which will interact with the correlator.
A correlator has to react to an external event - it either starts a new process, or waits on an external message. when it waits, the source may be unknown, the source may send the message long before an instance needs the value; or the value may be sent after an instance needing the value. the contents of the message contain the key to decide what to do.

One specific issue that occurs when a message correlator Another important aspect of communication is repetition. When important information needs to be sent repetitively, it costs resources and time, making it a hassle to reformulate the exact same request repeatedly. In such scenarios, it is convenient to have a rule become persistent, allowing messages to apply multiple times due to their relevance for different endpoints. Our custom message correlator fulfills this criteria and offers the possibility for a rule to become persistent, thus making the message be stored for yet another incoming rule, as this message

Things that are important for correlation to work, and that have to be defined when implementing a custom correlator:
- Data retention policy: What happens to a message that is matched with a rule? Is it dropped, is it stored indefinitely/for a limited time, can it be replaced by existing messages?
- Message reception behavior: How does the correlator behave when there is a matching correlation rule(instantiate the process), when there is a matching correlation request(forward message or data retention), and when there is no match(data retention policy)? 

## What is correlation?
Patterns - Point of View:
• Ask for information: the process engine asks an external service for some results.
• React on some external event:
• A new process instance has to be started.
• Waiting for some external message.
• External source may be unknown.
• External source may send the message long before an instance is needing
the value.
• External source may send the value long after an instance is needing the value.
• The contents of a message contain the key to decide what to do

## How is correlation done?
A correlator has to receive messages from arbitray sources, and analyze the contents of the message. A message might be an e-mail received via IMAP, a word document received via HTML Form upload, or more generic: any fileformat submitted through any means/protocol. The message needs to be forwarded to a potential instance that is waiting for the message, or stored for later use or a new instance of a process, with the message as input is created.

A correlator requires a set of rules to analyse incoming messages, the message type, e.g. email, where to look in message, e.g. subject contains ticket number and lastly, what to do with the message: whether to forward it or instantiate.

## Message analysis
A correlator will support a set of sources: Mailbox, HTTP/REST file upload. A correlator will support a set of file types that can be analysed, e.g.
• A means to read and analyse the contents of a word file
• A means to read and analyse the contents of a excel file
• A means to read and analyse the contents of a CAD file

A correlator will support a rule language to describe how to extract correlation information, e.g.:
• A word files contanins the signature of a particular person at the end of
page 7, contains a ticket number in the form /#\w{12}/ on page 2, and has a
heading “Customer Contract” on page 1
• An excel sheet has three worksheets, and on the first worksheet cell A1
contains the identifier of the customer

## Target Identification
Processes that are to be instantiated have to contain correlation rules when to do so. The correlation rule poses a criteria where and which message contents to check for ...e.g.
• A word file contains the signature of a particular person at the end of page 7, contains a ticket number in the form /#\w{12}/ on page 2, and has a heading “Customer Contract” on page 1
• The rule is generic, any match leads to an instantiation
• The message is an input to the resulting process instance, see P2 on the left
• The correlator has to analyse each process model to extract the correlation rules

Instances that require certain message (but no direct means to contact a source) have to make a correlation request to get the required information from the correlator:
• I need a word files contanins the signature of John Boss at the end of page 7, contains a ticket number in the form #QWER12tzui34 on page 2, and has a heading “Customer
Contract” on page 1
• The request is very special, this one particular message matches
• The correlator can store a list of requests on the fly, and delete entries whenever a request has fullfilled

## Message Received
A matching correlation rule exists:
• instantiate process
A matching correlation request exists:
• forward message
• Data Retention
No matches exists:
• Data Retention

## Data Retention
A message that instantiates a process: drop message after instantiation
A message that matches a correlation request - a retention policy has to exist:
• No policy: drop the message after forward
• Store indefinitely
• Other requests can be answered
• Store for a limited time
• Other requests can be answered
• Additional parameters have to be fulfilled in order to reuse the message to fulfill request
• E.g. a requestor has to submit a code to get the info
• Queue vs. Slot
• Slot - Messages can replace other existing messages - only the newest message fitting a correlation request is stored
• Queue - All messages are stored - the newest message fitting a correlation request is
delivered

## What do correlators contribute to?
Security: correlators connect external systems to internal process instances without exposing the internal structure.
Loose Coupling: external systems have a single point where to send information.
Policy Enforcing: how to deal with message retention - loose coupling & maintainability.
Compliance Checking: incoming data can be checked before it enters internal infrastructure
Maintainabilty: single place to deal with incoming messages. No need to implement anything in the engine.
The alternative would be much more complicated and relying on tighly coupled system.

## Implementation //How
We implemented our custom e-mail message correlator using Bottle for our server-side functions, creating the frontend using the .tpl format offered by Bottle and JavaScript. A SQLite database is used for saving and fetching information.

The files are structured in the directory prakss23 as follows:
- | /_| view
-     |- make_queues.tpl
- | corr.py
- receive_email.py
- init_db.py
- database.db
- email_schema.sql
- rule_schema.sql

Our correlator consists of two major Python files:
corr.py and receive_email.py. [TODO]
The corr.py creates a part of the correlator that 

We modeled an e-mail message for our custom message correlator as follows:
[TODO: UML]
As depicted in Figure XYZ, an e-mail message has a sender, a subject, a date when it is received, a content field, as well as a boolean indicator of whether it has attachments or not.

To model a rule, we gave it properties with which the correlator can match the e-mail with the given rules. We distinguish the different attributes based on their rule category:
Regular Expression rule:
- sender
- subject
- content
ISO 8601 rule:
- date_before
- date_after
Boolean rule:
- has_attachment
The regular expression sent to the correlator will then be matched to the 

- choreography scenarios
- inter/intra-process synchronization
- correlation patterns, dealing with data retention.

### Architecture
The correlator works by running the corr.py file, which serves as a connection to the CPEE-Engine. [TODO mention it in the beginning?] The file also serves the frontend and offers on an initial database boot the following interface:
Two empty tables with their respective columns modeling the email and rules.
The corr.py file will listen on the endpoint https://lehre.bpm.in.tum.de/21047/get_matching_message for a CPEE process instance's request.
Once a process instance sends a request, the file will
[TODO persistency]

#### Data Flow

## Future Work
As our e-mail model does not include every single attribute that is possible to consider, there are extensions that can be done on that end. It would be possible to extend the implementation to include the type of the file attachment, as well as its contents or meta information.
We also envision possibilities in the area of data retention, where
## Notes/References
- E-mail SEARCH criteria  keywords and what params it expects: https://datatracker.ietf.org/doc/html/rfc3501#section-6.4.4 
- email (https://docs.python.org/3.8/library/email.html) python lib covers: RFC5322, RFC6532, RFC2045,RFC2046,RFC2047,RFC2183,RFC2231; 
- the content data at the '(RFC822)' format comes on a list with a tuple with header, content, and the closing byte b')'

# message_from_bytes with no specific policy defaults to https://docs.python.org/3/library/email.policy.html#email.policy.Compat32, limiting the amount of retrieval methods. Now converted to EmailMessage object. select & specify policy here: https://docs.python.org/3.8/library/email.policy.html
can be in plain text or multipart, if its not plain text we need to separate the message from its annexes to get the text
on multipart we have the text message and other things like annex, and html version of the message, in that case we loop through the email payload
if the content type is text/plain #TODO what other content types are there to consider? we extract it
if the message isn't multipart, just extract it


https://campus.tum.de/tumonline/ee/ui/ca2/app/desktop/#/slc.tm.cp/student/courses/950691568?$ctx=design=ca;lang=de&$scrollTo=toc_overview

#https://humberto.io/blog/sending-and-receiving-emails-with-python/