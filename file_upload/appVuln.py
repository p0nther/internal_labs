from flask import Flask, request, render_template_string, send_from_directory
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML = """
<h1>Upload Profile Picture</h1>

<form method="POST" enctype="multipart/form-data">
    <input type="file" name="file">
    <button type="submit">Upload</button>
</form>

{% if msg %}
<p>{{ msg }}</p>
{% endif %}

<hr>

<h3>Uploaded Files</h3>

{% for f in files %}
<a href="/uploads/{{f}}">{{f}}</a><br>
{% endfor %}
"""

@app.route("/", methods=["GET", "POST"])
def upload():

    msg = ""

    if request.method == "POST":

        file = request.files.get("file")

        if not file:
            msg = "No file selected"

        else:

            filename = file.filename

            # VULNERABLE
            # Trusts extension only
            if filename.endswith(".jpg") or filename.endswith(".png"):

                path = os.path.join(
                    UPLOAD_FOLDER,
                    filename
                )

                file.save(path)

                msg = f"Uploaded: {filename}"

            else:
                msg = "Only jpg/png allowed"

    files = os.listdir(UPLOAD_FOLDER)

    return render_template_string(
        HTML,
        msg=msg,
        files=files
    )

@app.route("/uploads/<path:name>")
def files(name):
    return send_from_directory(
        UPLOAD_FOLDER,
        name
    )

if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )
