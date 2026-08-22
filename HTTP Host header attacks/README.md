# HTTP Host Header Attacks — Complete Notes

When many bug bounty hunters first encounter HTTP Host Header Attacks, they immediately start collecting payloads.

They memorize things like:

```http
Host: evil.com
X-Forwarded-Host: evil.com
X-Host: evil.com
Forwarded: host=evil.com
```

and start adding random headers to every request.

But without understanding how web servers actually use the Host header, Host Header Attacks often feel confusing.

In this article, we'll build the concept from the ground up and understand:

* What the Host header is
* Why it exists
* How web servers use it
* Why trusting it is dangerous
* Common attack scenarios
* How to identify vulnerable applications
* How developers should fix it

---

# What Is The Host Header?

Every HTTP/1.1 request contains a Host header.

Example:

```http
GET / HTTP/1.1
Host: app.example.com
```

The Host header tells the server:

```text
Which website does the client want?
```

Without it, modern web hosting would not work properly.

---

# Why Was The Host Header Created?

Imagine one server hosting multiple websites:

```text
192.168.1.10
     │
     ├── shop.example.com
     ├── api.example.com
     └── blog.example.com
```

All domains point to the same IP.

When a request arrives:

```http
GET / HTTP/1.1
Host: shop.example.com
```

the web server knows:

```text
Serve the shop website
```

If the request contains:

```http
GET / HTTP/1.1
Host: blog.example.com
```

the server serves:

```text
The blog website
```

This mechanism is called:

```text
Virtual Hosting
```

---

# How Web Servers Use Host

```text
Incoming Request
       │
       ▼
Read Host Header
       │
       ▼
Choose Virtual Host
       │
       ▼
Process Request
       │
       ▼
Return Response
```

Normally:

```http
Host: app.example.com
```

becomes:

```text
Current Website = app.example.com
```

---

# Why Is Trusting Host Dangerous?

Many developers assume:

```text
The Host header always contains a valid domain.
```

But the client controls:

```http
Host:
```

which means the attacker controls:

```text
Host
```

If the application uses Host in security-sensitive logic:

```text
Attacker
    │
    ▼
Host Header
    │
    ▼
Application Logic
```

unexpected behavior can occur.

---

# Vulnerable Example

```python
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():

    host = request.headers.get(
        "Host"
    )

    reset_link = (
        "https://" +
        host +
        "/reset-password"
    )

    return reset_link
```

The developer assumes:

```text
Host = app.example.com
```

But the attacker sends:

```http
GET / HTTP/1.1
Host: evil.com
```

The application generates:

```text
https://evil.com/reset-password
```

instead.

---

# Password Reset Poisoning

One of the most common Host Header vulnerabilities.

Imagine:

```python
reset_url = (
    "https://" +
    request.headers["Host"] +
    "/reset?token=ABC123"
)
```

Application sends:

```text
Password reset email
```

to the victim.

Attacker sends:

```http
Host: evil.com
```

The victim receives:

```text
https://evil.com/reset?token=ABC123
```

and clicks it.

Flow:

```text
Victim
   │
   ▼
Password Reset Email
   │
   ▼
evil.com
   │
   ▼
Token Stolen
   │
   ▼
Account Takeover
```

---

# Web Cache Poisoning

Many caches use:

```text
URL
```

as cache keys.

But applications may generate content using:

```http
Host
```

Example:

```python
host = request.headers.get(
    "X-Forwarded-Host",
    ""
)

response = f"""
<script src="https://{host}/app.js"></script>
"""
```

Attacker sends:

```http
X-Forwarded-Host: evil.com
```

Cache stores:

```html
<script src="https://evil.com/app.js"></script>
```

Victims later receive:

```html
<script src="https://evil.com/app.js"></script>
```

without sending the malicious header.

This becomes:

```text
Host Header Attack
        │
        ▼
Cache Poisoning
        │
        ▼
Stored XSS
```

in some environments.

---

# Routing-Based SSRF

Some applications use Host to decide backend routing.

Example:

```python
backend = (
    "http://" +
    request.headers["Host"]
)
```

Then:

```python
requests.get(backend)
```

Attacker sends:

```http
Host: 169.254.169.254
```

Possible result:

```text
Application
     │
     ▼
Cloud Metadata Service
```

This can become:

```text
Host Header
      │
      ▼
SSRF
```

