# SSTI (Server-Side Template Injection) — Complete Notes

When many bug bounty hunters first encounter SSTI (Server-Side Template Injection), they immediately start collecting payloads.

They memorize things like:

```text
{{7*7}}
{{config}}
{{self}}
${7*7}
<%= 7*7 %>
```

and start trying them everywhere.

But without understanding how template engines actually work, SSTI often feels like magic.

In this article, we'll build the foundation first:

* What template engines are
* Why developers use them
* How templates are rendered
* What user input does inside templates
* How SSTI vulnerabilities happen
* Detecting SSTI
* Exploiting SSTI
* Common impacts
* How developers can prevent it

---

# What Is a Template Engine?

Modern web applications generate HTML dynamically.

Instead of manually building every page, developers use **template engines**.

A template engine combines:

```text
Template
     +
Application Data
     =
Final HTML
```

For example:

Template:

```html
<h1>Hello {{ name }}</h1>
```

Application Data:

```python
name = "p0nther"
```

Final Output:

```html
<h1>Hello p0nther</h1>
```

The template engine replaces placeholders with actual values.

---

# Why Do Developers Use Templates?

Imagine an e-commerce website.

Without templates:

```html
<h1>Product 1</h1>
```

```html
<h1>Product 2</h1>
```

```html
<h1>Product 3</h1>
```

Thousands of pages would need to be created manually.

Instead:

```html
<h1>{{ product_name }}</h1>
```

The application simply changes the value.

Templates make websites scalable and maintainable.

---

# Understanding Template Rendering

Most template engines follow a process similar to:

```text
Template
    │
    ▼
Variables Inserted
    │
    ▼
Template Rendered
    │
    ▼
HTML Generated
    │
    ▼
Sent To Browser
```

Example:

Template:

```html
<h1>Welcome {{ username }}</h1>
```

Data:

```python
username = "Abdarhman"
```

Output:

```html
<h1>Welcome Abdarhman</h1>
```

Everything works exactly as intended.

---

# What Can Templates Contain?

Templates are often more powerful than simple variable replacement.

Many template engines support:

* Variables
* Loops
* Conditions
* Filters
* Functions
* Expressions

Example:

```html
{% if admin %}
<h1>Administrator</h1>
{% endif %}
```

Example:

```html
{{ 10 + 5 }}
```

Output:

```html
15
```

This means templates are capable of executing logic.

That capability is what makes SSTI dangerous.

---

# Introducing SSTI

SSTI stands for:

**Server-Side Template Injection**

It occurs when:

* User input reaches a template
* The input is treated as template code
* The template engine evaluates it

Instead of being displayed as text:

```text
{{7*7}}
```

the template engine interprets it.

Result:

```text
49
```

The attacker has injected template syntax into server-side rendering logic.

---

# Safe vs Dangerous Behavior

Safe:

```python
render_template(
    "profile.html",
    username=user_input
)
```

Template:

```html
<h1>{{ username }}</h1>
```

User Input:

```text
{{7*7}}
```

Output:

```html
<h1>{{7*7}}</h1>
```

The payload is treated as plain text.

---

Dangerous:

```python
template = f"""
<h1>{user_input}</h1>
"""

render_template_string(template)
```

User Input:

```text
{{7*7}}
```

Generated Template:

```html
<h1>{{7*7}}</h1>
```

Now the template engine evaluates it.

Output:

```html
<h1>49</h1>
```

SSTI confirmed.

---

# Why Does SSTI Happen?

The root cause is simple.

Developers accidentally mix:

```text
User Input
```

with

```text
Template Code
```

Instead of passing data safely:

```python
render_template(
    "page.html",
    name=user_input
)
```

they build templates dynamically:

```python
render_template_string(
    user_input
)
```

or

```python
template += user_input
```

Now the attacker controls part of the template itself.

---

# Understanding the Vulnerability

Think of a template engine as a mini programming language.

Normal flow:

```text
Developer Writes Template
           │
           ▼
Template Engine Executes It
```

Vulnerable flow:

```text
Attacker Controls Template
           │
           ▼
Template Engine Executes It
```

The engine cannot distinguish between developer code and attacker code.

It executes both.

