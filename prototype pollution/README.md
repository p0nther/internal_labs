# Prototype Pollution — Complete Notes

When many bug bounty hunters first encounter Prototype Pollution, they immediately start searching for payloads.

They memorize things like:

```json
{
  "__proto__": {
    "isAdmin": true
  }
}
```

or:

```http
?__proto__[isAdmin]=true
```

and start throwing them at every JavaScript application they find.

But without understanding how JavaScript prototypes actually work, Prototype Pollution often feels confusing.

In this article, we'll build the concept from the ground up and understand:

* What prototypes are
* Why JavaScript uses them
* What Prototype Pollution is
* How pollution occurs
* Common attack vectors
* Impact
* Detection methodology
* Secure coding practices

---

# What Is A Prototype?

In JavaScript, almost everything is an object.

Example:

```javascript
const user = {
    name: "p0nther"
};
```

Objects can inherit properties from other objects.

Example:

```javascript
const user = {};

console.log(user.toString());
```

Even though:

```javascript
user.toString
```

does not exist directly.

JavaScript finds it through:

```text
Object Prototype
```

---

# Why Do Prototypes Exist?

Without prototypes:

```javascript
const user1 = {
    login() {}
};

const user2 = {
    login() {}
};

const user3 = {
    login() {}
};
```

Every object would need its own copy.

Instead:

```javascript
User.prototype.login = function(){};
```

All objects share:

```text
login()
```

saving memory.

---

# Prototype Chain

Example:

```javascript
const user = {
    name: "p0nther"
};
```

Lookup process:

```text
user.name
   │
   ▼
Found Directly
```

But:

```javascript
user.toString()
```

becomes:

```text
user
  │
  ▼
Object.prototype
  │
  ▼
toString()
```

This chain is called:

```text
Prototype Chain
```

---

# Object.prototype

At the top sits:

```javascript
Object.prototype
```

Almost every JavaScript object inherits from it.

Example:

```javascript
const a = {};
const b = {};
```

Both inherit:

```text
Object.prototype
```

If we modify:

```javascript
Object.prototype
```

the change appears everywhere.

---

# What Is Prototype Pollution?

Prototype Pollution occurs when attacker-controlled input modifies:

```javascript
Object.prototype
```

or another shared prototype.

Instead of:

```javascript
obj.username = "p0nther";
```

the attacker injects:

```javascript
__proto__.isAdmin = true;
```

which becomes:

```javascript
Object.prototype.isAdmin = true;
```

Now:

```javascript
({}).isAdmin
```

returns:

```javascript
true
```

for every object.

---

# Why Is This Dangerous?

Normal object:

```javascript
const user = {};
```

Expected:

```javascript
user.isAdmin
```

↓

```text
undefined
```

After pollution:

```javascript
Object.prototype.isAdmin = true;
```

Now:

```javascript
user.isAdmin
```

↓

```text
true
```

The application never intended this.

---

# Vulnerable Example

Developer writes:

```javascript
function merge(target, source){

    for(let key in source){
        target[key] = source[key];
    }

    return target;
}
```

Looks harmless.

Application receives:

```json
{
  "__proto__": {
      "isAdmin": true
  }
}
```

Merge executes:

```javascript
target["__proto__"] = {
    isAdmin: true
};
```

Result:

```javascript
Object.prototype.isAdmin = true;
```

Prototype polluted.

---

# How Pollution Happens

```text
Attacker Input
      │
      ▼
Unsafe Merge
      │
      ▼
__proto__
      │
      ▼
Object.prototype
      │
      ▼
Entire Application Affected
```

---

# Common Pollution Properties

Most common:

```javascript
__proto__
```

---

Also:

```javascript
constructor
```

---

And:

```javascript
prototype
```

---

Attackers often target:

```javascript
constructor.prototype
```

because some filters block:

```javascript
__proto__
```

---

# Basic Payload

JSON:

```json
{
  "__proto__": {
    "isAdmin": true
  }
}
```

---

Query String:

```http
?__proto__[isAdmin]=true
```

---

Nested:

