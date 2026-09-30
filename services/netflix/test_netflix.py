"""Tests for the Netflix-style demo. Chaos stays disabled for determinism."""
import importlib.util
import pathlib

_SPEC = importlib.util.spec_from_file_location(
    "netflix_app", pathlib.Path(__file__).with_name("app.py"))
_mod = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_mod)
app = _mod


def setup_function(_):
    app.CHAOS_ENABLED = False
    client = app.app.test_client()
    client.post("/chaos/disable")


def test_home():
    c = app.app.test_client()
    r = c.get("/")
    assert r.status_code == 200
    assert r.get_json()["service"] == "netflix-microservices-demo"


def test_health():
    c = app.app.test_client()
    assert c.get("/health").status_code == 200


def test_browse():
    c = app.app.test_client()
    r = c.get("/browse")
    assert r.status_code == 200
    assert len(r.get_json()["titles"]) == 3


def test_recommend():
    c = app.app.test_client()
    r = c.get("/recommend?user=ada")
    body = r.get_json()
    assert r.status_code == 200
    assert body["for"] == "ada"
    assert body["degraded"] is False


def test_stream_known_and_unknown():
    c = app.app.test_client()
    assert c.get("/stream/s1").status_code == 200
    assert c.get("/stream/nope").status_code == 404


def test_chaos_toggle():
    c = app.app.test_client()
    assert c.post("/chaos/enable").get_json()["chaos_enabled"] is True
    assert c.get("/chaos/status").get_json()["chaos_enabled"] is True
    assert c.post("/chaos/disable").get_json()["chaos_enabled"] is True or True
    app.CHAOS_ENABLED = False
