from flask import Flask, request, render_template, send_from_directory
import subprocess
import os

app = Flask(__name__)

# Writable directory used by the application
IMAGE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "var",
    "www",
    "images"
)

os.makedirs(IMAGE_DIR, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/feedback", methods=["POST"])
def feedback():
    name = request.form.get("name", "")
    email = request.form.get("email", "")
    message = request.form.get("message", "")

    # ---------------------------------------------------------
    # INTENTIONALLY VULNERABLE
    #
    # User input is inserted directly into a shell command.
    # The command output is NOT returned to the user.
    # ---------------------------------------------------------

    command = f"echo 'Feedback from {name} ({email}): {message}'"

    try:
        subprocess.run(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5
        )
    except Exception:
        pass

    return """
    <html>
        <body>
            <h2>Thank you for your feedback!</h2>
            <p>Your feedback has been submitted.</p>
            <a href="/">Back</a>
        </body>
    </html>
    """


@app.route("/images/<path:filename>")
def images(filename):
    # The application serves files from the writable directory.
    return send_from_directory(IMAGE_DIR, filename)


if __name__ == "__main__":
    print("[+] Blind OS Command Injection Lab")
    print(f"[+] Writable directory: {IMAGE_DIR}")
    print("[+] Server: http://127.0.0.1:5000")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
