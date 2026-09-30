"""Tests for the Capital One-style demo."""
import importlib.util
import pathlib

_SPEC = importlib.util.spec_from_file_location(
    "capitalone_app", pathlib.Path(__file__).with_name("app.py"))
_mod = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_mod)
app = _mod


def test_home_and_health():
    c = app.app.test_client()
    assert c.get("/").get_json()["service"] == "capitalone-devsecops-demo"
    assert c.get("/health").status_code == 200


def test_security_headers():
    c = app.app.test_client()
    r = c.get("/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"


def test_balance_validation():
    c = app.app.test_client()
    assert c.get("/balance?account=ACC10001").status_code == 200
    assert c.get("/balance?account=bad!!").status_code == 400
    assert c.get("/balance").status_code == 400


def test_transferhappy_and_guards():
    c = app.app.test_client()
    app.BALANCES["ACC10001"] = 5000.0
    app.BALANCES["ACC10002"] = 0.0
    r = c.post("/transfer", json={"from": "ACC10001", "to": "ACC10002", "amount": 100})
    assert r.status_code == 201
    assert "tx" in r.get_json()
    assert c.post("/transfer", json={"from": "!!", "to": "ACC10002", "amount": 10}).status_code == 400
    assert c.post("/transfer", json={"from": "ACC10001", "to": "ACC10002", "amount": -5}).status_code == 400
    assert c.post("/transfer", json={"from": "ACC10002", "to": "ACC10001", "amount": 99999}).status_code in (400, 422)


def test_audit_and_compliance():
    c = app.app.test_client()
    assert "entries" in c.get("/audit").get_json()
    body = c.get("/compliance").get_json()
    assert body["input_validation"] is True
    assert body["audit_logging"] is True
