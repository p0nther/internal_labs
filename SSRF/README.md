# SSRF (Server-Side Request Forgery) — Complete Notes

When many bug bounty hunters first encounter SSRF (Server-Side Request Forgery), they immediately start collecting bypass payloads.

They memorize:

* `127.0.0.1`
* `localhost`
* Decimal IPs
* IPv6 tricks
* Redirect bypasses

But without understanding **why the server is making requests on your behalf**, SSRF often feels like a collection of random tricks.

In this article, we'll build the foundation first:

* What SSRF is
* Why applications fetch remote resources
* How server-side requests work
* How SSRF vulnerabilities happen
* Common SSRF attack flows
* Internal network access
* Cloud metadata abuse
* SSRF bypass techniques
* Blind SSRF
* How developers can prevent it

---

# What Is SSRF?

SSRF stands for:

**Server-Side Request Forgery**

It occurs when an attacker can make a vulnerable server send requests to locations chosen by the attacker.

Instead of the attacker directly contacting the target:

```
Attacker
    │
    ▼
Target
```

the request flow becomes:

```
Attacker
    │
    ▼
Vulnerable Server
    │
    ▼
Target
```

The vulnerable server becomes a proxy.

---

# Why Do Applications Fetch URLs?

Many applications need to retrieve remote resources.

Examples:

* Image importers
* PDF generators
* Link preview systems
* RSS readers
* File converters
* Video downloaders
* Webhooks
* API integrations

Example:

A website allows users to import profile pictures.

User submits:

```
https://example.com/avatar.jpg
```

The application downloads the image and stores it.

Conceptually:

```
User URL
    │
    ▼
Application
    │
    ▼
Remote Server
```

This functionality is completely normal.

Problems begin when user-controlled URLs are not properly restricted.

---

# Understanding Server-Side Requests

Imagine a server receives:

```
https://example.com/image.jpg
```

The application might perform:

```python
requests.get(url)
```

The request is not made by the attacker.

The request is made by the server itself.

This distinction is critical.

From the target's perspective:

```
Source IP = Application Server
```

not

```
Source IP = Attacker
```

The server inherits all trust and network access available to it.

---

# Why Is This Dangerous?

Servers often have access that external users do not.

For example:

```
Internet User
      │
      ▼
Cannot Reach Internal Network
```

but

```
Application Server
      │
      ▼
Can Reach Internal Network
```

This difference creates the opportunity for SSRF.

---

# Introducing SSRF

A vulnerability exists when:

* The application accepts a URL
* The attacker controls that URL
* The server fetches the URL
* Restrictions are missing or insufficient

Example vulnerable code:

```python
import requests

url = request.args.get("url")

response = requests.get(url)

return response.text
```

The attacker fully controls the destination.

---

# Basic SSRF Flow

Normal behavior:

```
User
 │
 ▼
https://images.example.com/cat.jpg
 │
 ▼
Application Downloads Image
```

Attacker behavior:

```
User
 │
 ▼
http://127.0.0.1/admin
 │
 ▼
Application Downloads Internal Page
```

Now the application accesses resources that should not be reachable from outside.

---

# Internal Network Access

Many organizations expose services only inside the corporate network.

Examples:

```
10.0.0.0/8
172.16.0.0/12
192.168.0.0/16
```

Internal targets may include:

* Admin panels
* Internal APIs
* Monitoring dashboards
* Databases
* Kubernetes services
* Development environments

Conceptually:

```
Attacker
    │
    ▼
Vulnerable Server
    │
    ▼
10.0.0.5
```

The attacker gains indirect access.

---

# Localhost Access

One of the most common SSRF targets is:

```
127.0.0.1
```

or

```
localhost
```

Why?

Applications often expose management interfaces only locally.

Example:

```
http://127.0.0.1:8080/admin
```

Developers assume:

> "Nobody can access this page externally."

SSRF breaks that assumption.

---

# Cloud Metadata Services

Cloud providers often expose metadata endpoints.

These endpoints provide information about the running instance.

Historically, one famous target has been:

```
http://169.254.169.254/
```

The exact paths vary by provider and version.

Metadata services may expose:

* Instance information
* Network information
* Temporary credentials
* Service configuration

This is one reason SSRF became such a high-impact vulnerability class.

---

