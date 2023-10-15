# SS23 TUM Advanced Practical Course - Message Correlation and Inter-Instance/Process Communication in Process Aware Information Systems 

## Abstract
Coordination and communication in automated process-oriented systems are essential for their performance and efficiency in task execution. To be effective in its operations, a system must be capable of asynchronous reactions and interactions with various external systems and communication media. One widely adopted communication medium is electronic mail (e-mail), facilitating asynchronous information exchange. In the context of this TUM lab course, we have developed a custom e-mail message correlator synchronizing asynchronous communication between a cocktail robot, its users, and potential external systems. This report provides an overview of its implementation and functionality.

## Motivation
Message correlators play a crucial role in process aware information systems (PAIS), synchronizing inter- and intra-process communication and supporting process instance choreography scenarios. Their purpose is to address the challenges of coordinating asynchronous messages, ensuring they reach the right destination at the right time given the right conditions. With a message correlator, it is possible to align incoming and outgoing messages based on a set of predefined rules, offering a structured approach that contributes to security, maintainability, efficiency, and reliability of asynchronicity in PAIS.

## Correlator Functionality
Message correlators can differ in their implementation, but each correlator has to define its behavior regarding two different communication items: messages and requests. We list the tasks it has to fulfill for handling both:

1) Message Handling: How messages are managed when they arrive at the correlator.
    1) Message Reception: A correlator has to receive messages from arbitrary sources. What constitutes as a message (source, type) is defined by the correlator. 
    2) Message Analysis: The contents of the message need to be analyzed to extract relevant information for correlation.
    3) Message Forwarding / Matching:  After attempting to match with existing requests, the message needs to be forwarded. We distinguish variations in forwarding behavior as follows:
        1) The message is forwarded to a potential instance that is waiting for the message, or
        2) The message is stored for later use, or 
        3) A new instance of a process is created, with the message as input.
4) Request Handling: How correlation requests are managed when they arrive at the correlator.
    1) Request reception: Process instances may require messages from sources they cannot directly contact. They create a correlation request to ask for the required information from the correlator. The correlator needs to be able to receive these requests.
    2) Request Analysis: The correlation request has to be analyzed by its provided correlation rules to identify what information it requires the message to contain, the criteria the message needs to fulfill, and where it can be found.
    2) Request Forwarding / Matching: The correlator is responsible for finding the message that best correlates with the rule provided by the request. It must then forward the request by:
        1) Forwarding the message to the requesting instance, or 
        2) Storing the request when there is no match, or
        3) Defining different behavior for the request in case of no match or a match.

We will define how we implemented each of these in our custom e-mail correlator and elaborate an addition we made in its request and message handling in the following section.

## Implementation
We implemented our custom e-mail message correlator using Bottle, Python and JavaScript. A SQLite database is used for saving and fetching information.

Our correlator consists of two major Python files: corr.py and receive_email.py.
The corr.py creates the part of the correlator that handles incoming requests, whereas the receive_email.py file handles incoming messages.

The request handling is defined as follows: When we listen to process instances from our endpoint, we receive correlation requests. Its correlation rule is checked for its validity (see how a correlation rule is modeled in Figure XYZ) before it is accepted. Upon receiving a valid request, we fetch every message that is available from the database and attempt a match between the provided correlation rules and the existing messages. We can either find a match or none.
- When there is a match, we fetch the message from the database and send it to the callback URL. The message is deleted from the database and the request is dropped.
- When there is no match, we save our request with its correlation rules and their callback-URL in the database. It receives an ascending ID.

However, if we receive a request containing a rule that already is present within the database, we do not save it, but instead make the older rule entry peristent by changing its persistent value to true in the database. This changes the message rentention on a match, which is explained in the next section. 

We handle messages in a similar manner. Every full minute, our script fetches unread e-mails from the inbox of the e-mail 'prakss23@gmail.com'. When there is a unread, and therefore new e-mail, we initiate the message handling process:
The content of the e-mail is extracted based on the parts we modeled in Figure XYZ. We then fetch all requests from our database and check if the incoming message matches with any of the saved requests. 

## Models
As we chose e-mails as our message type, we chose a specific e-mail address' inbox as the source of our messages.
In our correlator, we modeled an e-mail message as follows:
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