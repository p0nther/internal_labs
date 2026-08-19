from flask import Flask
import time

app = Flask(__name__)

cache = {}

TRUSTED_HOST = "cdn.example.com"

@app.route("/")
def home():
    path = request.path

    if path in cache:
        return cache[path]

    response = f"""
    <html>
        <head>
            <script src="https://{TRUSTED_HOST}/app.js"></script>
        </head>
        <body>
            <h1>Welcome</h1>
            <p>Generated at {time.time()}</p>
        </body>
    </html>
    """

    cache[path] = response

    return response

@app.route("/clear-cache")
def clear_cache():
    cache.clear()
    return "Cache cleared"

if __name__ == "__main__":
    app.run(port=5001, debug=True)
