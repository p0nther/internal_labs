from flask import Flask, request
import time
from datetime import datetime
app = Flask(__name__)

cache = {}

@app.route("/")
def home():
    path = request.path

    if path in cache:
        return cache[path]

    host = request.headers.get(
        "X-Forwarded-Host",
        "trusted-cdn.free.beeceptor.com"
    )

    response = f"""
    <html>
        <head>
            <script src="https://{host}/app.js"></script>
        </head>
        <body>
            <h1>Welcome</h1>
            <p>Generated at {datetime.fromtimestamp(time.time())}</p>
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
    app.run(debug=True)
