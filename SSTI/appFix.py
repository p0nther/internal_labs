from flask import Flask, request, render_template_string

app = Flask(__name__)

HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title> Fixed-Customer Portal</title>
</head>
<body>
    <h5>fixed</h5>

    <h1>Welcome, {{ name }}</h1>
    <p>{{ message }}</p>

    <hr>

    <form method="GET">
        <input name="name" placeholder="Your name">
        <input name="message" placeholder="Message">
        <button type="submit">Submit</button>
    </form>
</body>
<a href="/profile?username=p0nther">Profile </a>
<p></p>
 <a href="/search?q=don't implement user input directly in Template.">search </a>
</html>
"""


@app.route("/")
def home():
    value_name = request.args.get("name", "p0nther")
    value_message = request.args.get("message", "Welcome to our website")

    return render_template_string(
        HOME_TEMPLATE,
        name=value_name,
        message=value_message
    )


@app.route("/profile")
def profile():
    value_username = request.args.get("username", "guest")

    return render_template_string(
        """
        <h1>Profile</h1>
        <p>Username: {{ username }}</p>
        """,
        username=value_username
    )


@app.route("/search")
def search(): 
    value_query = request.args.get("q", "")

    return render_template_string(
        """
        <h1>Search Results</h1>
        <p>You searched for: {{ query }}</p>
        """,
        query=value_query
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False
    )
