import math
import os
import socket
import time
from flask import Flask, Response, jsonify
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = Flask(__name__)
VERSION = os.environ.get("APP_VERSION", "dev")
REQUESTS = Counter("app_requests_total", "Total HTTP requests", ["endpoint"])
WORK_SECONDS = Histogram("app_work_duration_seconds", "Time spent in /work")


@app.route("/")
def index():
    REQUESTS.labels(endpoint="/").inc()
    return jsonify(
        app="cloudnative-demo",
        version=VERSION,
        message=os.environ.get("APP_MESSAGE", "hello"),
        pod=socket.gethostname(),
        token_configured=bool(os.environ.get("API_TOKEN")),
    )


@app.route("/healthz")
def healthz():
    # Liveness: the process is alive and serving HTTP.
    return Response("ok\n", mimetype="text/plain")


@app.route("/readyz")
def readyz():
    # Readiness: only accept traffic once required configuration exists.
    if not os.environ.get("API_TOKEN"):
        return Response("missing API_TOKEN\n", status=503, mimetype="text/plain")
    return Response("ready\n", mimetype="text/plain")


@app.route("/work")
def work():
    # Burns about 200 ms of CPU so we can trigger autoscaling.
    REQUESTS.labels(endpoint="/work").inc()
    with WORK_SECONDS.time():
        end = time.time() + 0.2
        n = 0
        while time.time() < end:
            n += math.isqrt(123456789)
    return jsonify(pod=socket.gethostname(), iterations=n)


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)
