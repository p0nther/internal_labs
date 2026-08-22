from flask import Flask, request, render_template_string
import os
import uuid
import imghdr

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
MAX_SIZE = 2 * 1024 * 1024

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

HTML = """
<h1>Secure Upload</h1>

<form method="POST" enctype="multipart/form-data">
    <input type="file" name="file">
    <button type="submit">Upload</button>
</form>

{% if msg %}
<p>{{msg}}</p>
{% endif %}
"""

ALLOWED_TYPES = {
    "jpeg",
    "png"
}

@app.route("/", methods=["GET", "POST"])
def upload():

    msg = ""

    if request.method == "POST":

        file = request.files.get("file")

        if not file:
            return render_template_string(
                HTML,
                msg="No file selected"
            )

        data = file.read()

        if len(data) > MAX_SIZE:
            return render_template_string(
                HTML,
                msg="File too large"
            )

        real_type = imghdr.what(
            None,
            data
        )

        if real_type not in ALLOWED_TYPES:

            return render_template_string(
                HTML,
                msg="Invalid image"
            )

        filename = (
            str(uuid.uuid4())
            + "."
            + real_type
        )

        path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        with open(path, "wb") as f:
            f.write(data)

        msg = f"Saved as {filename}"

    return render_template_string(
        HTML,
        msg=msg
    )

if __name__ == "__main__":
    app.run(
        debug=True,
        port=5001
    )