---

# Host-Based Access Control Bypass

Developers sometimes trust Host.

Example:

```python
if request.headers["Host"] == "admin.internal":
    allow_admin()
```

Attacker sends:

```http
Host: admin.internal
```

If the server accepts it:

```text
Access Control Bypass
```

may occur.

---

# Virtual Host Brute Forcing

Sometimes hidden applications exist.

Server:

```text
10.10.10.10
```

Known host:

```text
www.example.com
```

Attacker tests:

```http
Host: admin.example.com
Host: dev.example.com
Host: staging.example.com
Host: internal.example.com
```

Responses may reveal:

* Internal panels
* Admin portals
* Staging environments
* Forgotten applications

---

# Common Headers To Test

Besides:

```http
Host:
```

test:

```http
X-Forwarded-Host:
```

---

```http
X-Host:
```

---

```http
Forwarded: host=evil.com
```

---

```http
X-Original-Host:
```

---

```http
X-Forwarded-Server:
```

Some frameworks trust these headers.

---

# Typical Testing Methodology

## 1. Modify Host

Original:

```http
Host: app.example.com
```

Test:

```http
Host: evil.com
```

Look for:

* Reflection
* Redirects
* Generated URLs
* Email links

---

## 2. Search For Absolute URLs

Example response:

```html
<a href="https://app.example.com/login">
```

Replace Host and check whether it changes.

---

## 3. Test Password Reset

Initiate password reset.

Replace:

```http
Host: evil.com
```

Check whether email links contain:

```text
evil.com
```

---

## 4. Test Cache Behavior

Send:

```http
X-Forwarded-Host: evil.com
```

Check:

```http
X-Cache: hit
Age: 30
```

If cached responses contain attacker data:

```text
Cache Poisoning Possible
```

---

## 5. Enumerate Virtual Hosts

Use tools like:

```bash
ffuf -H "Host: FUZZ.example.com"
```

Look for:

* Different status codes
* Different content lengths
* Different page titles

---

# Impact

## Password Reset Poisoning

```text
Host Header
      │
      ▼
Reset Link Manipulation
      │
      ▼
Account Takeover
```

---

## Web Cache Poisoning

```text
Host Header
      │
      ▼
Cache Poisoning
      │
      ▼
Victim Receives Malicious Response
```

---

## SSRF

```text
Host Header
      │
      ▼
Backend Request
      │
      ▼
Internal Resource Access
```

---

## Access Control Bypass

```text
Host Header
      │
      ▼
Trust Boundary Broken
      │
      ▼
Unauthorized Access
```

---

## Virtual Host Discovery

```text
Host Enumeration
       │
       ▼
Hidden Applications Found
```

---

# Vulnerable Flask Example

```python
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():

    host = request.headers.get(
        "Host"
    )

    return f"""
    <a href='https://{host}/login'>
        Login
    </a>
    """

app.run()
```

Problem:

```python
host = request.headers.get("Host")
```

is fully attacker-controlled.

---

# Secure Example

Use a trusted configuration value:

```python
BASE_URL = (
    "https://app.example.com"
)

reset_url = (
    BASE_URL +
    "/reset"
)
```

Never use:

```python
request.headers["Host"]
```

for security-sensitive operations.

---

# Additional Defenses

## Validate Host

Allow only trusted domains:

```python
ALLOWED = [
    "app.example.com"
]

if host not in ALLOWED:
    abort(400)
```

---

## Use Fixed Base URLs

Instead of:

```python
request.headers["Host"]
```

use:

```python
https://app.example.com
```

---

## Configure Reverse Proxies Correctly

Do not blindly trust:

```http
X-Forwarded-Host
```

from users.

---

## Separate Cache Keys

Ensure caches include every header that influences content generation.

---

# Quick Summary

Host Header:

* Identifies the requested website.
* Required for virtual hosting.

Problem:

* Client fully controls the Host header.

Common Attacks:

* Password Reset Poisoning
* Web Cache Poisoning
* SSRF
* Access Control Bypass
* Virtual Host Enumeration

Headers Worth Testing:

```http
Host
X-Forwarded-Host
X-Host
Forwarded
X-Original-Host
```

Defenses:

* Validate allowed hosts
* Use fixed base URLs
* Avoid trusting Host in security logic
* Configure proxies carefully
* Separate cache keys correctly
