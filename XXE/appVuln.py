from flask import Flask, request
from lxml import etree
import requests

app = Flask(__name__)

CALLBACK = "http://127.0.0.1:5000/callback"


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>XXE Training Lab</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 60px auto;
                text-align: center;
                background: #111;
                color: white;
            }

            .container {
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
                margin-top: 40px;
            }

            .button {
                display: inline-block;
                padding: 20px 35px;
                background: #222;
                color: white;
                text-decoration: none;
                border: 1px solid #555;
                border-radius: 8px;
                font-size: 18px;
            }

            .button:hover {
                background: #444;
            }
        </style>
    </head>

    <body>

        <h1>XXE Training Lab</h1>

        <p>Select an XXE technique</p>

        <div class="container">

            <a class="button" href="/internal">
                Internal XXE
            </a>

            <a class="button" href="/external">
                External XXE
            </a>

            <a class="button" href="/parameter">
                Parameter Entity
            </a>

        </div>

    </body>
    </html>
    """


# ============================================================
# INTERNAL XXE PAGE
# ============================================================

@app.route("/internal", methods=["GET"])
def internal_page():
    return """
    <h1>Internal Entity XXE</h1>

    <form method="POST" action="/internal">

        <textarea
            name="xml"
            rows="15"
            cols="80"
            placeholder="Paste XML here..."
        ></textarea>

        <br><br>

        <button type="submit">
            Parse XML
        </button>

    </form>

    <br>
    <a href="/">← Back</a>
    """


# ============================================================
# INTERNAL XXE PARSER
# ============================================================

@app.route("/internal", methods=["POST"])
def internal_entity():

    xml = request.form.get("xml", "").encode()

    try:

        parser = etree.XMLParser(
            load_dtd=True,
            resolve_entities=True,
            no_network=True
        )

        root = etree.fromstring(xml, parser)

        return f"""
        <h1>Result</h1>

        <pre>
{etree.tostring(root, pretty_print=True).decode()}
        </pre>

        <a href="/internal">← Back</a>
        """

    except Exception as e:

        return f"""
        <h1>Parser Error</h1>

        <pre>{e}</pre>

        <a href="/internal">← Back</a>
        """, 400


# ============================================================
# EXTERNAL ENTITY RESOLVER
# ============================================================

class ControlledResolver(etree.Resolver):

    def resolve(self, url, public_id, context):

        print(f"\n[XXE] External entity requested:")
        print(f"      {url}")

        # Only allow our local controlled callback.
    
        try:

            response = requests.get(
                url,
                timeout=5
            )

            print(
                f"[+] Callback response: "
                f"{response.status_code}"
            )

            return self.resolve_string(
                response.text,
                context
            )

        except Exception as e:

            print(f"[-] Request failed: {e}")

            return self.resolve_string(
                "",
                context
            )


# ============================================================
# EXTERNAL XXE PAGE
# ============================================================

@app.route("/external", methods=["GET"])
def external_page():

    return """
    <h1>External Entity XXE</h1>

    <form method="POST" action="/external">

        <textarea
            name="xml"
            rows="15"
            cols="80"
            placeholder="Paste XML here..."
        ></textarea>

        <br><br>

        <button type="submit">
            Parse XML
        </button>

    </form>

    <br>

    <a href="/">← Back</a>
    """


# ============================================================
# EXTERNAL XXE PARSER
# ============================================================

@app.route("/external", methods=["POST"])
def external_entity():

    xml = request.form.get("xml", "").encode()

    try:

        parser = etree.XMLParser(
            load_dtd=True,
            resolve_entities=True
        )

        parser.resolvers.add(
            ControlledResolver()
        )

        root = etree.fromstring(
            xml,
            parser
        )

        return f"""
        <h1>Result</h1>

        <pre>
{etree.tostring(root, pretty_print=True).decode()}
        </pre>

        <a href="/external">← Back</a>
        """

    except Exception as e:

        return f"""
        <h1>Parser Error</h1>

        <pre>{e}</pre>

        <a href="/external">← Back</a>
        """, 400


# ============================================================
# PARAMETER ENTITY PAGE
# ============================================================

@app.route("/parameter", methods=["GET"])
def parameter_page():

    return """
    <h1>Parameter Entity XXE</h1>

    <form method="POST" action="/parameter">

        <textarea
            name="xml"
            rows="15"
            cols="80"
            placeholder="Paste XML here..."
        ></textarea>

        <br><br>

        <button type="submit">
            Parse XML
        </button>

    </form>

    <br>

    <a href="/">← Back</a>
    """


# ============================================================
# PARAMETER ENTITY PARSER
# ============================================================

@app.route("/parameter", methods=["POST"])
def parameter_entity():

    xml = request.form.get("xml", "").encode()

    try:

        parser = etree.XMLParser(
            load_dtd=True,
            resolve_entities=True,
            no_network=True
        )

        root = etree.fromstring(
            xml,
            parser
        )

        return f"""
        <h1>Result</h1>

        <pre>
{etree.tostring(root, pretty_print=True).decode()}
        </pre>

        <a href="/parameter">← Back</a>
        """

    except Exception as e:

        return f"""
        <h1>Parser Error</h1>

        <pre>{e}</pre>

        <a href="/parameter">← Back</a>
        """, 400


# ============================================================
# OOB CALLBACK
# ============================================================

@app.route("/callback")
def callback():

    print("\n================================")
    print("[+] OOB CALLBACK RECEIVED")
    print("================================")

    print("\nHeaders:")

    for key, value in request.headers.items():

        print(f"{key}: {value}")

    return "XXE callback received"


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print("""
========================================
        XXE TRAINING LAB
========================================

[*] Home:
    http://127.0.0.1:5000/

[*] Internal:
    http://127.0.0.1:5000/internal

[*] External:
    http://127.0.0.1:5000/external

[*] Parameter:
    http://127.0.0.1:5000/parameter

[*] Callback:
    http://127.0.0.1:5000/callback

========================================
    """)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
