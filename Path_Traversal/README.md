# Path Traversal (Directory Traversal) — Complete Notes

When many bug bounty hunters first encounter Path Traversal, they immediately start collecting payloads.

They memorize things like:

```text
../../../etc/passwd
..\..\..\windows\win.ini
....//
..%2f
..%252f
```

and begin trying them everywhere.

But without understanding how applications access files, Path Traversal often feels like a collection of bypass techniques rather than a real vulnerability.

In this article, we'll build the foundation first:

* What file paths are
* How applications access files
* Why applications use user-supplied filenames
* How Path Traversal happens
* Detecting Path Traversal
* Common targets
* Relative and absolute paths
* Path normalization
* Common bypasses
* How developers can prevent it

---

# What Is a File Path?

A file path tells the operating system where a file is located.

Examples:

Linux:

```text
/home/user/file.txt
```

```text
/etc/passwd
```

Windows:

```text
C:\Users\Admin\file.txt
```

```text
C:\Windows\win.ini
```

Applications constantly use paths to:

* Read files
* Write files
* Upload files
* Download files
* Load templates
* Access logs
* Store user data

---

# Why Do Applications Use User-Supplied Paths?

Many applications allow users to request files.

Examples:

* Download centers
* Image viewers
* PDF viewers
* File managers
* Document portals

Example:

User requests:

```http
GET /download?file=report.pdf
```

Application:

```python
open("uploads/report.pdf")
```

The requested file is returned to the user.

This behavior is completely legitimate.

Problems begin when the filename is not properly restricted.

---

# Understanding Directories

Think of directories like folders inside folders.

Example:

```text
/
├── home
│   └── user
├── var
├── etc
└── uploads
```

If an application is designed to access:

```text
/uploads/
```

it should never allow users to escape that directory.

---

# Understanding Relative Paths

A relative path is interpreted based on the current directory.

Example:

```text
image.jpg
```

means:

```text
CurrentDirectory/image.jpg
```

Example:

```text
docs/report.pdf
```

means:

```text
CurrentDirectory/docs/report.pdf
```

The operating system resolves the final location automatically.

---

# Understanding ".."

Operating systems provide special directory references.

Current directory:

```text
.
```

Parent directory:

```text
..
```

Example:

```text
/var/www/uploads
```

One level up:

```text
..
```

becomes:

```text
/var/www
```

Another level:

```text
../..
```

becomes:

```text
/var
```

And another:

```text
../../..
```

becomes:

```text
/
```

This feature is useful for navigation.

It becomes dangerous when attackers control file paths.

---

# Introducing Path Traversal

Path Traversal occurs when:

* The application accepts a file path
* The attacker controls that path
* The application fails to restrict directory access
* Files outside the intended directory become accessible

Example:

Application:

```python
filename = request.args.get("file")

path = "uploads/" + filename

open(path)
```

Normal input:

```text
report.pdf
```

Generated path:

```text
uploads/report.pdf
```

Everything works normally.

---

Attacker input:

```text
../../../etc/passwd
```

Generated path:

```text
uploads/../../../etc/passwd
```

After normalization:

```text
/etc/passwd
```

The application reads a completely different file.

---

# Why Does This Happen?

The root problem is simple.

Developers combine:

```text
Trusted Directory
```

with:

```text
User Input
```

Example:

```python
path = "uploads/" + user_input
```

The operating system resolves the path.

The application assumes the file remains inside:

```text
uploads/
```

but the operating system follows directory traversal sequences.

---

# Understanding Path Normalization

Before accessing a file, the operating system usually normalizes the path.

Example:

```text
uploads/../images/photo.jpg
```

becomes:

```text
images/photo.jpg
```

Another example:

```text
uploads/../../../etc/passwd
```

becomes:

```text
/etc/passwd
```

This normalization process is what makes Path Traversal possible.

---

# Visualizing the Attack

Normal flow:

```text
User Input
     │
     ▼
report.pdf
     │
     ▼
uploads/report.pdf
     │
     ▼
File Returned
```

Traversal flow:

```text
User Input
     │
     ▼
../../../etc/passwd
     │
     ▼
uploads/../../../etc/passwd
     │
     ▼
Normalized
     │
     ▼
/etc/passwd
     │
     ▼
Sensitive File Returned
```

