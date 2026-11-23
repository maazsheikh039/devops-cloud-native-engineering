import os
import socket
import redis
from flask import Flask, jsonify
from redis.backoff import ExponentialBackoff
from redis.retry import Retry

APP_VERSION = os.environ.get("APP_VERSION", "dev")
app = Flask(__name__)

# Retry with backoff so the app survives Redis restarts and stale pooled connections.
cache = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PORT", "6379")),
    socket_connect_timeout=2,
    socket_timeout=2,
    retry=Retry(ExponentialBackoff(cap=1.0, base=0.1), 3),
    retry_on_error=[redis.exceptions.ConnectionError, redis.exceptions.TimeoutError],
)


@app.get("/")
def index():
    hits = cache.incr("hits")
    return jsonify(
        service="hitcounter",
        version=APP_VERSION,
        host=socket.gethostname(),
        hits=hits,
    )


@app.get("/healthz")
def healthz():
    # Liveness: the process is up and serving HTTP. Does NOT depend on Redis.
    return jsonify(status="alive")


@app.get("/ready")
def ready():
    # Readiness: can we actually do useful work?
    try:
        cache.ping()
        return jsonify(status="ready")
    except redis.RedisError as exc:
        return jsonify(status="degraded", error=str(exc)), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
# cache test 1795442380
