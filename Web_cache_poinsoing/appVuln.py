from flask import Flask, request, make_response
import time
from datetime import datetime

app = Flask(__name__)

cache = {}

CACHE_TTL = 30

@app.route("/")
def home():
    path = request.path
    now = time.time()

    # Cache HIT
    if path in cache:
        entry = cache[path]

        age = int(now - entry["cached_at"])

        if age <= CACHE_TTL:
            resp = make_response(entry["body"])

            resp.headers["Cache-Control"] = f"max-age={CACHE_TTL}"
            resp.headers["Age"] = str(age)
            resp.headers["X-Cache"] = "hit"

            return resp

        del cache[path]

    # Cache MISS
    host = request.headers.get(
        "X-Forwarded-Host",
        "trusted-cdn.free.beeceptor.com"
    )

    response_body = f"""
    <html>
        <head>
            <script src="https://{host}/app.js"></script>
        </head>
        <body>
            <h1>Welcome, Vuln app</h1>
            <p>Generated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </body>
    </html>
    """

    cache[path] = {
        "body": response_body,
        "cached_at": now
    }

    resp = make_response(response_body)

    resp.headers["Cache-Control"] = f"max-age={CACHE_TTL}"
    resp.headers["Age"] = "0"
    resp.headers["X-Cache"] = "miss"

    return resp


@app.route("/clear-cache")
def clear_cache():
    cache.clear()
    return "Cache cleared"


if __name__ == "__main__":
    app.run(debug=True,port=5000)
