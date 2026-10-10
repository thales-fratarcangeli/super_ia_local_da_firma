import pytest
from solution import TTLStore

class Clock:
    def __init__(self): self.t = 10.0
    def __call__(self): return self.t

def test_basic_and_default():
    c = Clock(); s = TTLStore(clock=c)
    s.set("a", 1)
    assert s.get("a") == 1 and s.get("zz") is None and s.get("zz", 7) == 7

def test_expiry_boundary():
    c = Clock(); s = TTLStore(clock=c)
    s.set("a", 1, ttl=5)
    c.t += 4.5
    assert s.get("a") == 1
    c.t += 0.5
    assert s.get("a") is None

def test_len_counts_only_alive_and_delete():
    c = Clock(); s = TTLStore(clock=c)
    s.set("a", 1, ttl=1); s.set("b", 2); s.set("c", 3, ttl=100)
    c.t += 2
    assert len(s) == 2
    assert s.delete("a") is False and s.delete("b") is True and len(s) == 1

def test_overwrite_resets_ttl_and_invalid():
    c = Clock(); s = TTLStore(clock=c)
    s.set("a", 1, ttl=2); c.t += 1.5; s.set("a", 2, ttl=2); c.t += 1.5
    assert s.get("a") == 2
    with pytest.raises(ValueError):
        s.set("x", 1, ttl=0)
