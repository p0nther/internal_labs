from flask import Flask, request
import time
from datetime import datetime

app = Flask(__name__)

cache = {}

TRUSTED_HOST = "trusted-cdn.free.beeceptor.com"

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

            <h1>Fixed app</h1>
            <h1>Welcome</h1>
            <p>Generated at {datetime.fromtimestamp(time.time())}</p>
            <h4>use hardcode host and don't trust user input </h4>
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
