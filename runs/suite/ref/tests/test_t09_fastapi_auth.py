from fastapi.testclient import TestClient
from solution import app

c = TestClient(app)

def test_ok():
    r = c.get("/me", headers={"Authorization": "Bearer secret-token"})
    assert r.status_code == 200 and r.json() == {"user": "admin"}

def test_missing_header_is_401():
    r = c.get("/me")
    assert r.status_code == 401
    assert "bearer" in r.headers.get("www-authenticate", "").lower()

def test_wrong_token_and_scheme():
    assert c.get("/me", headers={"Authorization": "Bearer nope"}).status_code == 401
    assert c.get("/me", headers={"Authorization": "Basic secret-token"}).status_code == 401
    assert c.get("/me", headers={"Authorization": "secret-token"}).status_code == 401

def test_health_public():
    assert c.get("/health").json() == {"status": "ok"}
