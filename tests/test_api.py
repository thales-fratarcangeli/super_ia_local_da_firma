import itertools
import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(_tmp, "test.db").replace("\\", "/")
os.environ["JWT_SECRET"] = "test-secret"

import jwt  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)
_n = itertools.count(1)


def new_user(role=None, password="secret123"):
    name = f"user{next(_n)}"
    body = {"username": name, "password": password}
    if role:
        body["role"] = role
    r = client.post("/auth/register", json=body)
    assert r.status_code == 201, r.text
    t = client.post("/auth/login", json={"username": name, "password": password})
    assert t.status_code == 200, t.text
    return {"id": r.json()["id"], "name": name, "h": {"Authorization": "Bearer " + t.json()["access_token"]}}


def new_project(u, name="proj"):
    r = client.post("/projects", json={"name": name}, headers=u["h"])
    assert r.status_code == 201, r.text
    return r.json()


# ---------- auth ----------
def test_register_ok_and_no_password_leak():
    r = client.post("/auth/register", json={"username": "alice", "password": "secret123"})
    assert r.status_code == 201
    d = r.json()
    assert d["username"] == "alice" and d["role"] == "member" and "id" in d
    assert "password" not in d and "password_hash" not in d and "hashed_password" not in d


def test_register_duplicate_409():
    client.post("/auth/register", json={"username": "dup", "password": "secret123"})
    r = client.post("/auth/register", json={"username": "dup", "password": "secret123"})
    assert r.status_code == 409


def test_register_validation_422():
    assert client.post("/auth/register", json={"username": "x1", "password": "123"}).status_code == 422
    assert client.post("/auth/register", json={"username": "x2", "password": "secret123", "role": "root"}).status_code == 422


def test_login_ok_and_token_is_jwt():
    u = new_user()
    tok = u["h"]["Authorization"].split()[1]
    payload = jwt.decode(tok, "test-secret", algorithms=["HS256"])
    assert "exp" in payload


def test_login_wrong_password_401():
    client.post("/auth/register", json={"username": "bob", "password": "secret123"})
    assert client.post("/auth/login", json={"username": "bob", "password": "nope-nope"}).status_code == 401
    assert client.post("/auth/login", json={"username": "ghost", "password": "secret123"}).status_code == 401


