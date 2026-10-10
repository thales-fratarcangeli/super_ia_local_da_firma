import pytest
from fastapi.testclient import TestClient
from solution import app

c = TestClient(app)

def test_default():
    r = c.get("/items").json()
    assert r == {"items": list(range(1, 11)), "total": 35, "page": 1, "page_size": 10}

def test_page_and_size():
    r = c.get("/items?page=2&page_size=20").json()
    assert r["items"] == list(range(21, 36)) and r["total"] == 35

def test_filter():
    r = c.get("/items?min=30").json()
    assert r["items"] == [30, 31, 32, 33, 34, 35] and r["total"] == 6

@pytest.mark.parametrize("q", ["page=0", "page_size=0", "page_size=51", "page=x", "min=abc"])
def test_422(q):
    assert c.get("/items?" + q).status_code == 422
