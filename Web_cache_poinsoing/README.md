# Web Cache Poisoning — Complete Notes

When many bug bounty hunters first encounter Web Cache Poisoning, they immediately start collecting payloads.

They memorize things like:

```text
X-Forwarded-Host
X-Host
X-Original-URL
X-Rewrite-URL
```

and start adding random headers to every request.

But without understanding how web caches actually work, Web Cache Poisoning often feels confusing.

In this article, we'll build the foundation first:

* What web caches are
* Why websites use caching
* How cache keys work
* How responses are cached
* How Web Cache Poisoning happens
* Cache key flaws
* Cache deception vs cache poisoning
* Common impacts
* How developers can prevent it

---

# What Is a Web Cache?

A web cache is a system that stores previously generated responses.

Instead of generating the same page repeatedly:

```text
User 1
   │
   ▼
Application
   │
   ▼
Response Generated
```

the cache stores the result:

```text
User 1
   │
   ▼
Application
   │
   ▼
Cache Stores Response
```

Then future users receive:

```text
User 2
   │
   ▼
Cache
   │
   ▼
Cached Response
```

without contacting the application.

---

# Why Do Websites Use Caching?

Generating pages repeatedly can be expensive.

Imagine:

```text
10,000 Users
       │
       ▼
Homepage
```

Without caching:

```text
10,000 Requests
       │
       ▼
10,000 Database Queries
```

With caching:

```text
10,000 Requests
       │
       ▼
1 Database Query
       │
       ▼
Cached Response
```

Benefits include:

* Faster performance
* Reduced server load
* Lower database usage
* Better scalability

This is why caching is everywhere.

---

# Types of Web Caches

Caching can happen at multiple layers.

Examples:

Browser Cache:

```text
User Browser
      │
      ▼
Cached Resource
```

CDN Cache:

```text
User
  │
  ▼
CDN
  │
  ▼
Origin Server
```

Reverse Proxy Cache:

```text
User
  │
  ▼
Cache Server
  │
  ▼
Web Application
```

Common caching technologies include:

* Varnish
* Nginx
* Cloudflare
* Akamai
* Fastly
* AWS CloudFront

---

# Understanding Cache Keys

A cache must decide whether two requests are identical.

To do this, it creates a:

**Cache Key**

Example request:

```http
GET /profile HTTP/1.1
Host: example.com
```

Cache key:

```text
example.com/profile
```

The cache stores:

```text
Cache Key
      │
      ▼
Cached Response
```

Future requests with the same key receive the cached response.

---

# Cache Hit vs Cache Miss

Cache Miss:

```text
Request
   │
   ▼
Cache
   │
   ▼
Not Found
   │
   ▼
Application
   │
   ▼
Response Generated
```

Cache Hit:

```text
Request
   │
   ▼
Cache
   │
   ▼
Cached Response Returned
```

No application processing is required.

---

# Introducing Web Cache Poisoning

Web Cache Poisoning occurs when:

* User-controlled input affects a response
* The cache stores that response
* Other users receive the poisoned content

Conceptually:

```text
Attacker Request
        │
        ▼
Application Generates Response
        │
        ▼
Cache Stores Response
        │
        ▼
Victims Receive Poisoned Content
```

The attacker poisons the cache once.

Many users receive the malicious result.

---

# Understanding the Root Problem

The vulnerability usually appears when:

```text
Input Affects Response
```

but

```text
Input Does NOT Affect Cache Key
```

This creates a mismatch.

Example:

Application uses:

```http
X-Forwarded-Host: evil.com
```

when generating content.

But cache key only contains:

```text
Host + Path
```

The cache ignores:

```text
X-Forwarded-Host
```

while the application trusts it.

This difference creates the vulnerability.

---

# Visualizing the Attack

Step 1:

Attacker sends:

```http
GET / HTTP/1.1
Host: example.com
X-Forwarded-Host: evil.com
```

Application generates:

```html
<script src="https://evil.com/app.js"></script>
```

---

Step 2:

Cache stores:

```html
<script src="https://evil.com/app.js"></script>
```

under:

```text
example.com/
```

---

Step 3:

Victim requests:

```http
GET / HTTP/1.1
Host: example.com
```

Cache responds:

```html
<script src="https://evil.com/app.js"></script>
```

The victim receives attacker-controlled content.

---

# Why Does This Happen?

Think of the system as two separate components.

Cache:

```text
Request
   │
   ▼
Cache Key Calculation
```

Application:

```text
Request
   │
   ▼
Response Generation
```

If they use different inputs:

```text
Cache Key Inputs
       ≠
Response Inputs
```

cache poisoning becomes possible.

---