# Detecting SSRF

A good methodology is to move gradually.

---

## Step 1: Confirm External Requests

Submit a URL pointing to a server you control.

Example:

```
https://your-server.com/test
```

If you receive a request, the application performs outbound requests.

---

## Step 2: Test Internal Targets

Try common internal locations:

```
127.0.0.1
localhost
```

Look for:

* Different responses
* Different response times
* Error message changes

---

## Step 3: Map Internal Services

If responses are reflected, internal enumeration may be possible.

Examples:

```
127.0.0.1:80
127.0.0.1:8080
127.0.0.1:5000
```

Different ports often produce different responses.

---

# Blind SSRF

Sometimes the application does not return the fetched response.

Example:

```python
requests.get(url)

return "Success"
```

The request happens.

But the response is discarded.

This is called:

**Blind SSRF**

You cannot directly see the returned data.

---

# Detecting Blind SSRF

Use a server you control.

Conceptually:

```
Attacker
     │
     ▼
Vulnerable Application
     │
     ▼
Attacker-Controlled Server
```

If your server receives a request:

* SSRF exists
* Outbound communication is possible

even if the application never returns the response.

---

# SSRF Through Redirects

Some applications validate the initial URL.

Example:

```python
if url.startswith(
    "https://trusted.com"
):
    requests.get(url)
```

Attacker:

```
https://trusted.com/redirect
```

Server:

```
302 Location:
http://127.0.0.1/admin
```

The application follows the redirect and reaches the internal target.

---

# Common SSRF Bypass Techniques

Developers often attempt simple filters.

Example:

```python
if "127.0.0.1" in url:
    block()
```

Attackers may look for alternative representations.

Examples include:

* Different hostnames
* Redirect chains
* DNS-based tricks
* URL parser inconsistencies

The exact techniques vary depending on the application and programming language.

The root problem remains the same:

The server is still allowed to make attacker-controlled requests.

---

# SSRF to Internal Reconnaissance

SSRF often becomes an internal discovery tool.

Conceptually:

```
SSRF
 │
 ▼
Internal Requests
 │
 ▼
Service Discovery
 │
 ▼
Attack Surface Expansion
```

An attacker may learn:

* Open ports
* Internal hostnames
* Available services
* Response characteristics

---

# SSRF to Remote Code Execution

Sometimes SSRF is only the first step.

Example chain:

```
SSRF
 │
 ▼
Internal Admin Interface
 │
 ▼
Dangerous Functionality
 │
 ▼
Remote Code Execution
```

The SSRF itself is not code execution.

However, it may provide access to systems that eventually lead to code execution.

---

# Vulnerable Python Example

```python
from flask import request
import requests

url = request.args.get("url")

response = requests.get(url)

return response.text
```

Problem:

The attacker controls the destination URL completely.

The server will fetch any reachable resource.

---

# More Secure Python Example

```python
from urllib.parse import urlparse

ALLOWED_HOSTS = [
    "images.example.com"
]

parsed = urlparse(url)

if parsed.hostname not in ALLOWED_HOSTS:
    return "Blocked"

response = requests.get(
    url,
    allow_redirects=False
)
```

Additional protections may include:

* DNS validation
* Redirect restrictions
* IP filtering
* Network segmentation
* Outbound firewall rules

---

# SSRF Defense in Depth

Good SSRF protection rarely relies on a single control.

A strong approach combines:

### Application Layer

* Allowlists
* URL validation
* Redirect restrictions

### Network Layer

* Outbound firewall rules
* Internal network isolation

### Infrastructure Layer

* Metadata protections
* Least privilege
* Service segmentation

Multiple layers reduce the impact of mistakes.

---

# Final Thoughts

Most SSRF payloads look simple.

However, understanding why they work requires understanding how applications fetch resources.

The vulnerability exists because:

1. Applications accept user-controlled URLs.

2. Servers trust those URLs.

3. Servers make requests on behalf of users.

4. Servers often have access that users do not.

5. Attackers abuse that trust boundary.

Once you understand request flow, internal networks, localhost access, cloud metadata services, and blind SSRF, SSRF becomes much easier to understand.

As a bug bounty hunter, don't focus on memorizing bypass payloads.

Focus on understanding why the server is making the request.

That's where the vulnerability actually lives.
