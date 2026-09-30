"""Capital One-style DevSecOps demo.

Mirrors Q2: shift-left security — strict input validation, security
headers, audit logging and a compliance endpoint. Fully deterministic
(banking must be); no random failures.
"""
import re
import time
import uuid

from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter

app = Flask(__name__)
metrics = PrometheusMetrics(app)

TRANSFERS = Counter("bank_transfers_total", "Successful transfers")
BLOCKED = Counter("bank_blocked_requests_total", "Blocked invalid requests")

AUDIT_LOG = []
BALANCES = {"ACC10001": 5000.0, "ACC10002": 1200.5}

ACCOUNT_RE = re.compile(r"^[A-Z0-9]{6,12}$")


def _audit(action, detail):
    AUDIT_LOG.append({"ts": time.time(), "action": action, "detail": detail})
    del AUDIT_LOG[:-100:]  # keep last 100


@app.after_request
def _security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Content-Security-Policy"] = "default-src 'self'"
    resp.headers["Strict-Transport-Security"] = "max-age=31536000"
    return resp


def _valid_account(name):
    return bool(name and ACCOUNT_RE.match(name))


@app.route("/")
def home():
    return jsonify({"status": "ok", "service": "capitalone-devsecops-demo"})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/balance")
def balance():
    acct = request.args.get("account", "")
    if not _valid_account(acct):
        BLOCKED.inc()
        return jsonify({"error": "invalid account format"}), 400
    return jsonify({"account": acct, "balance": BALANCES.get(acct, 0.0)})


@app.route("/transfer", methods=["POST"])
def transfer():
    data = request.get_json(silent=True) or {}
    src, dst, amount = data.get("from"), data.get("to"), data.get("amount")
    if not (_valid_account(src) and _valid_account(dst)):
        BLOCKED.inc()
        return jsonify({"error": "invalid account format"}), 400
    if not isinstance(amount, (int, float)) or not 0 < amount <= 10000:
        BLOCKED.inc()
        return jsonify({"error": "amount must be 0 < x <= 10000"}), 400
    if BALANCES.get(src, 0.0) < amount:
        return jsonify({"error": "insufficient funds"}), 422
    BALANCES[src] = BALANCES.get(src, 0.0) - amount
    BALANCES[dst] = BALANCES.get(dst, 0.0) + amount
    txid = str(uuid.uuid4())
    TRANSFERS.inc()
    _audit("transfer", {"tx": txid, "from": src, "to": dst, "amount": amount})
    return jsonify({"tx": txid, "status": "committed"}), 201


@app.route("/audit")
def audit():
    return jsonify({"entries": AUDIT_LOG[-20:]})


@app.route("/compliance")
def compliance():
    """Compliance-as-code: steady proof for auditors."""
    return jsonify({
        "input_validation": True,
        "security_headers": True,
        "audit_logging": True,
        "scan": "bandit in CI (see workflow)",
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # nosec B104 - required for Docker/K8s