```json
{
  "constructor": {
      "prototype": {
          "isAdmin": true
      }
  }
}
```

---

# Realistic Vulnerable Code

```javascript
app.post("/update", (req,res)=>{

    const defaults = {
        theme: "light"
    };

    Object.assign(
        defaults,
        req.body
    );

    res.send("updated");
});
```

Attacker sends:

```json
{
  "__proto__": {
      "isAdmin": true
  }
}
```

Result:

```javascript
({}).isAdmin
```

↓

```javascript
true
```

---

# Access Control Bypass

Imagine:

```javascript
if(user.isAdmin){
    showAdminPanel();
}
```

Developer expects:

```javascript
user.isAdmin
```

to exist only for admins.

After pollution:

```javascript
Object.prototype.isAdmin = true;
```

Every object appears to be admin.

Flow:

```text
Prototype Pollution
         │
         ▼
isAdmin=true
         │
         ▼
Authorization Bypass
```

---

# Server-Side Prototype Pollution (SSPP)

Pollution can happen on the server.

Example:

```javascript
Node.js
Express
NestJS
```

Attacker pollutes:

```javascript
Object.prototype
```

and influences server logic.

Potential outcomes:

* Authentication bypass
* Application crashes
* SSRF
* RCE chains

---

# Client-Side Prototype Pollution

Browser JavaScript:

```javascript
Object.prototype.debug = true;
```

may affect:

* Frontend logic
* Security checks
* Rendering behavior

Sometimes leading to:

```text
DOM XSS
```

---

# From Pollution To XSS

Application:

```javascript
if(config.escapeHtml){
    sanitize();
}
```

Developer assumes:

```javascript
config.escapeHtml
```

is always:

```javascript
true
```

Attacker pollutes:

```javascript
{
  "__proto__": {
      "escapeHtml": false
  }
}
```

Result:

```text
Sanitization Disabled
         │
         ▼
XSS
```

---

# From Pollution To SSRF

Application:

```javascript
fetch(
    url,
    options
);
```

Options:

```javascript
{
   timeout: 1000
}
```

Attacker pollutes:

```javascript
{
 "__proto__": {
    hostname: "169.254.169.254"
 }
}
```

Depending on implementation:

```text
Prototype Pollution
         │
         ▼
Request Manipulation
         │
         ▼
SSRF
```

---

# From Pollution To RCE

Pollution alone usually is NOT RCE.

Instead:

```text
Prototype Pollution
        │
        ▼
Dangerous Gadget
        │
        ▼
Code Execution
```

A gadget is code that uses polluted properties in a dangerous way.

---

# Common Sources

## Deep Merge Functions

Example:

```javascript
merge(a,b)
```

---

## Object.assign()

```javascript
Object.assign()
```

---

## lodash.merge()

Historically involved in multiple Prototype Pollution vulnerabilities.

---

## qs Library

Parsing:

```http
?__proto__[x]=1
```

into objects.

---

## YAML Parsers

User-controlled nested objects sometimes lead to pollution.

---

# Detection Methodology

## 1. Find Object Merge Operations

Search for:

```javascript
Object.assign(
```

---

```javascript
merge(
```

---

```javascript
lodash.merge(
```

---

## 2. Send Test Payload

```json
{
  "__proto__": {
      "polluted": "YES"
  }
}
```

---

## 3. Look For Reflection

Application later outputs:

```javascript
{}.polluted
```

↓

```text
YES
```

---

## 4. Search For Gadgets

Ask:

```text
What uses polluted properties?
```

Examples:

* Authentication
* URL generation
* File access
* Template rendering

---

## 5. Escalate Impact

```text
Pollution
     │
     ▼
Gadget
     │
     ▼
XSS / SSRF / RCE
```

---

# Example Detection Payloads

Basic:

```json
{
 "__proto__": {
   "test":"polluted"
 }
}
```

---

Alternative:

```json
{
 "constructor":{
   "prototype":{
      "test":"polluted"
   }
 }
}
```

---

Query String:

```http
?__proto__[test]=polluted
```

---

