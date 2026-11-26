import os
import socket
import time
import redis
from flask import Flask, jsonify, request

app = Flask(__name__)

VERSION = os.environ.get("APP_VERSION", "v1")
GREETING = os.environ.get("GREETING", "hello")
LOG_FILE = os.environ.get("LOG_FILE")
CONFIG_FILE = os.environ.get("CONFIG_FILE", "/etc/inventory/app.properties")

r = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PORT", "6379")),
    password=os.environ.get("REDIS_PASSWORD") or None,
    socket_connect_timeout=2,
    socket_timeout=2,
    decode_responses=True,
)


@app.after_request
def access_log(response):
    # Write an access log file for the sidecar to ship (probes are skipped).
    if LOG_FILE and request.path not in ("/healthz", "/ready"):
        line = (
            f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {request.method} "
            f"{request.path} {response.status_code} {socket.gethostname()}\n"
        )
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as fh:
                fh.write(line)
        except OSError:
            pass
    return response


@app.get("/")
def index():
    return jsonify(
        service="inventory-api",
        version=VERSION,
        greeting=GREETING,
        pod=socket.gethostname(),
    )


@app.get("/healthz")
def healthz():
    # Liveness: only says "the process is alive". Never depends on Redis.
    return "ok\n", 200


@app.get("/ready")
def ready():
    # Readiness: can we actually serve traffic? Needs Redis.
    try:
        r.ping()
        return "ready\n", 200
    except redis.RedisError as exc:
        return f"not ready: {exc}\n", 503


@app.get("/config")
def config():
    try:
        with open(CONFIG_FILE, encoding="utf-8") as fh:
            return fh.read(), 200, {"Content-Type": "text/plain"}
    except OSError:
        return "no config file\n", 404


@app.post("/items/<name>")
def add_item(name):
    count = r.incr(f"item:{name}")
    r.sadd("items", name)
    return jsonify(item=name, count=count), 201


@app.get("/items")
def list_items():
    names = sorted(r.smembers("items"))
    return jsonify({n: int(r.get(f"item:{n}") or 0) for n in names})
