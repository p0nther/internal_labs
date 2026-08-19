---

XXE (XML External Entity) - Complete Notes
When many bug bounty hunters first encounter XXE (XML External Entity Injection), they immediately start memorizing payloads. However, without understanding how XML actually works, XXE often feels like magic.
In this article, we'll build the foundation first:
What XML is

What DTDs are

What entities are

How XML parsers process data

How XXE vulnerabilities happen

How attackers escalate XXE into SSRF and Blind XXE

How developers can prevent it

---

What Is XML?
XML stands for eXtensible Markup Language.
It is a markup language designed to store and transport structured data.
Many beginners think XML is just another version of HTML, but there is one major difference:
HTML comes with predefined tags. Browsers already know what those tags mean.
XML does not have predefined tags.
You create your own tags based on your application's needs.
Example:
<?xml version="1.0" encoding="UTF-8"?>
<person>
    <name>p0nther</name>
    <job>Hacker</job>
    <goal>Pwn2Own</goal>
    <role_model>Orange Tsai</role_model>
</person>
XML is simply a structured way to represent information.

---

Why Was XML Created?
Imagine 50 companies exchanging data.
Without standards, one company may send:
<username>john</username>
Another may send:
<user>john</user>
And another:
<name>john</name>
The receiving application would constantly need special handling for every format.
XML solves the data structure problem.
However, we still need a way to define:
Which tags are allowed

Which tags are required

The order of tags

Which attributes are valid

This is where DTD comes in.

---

What Is DTD?
DTD stands for Document Type Definition.
Think of it as a rulebook for XML files.
It tells the parser:
Which tags are valid

Which tags must exist

How elements are structured

Which attributes are allowed

