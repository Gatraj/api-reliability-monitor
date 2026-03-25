from flask import Flask, render_template, jsonify
import requests
import time
import datetime
import os
import json


app = Flask(__name__)

# Default services — used when MONITORED_SERVICES env var is not set
DEFAULT_SERVICES = [
    {"name": "GitHub API", "url": "https://api.github.com"},
    {"name": "JSONPlaceholder", "url": "https://jsonplaceholder.typicode.com/posts/1"},
    {"name": "HTTPBin Healthy", "url": "https://httpbin.org/status/200"},
    {"name": "HTTPBin Down", "url": "https://httpbin.org/status/503"},
]

def load_services():
    raw = os.environ.get("MONITORED_SERVICES")
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            print("WARNING: MONITORED_SERVICES is not valid JSON. Using defaults.")
    return DEFAULT_SERVICES

SERVICES = load_services()

def check_service(service):
    try:
        start = time.time()
        response = requests.get(service["url"], timeout=5)
        response_time = round((time.time() - start) * 1000)
        return {
            "name": service["name"],
            "url": service["url"],
            "status": "UP" if response.status_code == 200 else "DOWN",
            "status_code": response.status_code,
            "response_time_ms": response_time,
            "checked_at": datetime.datetime.now().strftime("%H:%M:%S")
        }
    except Exception as e:
        return {
            "name": service["name"],
            "url": service["url"],
            "status": "DOWN",
            "status_code": None,
            "response_time_ms": None,
            "checked_at": datetime.datetime.now().strftime("%H:%M:%S")
        }

@app.route("/")
def dashboard():
    results = [check_service(s) for s in SERVICES]
    return render_template("index.html", services=results)

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": str(datetime.datetime.now())})

@app.route("/metrics")
def metrics():
    results = [check_service(s) for s in SERVICES]
    output = ""
    for r in results:
        name = r["name"].lower().replace(" ", "_")
        status = 1 if r["status"] == "UP" else 0
        output += f'service_up{{name="{r["name"]}"}} {status}\n'
        if r["response_time_ms"]:
            output += f'service_response_ms{{name="{r["name"]}"}} {r["response_time_ms"]}\n'
    return output, 200, {"Content-Type": "text/plain; charset=utf-8"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)


