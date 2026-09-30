"""Netflix-style microservices demo.

Mirrors Q1: small independent services (browse / recommend / billing /
stream) with graceful degradation + Chaos-Monkey-style fault injection.
Chaos is OFF by default so tests stay deterministic; enable via
  CHAOS_ENABLED=1  or  POST /chaos/enable
"""
import os
import random
import time

from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter

app = Flask(__name__)
metrics = PrometheusMetrics(app)

STREAM_PLAYS = Counter("netflix_stream_plays_total", "Successful stream plays")
BILLING_FAILURES = Counter("netflix_billing_failures_total", "Billing faults (chaos)")

CATALOG = [
    {"id": "s1", "title": "Space Heist", "genre": "sci-fi"},
    {"id": "s2", "title": "Slow Burns", "genre": "drama"},
    {"id": "s3", "title": "Chaos Diaries", "genre": "documentary"},
]

CHAOS_ENABLED = os.getenv("CHAOS_ENABLED", "0") == "1"


def _maybe_chaos():
    """Inject latency / failure only when chaos is enabled."""
    if not CHAOS_ENABLED:
        return None
    time.sleep(random.uniform(0.05, 0.3))  # nosec B311 - chaos fault, not crypto
    if random.random() < 0.15:  # nosec B311 - chaos fault, not crypto
        return jsonify({"error": "chaos fault injected"}), 500
    return None


@app.route("/")
def home():
    return jsonify({"status": "ok", "service": "netflix-microservices-demo"})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/browse")
def browse():
    fault = _maybe_chaos()
    if fault:
        return fault
    return jsonify({"titles": CATALOG})


@app.route("/recommend")
def recommend():
    fault = _maybe_chaos()
    if fault:
        # graceful degradation: fall back to default row instead of 500
        return jsonify({"for": request.args.get("user", "anon"),
                        "picks": [CATALOG[0]], "degraded": True})
    user = request.args.get("user", "anon")
    return jsonify({"for": user, "picks": CATALOG[:2], "degraded": False})


@app.route("/billing")
def billing():
    fault = _maybe_chaos()
    if fault:
        BILLING_FAILURES.inc()
        return fault
    return jsonify({"account": "current", "due": 0})


@app.route("/stream/<title_id>")
def stream(title_id):
    """Video play must survive even if billing is faulty (isolation)."""
    fault = _maybe_chaos()
    if fault:
        # degrade: still return stream URL, flag billing unknown
        STREAM_PLAYS.inc()
        return jsonify({"title": title_id, "playing": True,
                        "billing": "unknown (degraded)"})
    match = next((t for t in CATALOG if t["id"] == title_id), None)
    if not match:
        return jsonify({"error": "unknown title"}), 404
    STREAM_PLAYS.inc()
    return jsonify({"title": match["title"], "playing": True})


@app.route("/chaos/status")
def chaos_status():
    return jsonify({"chaos_enabled": CHAOS_ENABLED})


@app.route("/chaos/enable", methods=["POST"])
def chaos_enable():
    global CHAOS_ENABLED
    CHAOS_ENABLED = True
    return jsonify({"chaos_enabled": True})


@app.route("/chaos/disable", methods=["POST"])
def chaos_disable():
    global CHAOS_ENABLED
    CHAOS_ENABLED = False
    return jsonify({"chaos_enabled": False})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # nosec B104 - required for Docker/K8s