---

# Detecting Path Traversal

A good methodology is to move gradually.

---

## Step 1: Identify File Functionality

Look for features such as:

* File downloads
* File previews
* Image viewers
* Log viewers
* Template loaders
* Backup downloads

Any feature that accesses files is a potential target.

---

## Step 2: Test Traversal Sequences

Try moving up directories.

Example:

```text
../
```

```text
../../
```

```text
../../../
```

Observe whether:

* Different files are returned
* Error messages change
* Response sizes change

---

## Step 3: Confirm Arbitrary File Access

If files outside the intended directory become accessible, Path Traversal is confirmed.

---

# Common Targets

Attackers often look for files containing useful information.

Examples:

Linux:

```text
/etc/passwd
```

```text
/etc/hosts
```

```text
/etc/nginx/nginx.conf
```

Windows:

```text
C:\Windows\win.ini
```

```text
C:\Windows\System32\drivers\etc\hosts
```

Application-specific files:

```text
.env
config.yml
settings.py
database.db
```

The exact targets depend on the environment.

---

# Absolute Paths

Sometimes applications allow absolute paths.

Example:

```text
/etc/passwd
```

or

```text
C:\Windows\win.ini
```

If absolute paths are accepted directly, traversal sequences may not even be required.

---

# URL Encoding

Applications often receive paths through URLs.

Example:

```text
../
```

may become:

```text
..%2f
```

because:

```text
/
```

is URL-encoded as:

```text
%2f
```

Path validation mistakes frequently occur during decoding and normalization.

---

# Double Decoding Problems

Some applications decode input multiple times.

Example:

```text
..%252f
```

First decode:

```text
..%2f
```

Second decode:

```text
../
```

The final result becomes a traversal sequence.

This class of issue often appears when validation occurs before full decoding.

---

# Path Traversal vs File Inclusion

Many beginners confuse these vulnerabilities.

Path Traversal:

```text
Application
      │
      ▼
Reads Arbitrary File
```

File Inclusion:

```text
Application
      │
      ▼
Loads File As Code
```

Path Traversal usually results in file disclosure.

File Inclusion can sometimes lead to code execution.

---

# Common Impacts

Path Traversal often leads to:

* Configuration disclosure
* Source code disclosure
* Credential leakage
* Environment variable exposure
* Internal application discovery

Conceptually:

```text
Path Traversal
       │
       ▼
Sensitive File Access
       │
       ▼
Information Disclosure
```

In some environments, additional attack chains may be possible.

---

# Vulnerable Python Example

```python
from flask import request

filename = request.args.get("file")

with open(
    "uploads/" + filename
) as f:
    return f.read()
```

Problem:

The attacker controls part of the path.

The operating system resolves traversal sequences.

---

# More Secure Python Example

```python
from pathlib import Path

BASE_DIR = Path("uploads").resolve()

requested = (
    BASE_DIR / filename
).resolve()

if not str(requested).startswith(
    str(BASE_DIR)
):
    return "Access Denied"

return requested.read_text()
```

Why is this safer?

The application verifies that the final resolved path remains inside:

```text
uploads/
```

Even after normalization.

---

# Defense in Depth

Good protection combines multiple controls.

### Application Layer

* Use allowlists
* Validate filenames
* Restrict extensions
* Avoid direct path concatenation

### Operating System Layer

* Least privilege
* File permissions
* Isolated storage

### Infrastructure Layer

* Containerization
* Segmentation
* Monitoring

Multiple layers reduce risk.

---

# Understanding the Root Cause

Most Path Traversal payloads look simple.

However, understanding why they work requires understanding how operating systems resolve file paths.

The vulnerability exists because:

1. Applications access files using paths.

2. User input influences those paths.

3. Operating systems support parent-directory navigation.

4. Path normalization resolves traversal sequences.

5. The application accesses files outside the intended directory.

Once you understand directories, relative paths, normalization, and file access, Path Traversal becomes much easier to understand.

As a bug bounty hunter, don't focus on memorizing traversal payloads.

Focus on understanding how the application constructs and resolves file paths.

That's where the vulnerability actually lives.