Example:
ELEMENT note (to, from, message)
ELEMENT to (#PCDATA)
ELEMENT from (#PCDATA)
ELEMENT message (#PCDATA)
This DTD says a note must contain:
to

from

message

and each of those elements contains text.

---

Why Do Developers Use DTD?
Imagine a company receives thousands of XML files daily.
Without validation, someone might send:
<note>
    <sender>Bob</sender>
</note>
while the application expects:
<note>
    <from>Bob</from>
</note>
The application could fail.
DTD prevents this by enforcing rules.
It can:
Ensure required tags exist

Reject unexpected tags

Validate structure

Standardize data between systems

---

Internal DTD
An Internal DTD is written directly inside the XML document.
Example:
DOCTYPE BUGS [
ELEMENT BUGS (item+)
ELEMENT item (name,severity)
ELEMENT name (#PCDATA)
ELEMENT severity (#PCDATA)
ATTLIST item PRIORITY CDATA "0"
]
Example XML:
<BUGS>
    <item PRIORITY="HIGH">
        <name>Server-Side Bugs</name>
        <severity>9.2</severity>
    </item>
</BUGS>

---

External DTD
Instead of embedding rules inside every XML file, developers often place them in a separate file.
Example DTD file:
ELEMENT BUGS (item+)
ELEMENT item (name,severity)
ELEMENT name (#PCDATA)
ELEMENT severity (#PCDATA)
Referenced from XML:
DOCTYPE BUGS SYSTEM "rules.dtd"
The parser loads the external DTD and validates the XML against it.
This approach is easier to maintain and reuse across multiple systems.

---

Understanding XML Entities
Entities are essentially variables inside XML.
Instead of repeating values everywhere, we define them once and reference them later.
Example:
ENTITY author "Abdarhman Mohamed (p0nther)"
Usage:
<name>author</name>
After expansion, the parser inserts the value of the entity into the document.
Simple enough.
But entities become very interesting when they reference external resources.

---

External Entities
XML entities can load data from files or URLs.
Conceptually:
Entity
   │
   ▼
External File / URL
   │
   ▼
Data Returned To Parser
If external entities are enabled, the parser may attempt to read local files or contact remote systems.
This behavior is exactly what makes XXE possible.

---

How XML Parsers Process Documents
Understanding the parser workflow is critical.
Most XML parsers process documents in roughly this order:
Incoming XML
      │
      ▼
Read DOCTYPE
      │
      ▼
Load DTD
      │
      ▼
Validate Structure
      │
      ▼
Expand Entities
      │
      ▼
Build Final XML Object
      │
      ▼
Application Logic
The dangerous step is entity expansion.
If attackers control the XML document, they may be able to force the parser to load local files or remote resources.

---

Introducing XXE
XXE stands for:
XML External Entity Injection
It occurs when:
The application accepts XML input.

External entities are enabled.

The attacker controls part of the XML document.

A vulnerable parser may expand attacker-controlled entities and access resources that should never be exposed.
Common impacts include:
Local file disclosure

Internal network access

SSRF

Blind data exfiltration

---

Detecting XXE
A good testing methodology is to move gradually.
Step 1: Confirm Entity Expansion
Start with a harmless entity.
If the application reflects the expanded value, entity processing is enabled.

---

Step 2: Attempt File Disclosure
Try referencing a local file.
If file contents appear in the response, XXE is confirmed.
Potential targets include:
Configuration files

Application source code

Environment files

Logs

---

Step 3: Test Outbound Requests
Try referencing a URL you control.
If your server receives a request, outbound communication is possible.
This becomes important for Blind XXE testing.

---

Blind XXE
Sometimes the application processes entities but does not return the result.
The file may be read successfully, but you never see the contents in the response.
This situation is called Blind XXE.
In these cases, attackers often rely on external interactions to confirm exploitation.

---

Parameter Entities
XML supports a special type of entity called a parameter entity.
Normal entities are referenced inside XML content.
Parameter entities are primarily used inside DTD files.
These become important when working with advanced XXE techniques involving external DTDs.

---

Loading a Remote DTD
Instead of embedding a large DTD inside a request, an attacker may attempt to make the parser load a DTD hosted on another server.
Conceptually:
XML Document
      │
      ▼
External DTD
      │
      ▼
Parser Processes Rules
If external DTD loading is enabled, the parser may download and process the remote DTD.

---

Out-of-Band XXE
Sometimes the application does not display any file contents.
In such cases, attackers may attempt to force the vulnerable server to interact with an external system under their control.
Conceptually:
Victim Parser
      │
      ▼
Loads Remote DTD
      │
      ▼
Processes Entities
      │
      ▼
Makes External Request
      │
      ▼
Attacker Observes Activity
This technique is known as Out-of-Band (OOB) XXE.

---

XXE to SSRF
One of the most common XXE escalation paths is SSRF.
Because the XML parser may be capable of making outbound requests, attackers can sometimes force it to access internal resources.
Conceptually:
XXE
 │
 ▼
Server Makes Request
 │
 ▼
Internal Resource Access
 │
 ▼
SSRF
Potential targets include:
Internal APIs

Administrative panels

Microservices

Cloud services

The exact impact depends on the target environment.

---

Vulnerable Python Example
A common mistake is enabling entity resolution.
from lxml import etree
parser = etree.XMLParser(
    resolve_entities=True,
    no_network=False
)
Problems:
resolve_entities=True expands attacker-controlled entities.

no_network=False allows external resource fetching.

This can create XXE vulnerabilities.

---

Secure Python Example
from lxml import etree
parser = etree.XMLParser(
    resolve_entities=False,
    load_dtd=False,
    no_network=True
)
Why?
resolve_entities=False disables entity expansion.

load_dtd=False blocks external DTD loading.

no_network=True prevents outbound network requests.

Together, these settings eliminate the most common XXE attack paths.

---

Final Thoughts
Most XXE payloads look simple.
However, understanding why they work requires understanding XML itself.
The attack exists because:
XML supports entities.

Entities can reference external resources.

XML parsers automatically process those resources.

Applications trust the parser.

Once you understand DTDs, entities, parser behavior, and external resource loading, XXE becomes much easier to understand.
As a bug bounty hunter, don't focus on memorizing payloads.
Focus on understanding the parser.
That's where the vulnerability actually lives.
