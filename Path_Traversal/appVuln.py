import os
from flask import Flask, request, send_from_directory, abort

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Ensure the directory exists so Flask doesn't throw an error
FILES_DIR = os.path.join(BASE_DIR, "files")
os.makedirs(FILES_DIR, exist_ok=True)

@app.route("/")
def home():
    return """
    <h1>Fixed Path Traversal Lab</h1>
    <p>Try:</p>
    <ul>
        <li><a href="/download?file=cat.jpg">cat image</a></li>
        <li><a href="/download?file=dog.jpg">dog image</a></li>
    </ul>
    """

@app.route("/download")
def download():
    filename = request.args.get("file")

    if not filename:
        return "Missing file parameter", 400

    try:
        # send_from_directory automatically blocks '..' and absolute path hacks
        return send_from_directory(FILES_DIR, filename)
    except ValueError:
        return "File not found", 404

if __name__ == "__main__":
    app.run(port=5000, debug=True)
