# OS Command Injection — Complete Notes

When many bug bounty hunters first encounter OS Command Injection, they immediately start collecting payloads.

They memorize things like:

```text
; id
&& whoami
| cat /etc/passwd
$(id)
`whoami`
```

and start trying them everywhere.

But without understanding how applications execute operating system commands, OS Command Injection often feels like a collection of tricks rather than a real vulnerability.

In this article, we'll build the foundation first:

* What OS commands are
* Why applications execute system commands
* How command execution works
* How OS Command Injection happens
* Detecting OS Command Injection
* Blind Command Injection
* Common impacts
* Command chaining
* Why filters fail
* How developers can prevent it

---

# What Is an Operating System Command?

Operating systems provide commands that allow programs and users to interact with the system.

Examples:

Linux:

```bash
ls
pwd
whoami
id
cat
```

Windows:

```cmd
dir
whoami
type
ipconfig
```

Commands allow interaction with:

* Files
* Directories
* Processes
* Users
* Network interfaces
* System configuration

---

# Why Do Applications Execute Commands?

Many legitimate applications use system commands.

Examples:

* Ping utilities
* File conversion tools
* Backup systems
* Network diagnostics
* Media processing
* Compression utilities

Example:

A web application allows administrators to test connectivity.

User enters:

```text
google.com
```

The application runs:

```bash
ping google.com
```

and displays the result.

This functionality is completely legitimate.

Problems begin when user input becomes part of the command itself.

---

# Understanding Command Execution

Imagine the application receives:

```text
google.com
```

The backend might execute:

```python
import os

os.system(
    "ping " + host
)
```

Result:

```bash
ping google.com
```

The operating system executes the command.

Conceptually:

```text
User Input
     │
     ▼
Application
     │
     ▼
Operating System
     │
     ▼
Command Executed
```

---

# Introducing OS Command Injection

OS Command Injection occurs when:

* User input reaches a system command
* The application builds commands insecurely
* The operating system interprets attacker-controlled input

Example:

Application:

```bash
ping USER_INPUT
```

Normal Input:

```text
google.com
```

Generated Command:

```bash
ping google.com
```

Everything works normally.

---

Attacker Input:

```text
google.com; whoami
```

Generated Command:

```bash
ping google.com; whoami
```

Now the operating system executes:

```bash
ping google.com
```

and then:

```bash
whoami
```

The attacker has injected a second command.

---

# Why Does This Happen?

The root problem is simple.

Developers accidentally combine:

```text
User Data
```

with

```text
System Command
```

Instead of:

```python
safe_function(user_input)
```

they do:

```python
os.system(
    "ping " + user_input
)
```

The operating system receives attacker-controlled content.

---

# Understanding the Shell

Many command injection vulnerabilities involve a shell.

Examples:

Linux:

```bash
/bin/sh
/bin/bash
```

Windows:

```cmd
cmd.exe
```

The shell interprets special characters.

Examples:

```bash
;
&&
||
|
$
`
```

These characters have meaning to the shell.

The operating system processes them before executing commands.

---

# Basic Command Injection Flow

Normal:

```text
User Input
    │
    ▼
ping google.com
    │
    ▼
Ping Executes
```

Vulnerable:

```text
User Input
    │
    ▼
google.com; id
    │
    ▼
ping google.com; id
    │
    ▼
Two Commands Execute
```

The attacker changes the intended behavior.

---

# Detecting OS Command Injection

A good methodology is to move gradually.

---

## Step 1: Trigger an Error

Try input that may break command syntax.

Unexpected errors can indicate command processing.

Examples:

```text
'
"
\
```

Error messages sometimes reveal:

* Shell usage
* Underlying commands
* Operating system details

---

## Step 2: Test Command Chaining

Different operating systems support different separators.

Examples:

Linux:

```bash
;
&&
|
```

Windows:

```cmd
&
&&
|
```

Behavioral changes may indicate command execution.

---

## Step 3: Look for Output Reflection

Some applications return command output directly.

Example:

```bash
whoami
```

may appear inside the response.

This often confirms exploitation immediately.

---

# Common Impacts

OS Command Injection is often severe because the attacker interacts with the operating system itself.

Potential impacts include:

* File disclosure
* User enumeration
* Environment variable access
* Internal network access
* Service discovery
* Application compromise
* Full server compromise

Conceptually:

```text
OS Command Injection
          │
          ▼
Operating System Access
          │
          ▼
High Impact
```

---

# Blind Command Injection

Sometimes commands execute successfully, but output is hidden.

Example:

```python
os.system(command)

return "Success"
```

The command runs.

The response never contains the result.

This situation is called:

**Blind Command Injection**

---

# Detecting Blind Command Injection

Instead of looking for output, testers look for side effects.

Examples:

### Time-Based Effects

If execution time changes unexpectedly:

```text
Request
   │
   ▼
Command Executes
   │
   ▼
Longer Response Time
```

This may indicate command execution.

---

### External Interactions

The vulnerable server may:

```text
Execute Command
       │
       ▼
Contact External System
       │
       ▼
Attacker Observes Activity
```

This can confirm exploitation even when no output is visible.

---

# Command Chaining

Operating systems support executing multiple commands.

Conceptually:

```bash
command1
command2
command3
```

The shell can process them sequentially.

This behavior is exactly what attackers abuse.

Conceptually:

```text
Original Command
       │
       ▼
Injected Separator
       │
       ▼
Attacker Command
```

---

# Why Blacklists Often Fail

Developers sometimes block specific characters.

Example:

```python
if ";" in user_input:
    reject()
```

Unfortunately, shells often provide multiple ways to achieve similar behavior.

Blocking a few characters rarely solves the problem completely.

The root problem remains:

```text
Attacker Controls Command
```

instead of:

```text
Attacker Controls Data
```

---

# OS Command Injection vs Code Injection

Many beginners confuse these vulnerabilities.

OS Command Injection:

```text
Application
    │
    ▼
Operating System Command
```

Code Injection:

```text
Application
    │
    ▼
Programming Language Runtime
```

Command Injection targets the operating system.

Code Injection targets the application's programming language.

---

# Vulnerable Python Example

```python
import os
from flask import request

host = request.args.get("host")

os.system(
    "ping -c 1 " + host
)
```

Problem:

User input becomes part of the command.

The operating system interprets it.

---

# More Secure Python Example

Instead of building a shell command:

```python
import subprocess

subprocess.run(
    ["ping", "-c", "1", host]
)
```

Why is this safer?

The operating system receives:

```text
Argument 1 = ping
Argument 2 = -c
Argument 3 = 1
Argument 4 = host
```

The shell is not involved.

Special shell characters are not interpreted as commands.

Additional validation should still be applied.

---

# Defense in Depth

Good protection combines multiple controls.

### Application Layer

* Input validation
* Allowlists
* Safe APIs

### System Layer

* Least privilege
* Restricted accounts
* Sandboxing

### Infrastructure Layer

* Network segmentation
* Monitoring
* Process isolation

Multiple layers reduce risk.

---

# Understanding the Root Cause

Most command injection payloads look simple.

However, understanding why they work requires understanding how applications execute operating system commands.

The vulnerability exists because:

1. Applications execute system commands.

2. User input becomes part of those commands.

3. The shell interprets special characters.

4. Additional commands are executed.

5. The attacker gains control over operating system functionality.

Once you understand command execution, shell parsing, process creation, and user-controlled input, OS Command Injection becomes much easier to understand.

As a bug bounty hunter, don't focus on memorizing payloads.

Focus on understanding how the application builds and executes commands.

That's where the vulnerability actually lives.