def test_protected_requires_token():
    assert client.get("/projects").status_code == 401
    assert client.get("/projects", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_expired_token_401():
    import datetime
    u = new_user()
    bad = jwt.encode(
        {"sub": str(u["id"]), "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=5)},
        "test-secret", algorithm="HS256")
    assert client.get("/projects", headers={"Authorization": "Bearer " + bad}).status_code == 401


# ---------- projects ----------
def test_create_project_and_validation():
    u = new_user()
    p = new_project(u, "meu")
    assert p["name"] == "meu" and p["owner_id"] == u["id"]
    assert client.post("/projects", json={"name": ""}, headers=u["h"]).status_code == 422


def test_member_sees_only_own_projects_admin_sees_all():
    a, b, adm = new_user(), new_user(), new_user("admin")
    pa = new_project(a, "A")
    pb = new_project(b, "B")
    ids_a = [p["id"] for p in client.get("/projects", headers=a["h"]).json()["items"]]
    assert pa["id"] in ids_a and pb["id"] not in ids_a
    ids_adm = [p["id"] for p in client.get("/projects?page_size=50", headers=adm["h"]).json()["items"]]
    assert pa["id"] in ids_adm and pb["id"] in ids_adm


def test_project_pagination():
    u = new_user()
    for i in range(5):
        new_project(u, f"p{i}")
    r = client.get("/projects?page=2&page_size=2", headers=u["h"]).json()
    assert r["total"] == 5 and r["page"] == 2 and r["page_size"] == 2 and len(r["items"]) == 2
    ids = [p["id"] for p in client.get("/projects?page_size=50", headers=u["h"]).json()["items"]]
    assert ids == sorted(ids)
    assert [p["id"] for p in r["items"]] == ids[2:4]


@pytest.mark.parametrize("q", ["page=0", "page_size=0", "page_size=51", "page=abc"])
def test_pagination_invalid_422(q):
    u = new_user()
    assert client.get("/projects?" + q, headers=u["h"]).status_code == 422


def test_project_permissions():
    a, b, adm = new_user(), new_user(), new_user("admin")
    p = new_project(a)
    assert client.get(f"/projects/{p['id']}", headers=a["h"]).status_code == 200
    assert client.get(f"/projects/{p['id']}", headers=b["h"]).status_code == 403
    assert client.get(f"/projects/{p['id']}", headers=adm["h"]).status_code == 200
    assert client.get("/projects/999999", headers=a["h"]).status_code == 404
    assert client.delete(f"/projects/{p['id']}", headers=b["h"]).status_code == 403
    assert client.delete("/projects/999999", headers=a["h"]).status_code == 404


def test_delete_project_cascades_tasks():
    u = new_user()
    p = new_project(u)
    t = client.post(f"/projects/{p['id']}/tasks", json={"title": "t"}, headers=u["h"]).json()
    assert client.delete(f"/projects/{p['id']}", headers=u["h"]).status_code == 204
    assert client.get(f"/projects/{p['id']}", headers=u["h"]).status_code == 404
    assert client.patch(f"/tasks/{t['id']}", json={"title": "x"}, headers=u["h"]).status_code == 404


# ---------- tasks ----------
def test_create_task_defaults_and_validation():
    u = new_user()
    p = new_project(u)
    r = client.post(f"/projects/{p['id']}/tasks", json={"title": "fazer"}, headers=u["h"])
    assert r.status_code == 201
    d = r.json()
    assert d["status"] == "todo" and d["description"] is None and d["project_id"] == p["id"]
    assert client.post(f"/projects/{p['id']}/tasks", json={"title": ""}, headers=u["h"]).status_code == 422
    assert client.post(f"/projects/{p['id']}/tasks", json={"title": "x", "status": "weird"}, headers=u["h"]).status_code == 422


def test_task_project_permissions():
    a, b = new_user(), new_user()
    p = new_project(a)
    assert client.post(f"/projects/{p['id']}/tasks", json={"title": "x"}, headers=b["h"]).status_code == 403
    assert client.post("/projects/999999/tasks", json={"title": "x"}, headers=a["h"]).status_code == 404
    assert client.get(f"/projects/{p['id']}/tasks", headers=b["h"]).status_code == 403


def test_list_tasks_filter_and_pagination():
    u = new_user()
    p = new_project(u)
    for i, s in enumerate(["todo", "doing", "done", "todo", "todo"]):
        assert client.post(f"/projects/{p['id']}/tasks", json={"title": f"t{i}", "status": s}, headers=u["h"]).status_code == 201
    r = client.get(f"/projects/{p['id']}/tasks?status=todo", headers=u["h"]).json()
    assert r["total"] == 3 and all(t["status"] == "todo" for t in r["items"])
    r = client.get(f"/projects/{p['id']}/tasks?page=2&page_size=2", headers=u["h"]).json()
    assert r["total"] == 5 and len(r["items"]) == 2
    assert client.get(f"/projects/{p['id']}/tasks?status=bad", headers=u["h"]).status_code == 422


def test_patch_task_partial():
    u = new_user()
    p = new_project(u)
    t = client.post(f"/projects/{p['id']}/tasks", json={"title": "a", "description": "d"}, headers=u["h"]).json()
    r = client.patch(f"/tasks/{t['id']}", json={"status": "done"}, headers=u["h"])
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "done" and d["title"] == "a" and d["description"] == "d"
    assert client.patch(f"/tasks/{t['id']}", json={"status": "zzz"}, headers=u["h"]).status_code == 422
    assert client.patch("/tasks/999999", json={"title": "x"}, headers=u["h"]).status_code == 404


def test_task_permissions_patch_delete():
    a, b, adm = new_user(), new_user(), new_user("admin")
    p = new_project(a)
    t = client.post(f"/projects/{p['id']}/tasks", json={"title": "a"}, headers=a["h"]).json()
    assert client.patch(f"/tasks/{t['id']}", json={"title": "h"}, headers=b["h"]).status_code == 403
    assert client.delete(f"/tasks/{t['id']}", headers=b["h"]).status_code == 403
    assert client.patch(f"/tasks/{t['id']}", json={"title": "ok"}, headers=adm["h"]).status_code == 200
    assert client.delete(f"/tasks/{t['id']}", headers=a["h"]).status_code == 204
    assert client.delete(f"/tasks/{t['id']}", headers=a["h"]).status_code == 404
