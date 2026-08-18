from flask import Flask, request
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>SSRF Lab</h1>
    <h2> To Access /secret must be admin or requested from  localhost</h2>
    <form action="/fetch">
        <input name="url" placeholder="http://example.com">
        <button>Fetch</button>
    </form>
    """

@app.route("/fetch")
def fetch():
    url = request.args.get("url")

    if not url:
        return "Missing url parameter", 400

    try:
        response = requests.get(url, timeout=5)
        return f"""
        <h2>Fetched: {url}</h2>
        <pre>{response.text[:5000]}</pre>
        """
    except Exception as e:
        return str(e), 500

@app.route("/secret")
def secret():
    return "FLAG{local_ssrf_demo}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
