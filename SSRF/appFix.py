from flask import Flask, request
import requests
import socket
import ipaddress
from urllib.parse import urlparse

app = Flask(__name__)

def is_private_host(hostname):
    try:
        ip = socket.gethostbyname(hostname)

        ip_obj = ipaddress.ip_address(ip)

        return (
            ip_obj.is_private		# its return boolean if is_private =True
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_reserved
        )
    except Exception:
        return True

@app.route("/")
def home():
    return """
    <h1>Fixed SSRF Lab</h1>
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

    parsed = urlparse(url)

    if parsed.scheme not in ["http", "https"]:
        return "Only HTTP/HTTPS allowed", 403

    if is_private_host(parsed.hostname):
        return "Access denied", 403

    try:
        response = requests.get(url, timeout=5, allow_redirects=False)
        return response.text[:5000]
    except Exception as e:
        return str(e), 500

@app.route("/secret")
def secret():
    return "FLAG{local_ssrf_demo}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
