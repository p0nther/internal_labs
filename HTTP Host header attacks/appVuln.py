from flask import Flask, request, render_template_string

app = Flask(__name__)

last_reset_link = ""

HTML = """
<h1>HTTP Host Header Attack Lab</h1>

<h2>Request Password Reset</h2>

<form method="POST" action="/forgot">
    <input name="email" placeholder="victim@example.com">
    <button type="submit">Reset Password</button>
</form>

<hr>

<h3>Last Generated Reset Link</h3>
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

    # VULNERABLE
    host = request.headers.get("Host")

    reset_token = "ABC123"

    last_reset_link = (
        f"http://{host}/reset?token={reset_token}"
    )

    return f"""
    Password reset email sent to {email}<br><br>
    Generated Link:<br>
    {last_reset_link}
    """

@app.route("/reset")
def reset():
    token = request.args.get("token")
    return f"Reset page. Token = {token}"

if __name__ == "__main__":
    app.run(debug=True)
