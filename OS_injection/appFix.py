from flask import Flask, request, render_template, send_from_directory
import subprocess
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "var", "www", "images")

os.makedirs(IMAGE_DIR, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/feedback", methods=["POST"])
def feedback():
    name = request.form.get("name", "")
    email = request.form.get("email", "")
    message = request.form.get("message", "")

    # SAFE:
    # No shell is involved and user input is passed as arguments.
    try:
        subprocess.run(
            ["echo", "Feedback from", name, f"({email}):", message],
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False
        )
    except Exception:
        pass

    return """
    <h2>Thank you for your feedback!</h2>
    <p>Your feedback has been submitted.</p>
    <a href="/">Back</a>
    """


@app.route("/images/<path:filename>")
def images(filename):
    return send_from_directory(IMAGE_DIR, filename)


if __name__ == "__main__":
    print("[+] Fixed application")
    print("[+] http://127.0.0.1:5000")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
