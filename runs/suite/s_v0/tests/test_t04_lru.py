import pytest
from solution import LRUCache

def test_eviction_order():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2)
    assert c.get("a") == 1
    c.put("c", 3)
    assert c.get("b") is None and c.get("a") == 1 and c.get("c") == 3

def test_update_refreshes():
    c = LRUCache(2)
    c.put("a", 1); c.put("b", 2); c.put("a", 10); c.put("c", 3)
    assert c.get("a") == 10 and c.get("b") is None

def test_len_and_invalid():
    c = LRUCache(3)
    for i in range(5):
        c.put(i, i)
    assert len(c) == 3
    with pytest.raises(ValueError):
        LRUCache(0)
