from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route("/")
def home():
    name = request.args.get("name", "p0nther")
    message = request.args.get("message", "Welcome to our website")

    # INTENTIONALLY VULNERABLE:
    # Both parameters become part of the template itself.
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vuln-Customer Portal</title>
    </head>
    <body>
	<h5>Vuln</h5>
        <h1>Welcome, {name}</h1>
        <p>{message}</p>

        <hr>

        <form method="GET">
            <input name="name" placeholder="Your name">
            <input name="message" placeholder="Message">
            <button type="submit">Submit</button>
        </form>
    </body>
    <a href="/profile?username=p0nther">Profile </a>
     <p></p>
    <a href="/search?q=how to fix this bug,">search </a>
    </html>
    """

    return render_template_string(template)


@app.route("/profile")
def profile():
    username = request.args.get("username", "guest")

    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Profile</title>
    </head>
    <body>
        <h1>Profile</h1>
        <p>Username: {username}</p>
    </body>
    </html>
    """

    return render_template_string(template)


@app.route("/search")
def search():
    query = request.args.get("q", "")

    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Search</title>
    </head>
    <body>
        <h1>Search Results</h1>
        <p>You searched for: {query}</p>
    </body>
    </html>
    """

    return render_template_string(template)


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
