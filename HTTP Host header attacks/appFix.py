from flask import Flask, request, render_template_string

app = Flask(__name__)

TRUSTED_HOST = "127.0.0.1:5000"

last_reset_link = ""

HTML = """
<h1>Fixed Version</h1>

<form method="POST" action="/forgot">
    <input name="email">
    <button type="submit">Reset Password</button>
</form>

<hr>

<pre>{{ link }}</pre>
"""

@app.route("/")
def home():
    return render_template_string(
        HTML,
        link=last_reset_link
    )

@app.route("/forgot", methods=["POST"])
def forgot():

    global last_reset_link

    email = request.form.get("email")

    reset_token = "ABC123"

    # FIX:
    last_reset_link = (
        f"http://{TRUSTED_HOST}/reset?token={reset_token}"
    )

    return f"""
    Password reset email sent to {email}<br><br>
    Generated Link:<br>
    {last_reset_link}
    """

@app.route("/reset")
def reset():
    return "Password reset page"

if __name__ == "__main__":
    app.run(debug=True)
