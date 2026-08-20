from flask import Flask, request, render_template_string
import pickle
import base64

app = Flask(__name__)

HTML = """
<h1>Insecure Deserialization Lab</h1>

<form method="POST">
    <textarea name="data" rows="10" cols="80"></textarea><br><br>
    <button type="submit">Import Profile</button>
</form>

{% if result %}
<hr>
<h3>Deserialized Object:</h3>
<pre>{{ result }}</pre>
{% endif %}
"""

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""

    if request.method == "POST":
        try:
            data = request.form.get("data", "")

            decoded = base64.b64decode(data)

            # VULNERABLE
            obj = pickle.loads(decoded)

            result = repr(obj)

        except Exception as e:
            result = f"Error: {e}"

    return render_template_string(HTML, result=result)

if __name__ == "__main__":
    app.run(debug=True,port=5000)
