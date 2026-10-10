from fastapi.testclient import TestClient
from solution import app

c = TestClient(app)

def test_create_and_get():
    r = c.post("/notes", json={"title": "Compras", "body": "leite"})
    assert r.status_code == 201
    d = r.json()
    assert set(d) == {"id", "title", "body"} and d["title"] == "Compras"
    assert c.get(f"/notes/{d['id']}").json() == d

def test_default_body_and_ids_increase():
    a = c.post("/notes", json={"title": "x"}).json()
    b = c.post("/notes", json={"title": "y"}).json()
    assert a["body"] == "" and b["id"] == a["id"] + 1

def test_validation():
    assert c.post("/notes", json={"title": ""}).status_code == 422
    assert c.post("/notes", json={"title": "a" * 51}).status_code == 422
    assert c.post("/notes", json={"title": "a" * 50}).status_code == 201

def test_put_delete_404():
    n = c.post("/notes", json={"title": "orig"}).json()
    r = c.put(f"/notes/{n['id']}", json={"title": "novo", "body": "b"})
    assert r.status_code == 200 and r.json()["title"] == "novo"
    assert c.delete(f"/notes/{n['id']}").status_code == 204
    assert c.get(f"/notes/{n['id']}").status_code == 404
    assert c.put(f"/notes/{n['id']}", json={"title": "z"}).status_code == 404
    assert c.delete(f"/notes/{n['id']}").status_code == 404

def test_list_and_search():
    c.post("/notes", json={"title": "Reunião SEMANAL"})
    ids = [n["id"] for n in c.get("/notes").json()]
    assert ids == sorted(ids)
    found = c.get("/notes?q=semanal").json()
    assert found and all("semanal" in n["title"].lower() for n in found)