# Impact

## Access Control Bypass

```text
Prototype Pollution
       │
       ▼
isAdmin=true
       │
       ▼
Admin Access
```

---

## DOM XSS

```text
Prototype Pollution
       │
       ▼
Security Logic Broken
       │
       ▼
XSS
```

---

## SSRF

```text
Prototype Pollution
       │
       ▼
Request Manipulation
       │
       ▼
SSRF
```

---

## Remote Code Execution

```text
Prototype Pollution
       │
       ▼
Dangerous Gadget
       │
       ▼
RCE
```

---

# Secure Example

Unsafe:

```javascript
Object.assign(
    defaults,
    userInput
);
```

Safer:

```javascript
const allowed = {
    theme: userInput.theme
};
```

Explicitly copy only expected fields.

---

# Additional Defenses

## Block Dangerous Keys

Reject:

```javascript
__proto__
```

---

Reject:

```javascript
prototype
```

---

Reject:

```javascript
constructor
```

---

## Use Null Prototypes

```javascript
const obj = Object.create(null);
```

No inherited prototype.

---

## Upgrade Vulnerable Libraries

Many historical Prototype Pollution bugs existed in:

```text
lodash
qs
hoek
minimist
```

---

## Validate Input

Whitelist:

```javascript
theme
language
timezone
```

instead of accepting arbitrary keys.

---

# Quick Summary

Prototype:

* JavaScript inheritance mechanism.

Prototype Pollution:

* Attacker modifies shared prototypes.

Common Targets:

```javascript
__proto__
constructor.prototype
prototype
```
______
In JavaScript, `Object.prototype` is the **master blueprint** that almost every single object in JavaScript inherits from.

When you write `Object.prototype.anything = "hello"`, you are adding a property called `anything` directly to that master blueprint. Because of how JavaScript looks up properties, **every object in your entire application will now act as if it has `anything: "hello"**`, unless it defined its own property with that name first.

---

### 1. How JavaScript Looks Up Properties (The Prototype Chain)

When you ask JavaScript for `myObject.anything`, it follows a simple search path:

1. **Step 1:** Does `myObject` have a property named `anything` directly on itself?
* *Yes:* Return that value.
* *No:* Go look at `myObject.__proto__` (which points to `Object.prototype`).


2. **Step 2:** Does `Object.prototype` have a property named `anything`?
* *Yes:* Return that value.
* *No:* Return `undefined`.



---

### 2. A Concrete Code Example

```javascript
// Step 1: Object prototype is normal
let user = {};
console.log(user.anything); // Output: undefined

// Step 2: Pollute the master blueprint
Object.prototype.anything = "POLLUTED";

// Step 3: Check ANY object (even newly created ones or existing ones)
let admin = {};
let config = { timeout: 1000 };

console.log(admin.anything);  // Output: "POLLUTED"
console.log(config.anything); // Output: "POLLUTED"

```

Notice that we never added `anything` to `admin` or `config`. They inherited it automatically from `Object.prototype`.

---

### 3. Why This Causes Security Vulnerabilities (RCE / Privilege Escalation)

Developers often write code that relies on **optional properties** or **fallback default values** using `if` checks or logical OR (`||`):

```javascript
// Developer code inside a server function:
function checkAccess(user) {
    // If user.isAdmin is not defined on the object, 
    // JS checks Object.prototype.isAdmin
    if (user.isAdmin) { 
        grantAdminAccess();
    }
}

```

* **Normal state:** `user.isAdmin` is `undefined` (falsy), so access is denied.
* **Polluted state (`Object.prototype.isAdmin = true`):** Every empty object `{}` now evaluates `user.isAdmin` as `true`. Every user becomes an admin instantly.
Common Sources:

* Deep merge functions
* Object.assign()
* Vulnerable libraries

Possible Impacts:

* Access Control Bypass
* DOM XSS
* SSRF
* RCE (through gadgets)

Defenses:

* Block dangerous keys
* Whitelist fields
* Use Object.create(null)
* Update vulnerable libraries
* Avoid unsafe object merging
