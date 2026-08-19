from flask import Flask, request, send_file
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, "files")

@app.route("/")
def home():
    return """
    <h1>Vuln Path Traversal Lab</h1>

    <p>Try:</p>
   
    <ul>
        <a href="/download?file=cat.jpg">cat image</a>
        <p> </p>
        <a href="/download?file=dog.jpg">dog image</a>
    </ul>
    """


@app.route("/download")
def download():
    filename = request.args.get("file")

    if not filename:
        return "Missing file parameter", 400

    path = os.path.join(FILES_DIR, filename)

    return send_file(path)

if __name__ == "__main__":
    app.run(debug=True)
