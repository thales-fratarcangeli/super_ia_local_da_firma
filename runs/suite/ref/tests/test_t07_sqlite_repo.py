import pytest
from solution import TodoRepo

def test_add_get():
    r = TodoRepo()
    i = r.add("a")
    assert r.get(i) == {"id": i, "title": "a", "done": False}
    assert r.get(999) is None

def test_validation():
    r = TodoRepo()
    for bad in ["", "   "]:
        with pytest.raises(ValueError):
            r.add(bad)

def test_list_filter_and_done():
    r = TodoRepo()
    a, b, c = r.add("a"), r.add("b"), r.add("c")
    assert r.set_done(b, True) is True and r.set_done(999, True) is False
    assert [t["id"] for t in r.list()] == [a, b, c]
    assert [t["id"] for t in r.list(done=True)] == [b]
    assert [t["id"] for t in r.list(done=False)] == [a, c]
    assert r.get(b)["done"] is True

def test_delete_and_injection_safe():
    r = TodoRepo()
    i = r.add("x'); DROP TABLE todos;--")
    assert r.get(i)["title"] == "x'); DROP TABLE todos;--"
    assert r.delete(i) is True and r.delete(i) is False
    assert r.list() == []