# Detecting Web Cache Poisoning

A good methodology is to move gradually.

---

## Step 1: Determine Whether Caching Exists

Look for headers such as:

```http
Cache-Control
Age
X-Cache
CF-Cache-Status
```

Common indicators:

```http
X-Cache: HIT
```

```http
CF-Cache-Status: HIT
```

A cache hit indicates cached content.

---

## Step 2: Find User-Controlled Inputs

Potential inputs include:

* Headers
* Query parameters
* Host headers
* Cookies
* URL paths

Ask:

```text
Does this input affect the response?
```

---

## Step 3: Check Cache Key Behavior

Ask:

```text
Does this input affect the cache key?
```

If:

```text
Affects Response
```

but

```text
Does Not Affect Cache Key
```

the input becomes interesting.

---

# Common Unkeyed Inputs

An unkeyed input is used by the application but ignored by the cache.

Examples often include:

```http
X-Forwarded-Host
```

```http
X-Host
```

```http
X-Forwarded-Scheme
```

```http
X-Original-URL
```

The exact behavior depends on the environment.

---

# Cache Poisoning Through Headers

Imagine:

Application:

```python
url = request.headers.get(
    "X-Forwarded-Host"
)
```

Used inside:

```html
<script src="https://HOST/app.js"></script>
```

Cache key:

```text
Host + Path
```

Header ignored.

Now an attacker can influence the cached page.

---

# Cache Poisoning Through Query Parameters

Sometimes applications reflect query parameters.

Example:

```http
GET /?theme=dark
```

If:

```text
theme
```

changes the response but is ignored by caching logic, poisoning may become possible.

---

# Cache Poisoning Through Host Headers

Applications frequently build URLs using:

```http
Host:
```

Example:

```html
<link href="https://HOST/style.css">
```

Improper handling may allow attacker-controlled content to enter cached responses.

---

# Cache Poisoning and Stored XSS

One of the most common outcomes is:

```text
Web Cache Poisoning
          │
          ▼
Cached Malicious Script
          │
          ▼
Victim Browser
          │
          ▼
Stored XSS-Like Impact
```

The payload executes for every user receiving the poisoned response.

---

# Cache Poisoning and Open Redirects

Conceptually:

```text
Cache Poisoning
        │
        ▼
Cached Redirect
        │
        ▼
Victims Redirected
```

An attacker poisons a redirect response and affects subsequent visitors.

---

# Cache Poisoning and Denial of Service

Sometimes the attacker causes:

```text
Malformed Response
       │
       ▼
Cached Error Page
       │
       ▼
All Users Receive Error
```

This can create large-scale disruption.

---

# Web Cache Poisoning vs Web Cache Deception

Many beginners confuse these vulnerabilities.

Web Cache Poisoning:

```text
Attacker Stores
Malicious Content
Inside Cache
```

Goal:

```text
Poison Future Responses
```

---

Web Cache Deception:

```text
Sensitive Response
Accidentally Cached
```

Goal:

```text
Steal Cached Data
```

One poisons the cache.

The other tricks the cache into storing sensitive information.

---

# Real-World Attack Flow

Conceptually:

```text
Attacker
    │
    ▼
Find Unkeyed Input
    │
    ▼
Modify Response
    │
    ▼
Poison Cache
    │
    ▼
Victims Request Page
    │
    ▼
Receive Poisoned Content
```

The attacker only needs one successful poisoning event.

The cache distributes the payload afterward.

---

# Preventing Web Cache Poisoning

The safest approach is ensuring:

```text
Everything That Influences
The Response
Also Influences
The Cache Key
```

or

```text
Untrusted Input
Cannot Influence
Cacheable Responses
```

---

# Defense in Depth

### Application Layer

* Validate headers
* Validate hostnames
* Avoid trusting proxy headers
* Avoid reflecting user input

### Cache Layer

* Key relevant headers
* Disable caching for dynamic content
* Normalize requests consistently

### Infrastructure Layer

* Restrict trusted proxies
* Use strict CDN configuration
* Monitor unusual cache behavior

---

# Understanding the Root Cause

Most Web Cache Poisoning payloads look simple.

However, understanding why they work requires understanding how caches make decisions.

The vulnerability exists because:

1. Caches store responses.

2. Caches use cache keys.

3. Applications generate responses using request data.

4. Some inputs affect the response but not the cache key.

5. Attackers exploit that mismatch.

Once you understand cache keys, cache hits, unkeyed inputs, and response generation, Web Cache Poisoning becomes much easier to understand.

As a bug bounty hunter, don't focus on memorizing header payloads.

Focus on understanding what the cache sees versus what the application sees.

That's where the vulnerability actually lives.