---

# Detecting SSTI

A good methodology is to move gradually.

---

## Step 1: Test Arithmetic

Try simple expressions.

Examples:

```text
{{7*7}}
```

```text
${7*7}
```

```text
<%=7*7%>
```

If the result changes:

```text
49
```

instead of:

```text
{{7*7}}
```

the input may be evaluated.

---

## Step 2: Identify the Template Engine

Different template engines use different syntax.

Examples:

| Engine     | Syntax |
| ---------- | ------ |
| Jinja2     | {{ }}  |
| Twig       | {{ }}  |
| Smarty     | { }    |
| Freemarker | ${ }   |
| ERB        | <%= %> |

Identifying the engine helps determine possible attack paths.

---

## Step 3: Explore Context

Template engines usually expose objects.

Examples may include:

```text
config
request
session
application
```

Access to internal objects often reveals sensitive information.

---

# What Can Attackers Access?

Depending on the engine, attackers may access:

* Application settings
* Environment variables
* Debug information
* Source code
* Internal objects
* Framework functionality

Conceptually:

```text
Template Context
      │
      ▼
Sensitive Objects
      │
      ▼
Information Disclosure
```

---

# SSTI to Information Disclosure

One common impact is leaking application data.

Example targets:

* API keys
* Database credentials
* Secret tokens
* Configuration values

Conceptually:

```text
SSTI
 │
 ▼
Access Internal Objects
 │
 ▼
Read Sensitive Data
```

---

# SSTI to Remote Code Execution

In some template engines, attackers can eventually reach dangerous functionality.

Conceptually:

```text
SSTI
 │
 ▼
Template Engine
 │
 ▼
Underlying Language Objects
 │
 ▼
System Interaction
 │
 ▼
Remote Code Execution
```

The exact technique depends heavily on:

* Template engine
* Framework
* Programming language
* Sandbox restrictions

---

# Blind SSTI

Sometimes the output is not reflected.

Example:

```text
Input Processed
      │
      ▼
Template Evaluated
      │
      ▼
Output Hidden
```

The payload executes.

But the attacker cannot directly see the result.

This situation is called:

**Blind SSTI**

---

# Detecting Blind SSTI

Instead of looking for reflected output, testers often look for side effects.

Examples:

* Response delays
* Error messages
* External interactions
* Behavioral changes

Conceptually:

```text
Injected Template
        │
        ▼
Executed Server Side
        │
        ▼
Observable Effect
```

---

# Common Places SSTI Appears

SSTI often appears in features involving:

* Email templates
* PDF generation
* Notification systems
* CMS platforms
* Reporting systems
* Dynamic themes
* User-customizable templates

Anywhere users influence template content becomes a potential target.

---

# Vulnerable Python Example

Using Flask and Jinja2:

```python
from flask import request
from flask import render_template_string

name = request.args.get("name")

template = f"""
<h1>Hello {name}</h1>
"""

return render_template_string(
    template
)
```

Problem:

The attacker controls part of the template itself.

---

# Secure Python Example

```python
from flask import render_template

return render_template(
    "profile.html",
    username=name
)
```

Template:

```html
<h1>Hello {{ username }}</h1>
```

Why is this safe?

The user controls:

```text
username
```

but does not control:

```text
template syntax
```

The engine treats the value as data rather than executable template code.

---

# Preventing SSTI

The safest approach is simple:

Never allow users to control templates.

Good practices:

* Treat user input as data
* Avoid dynamic template generation
* Avoid rendering user-supplied templates
* Use sandboxing where available
* Keep template engines updated
* Restrict dangerous functionality

---

# Understanding the Root Cause

Most SSTI payloads look simple.

However, understanding why they work requires understanding template engines.

The vulnerability exists because:

1. Template engines execute template logic.

2. Templates are effectively code.

3. User input reaches the template itself.

4. The engine evaluates attacker-controlled content.

5. The attacker gains access to template functionality.

Once you understand template rendering, execution flow, template context, and engine behavior, SSTI becomes much easier to understand.

As a bug bounty hunter, don't focus on memorizing payloads.

Focus on understanding how the template engine processes data.

That's where the vulnerability actually lives.
