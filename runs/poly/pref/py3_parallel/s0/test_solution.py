
import threading
import pytest
from solution import parallel_map

def test_order_and_values():
    assert parallel_map(lambda x: x * 2, [1, 2, 3, 4, 5], workers=3) == [2, 4, 6, 8, 10]
    assert parallel_map(str, []) == []

def test_really_concurrent():
    barrier = threading.Barrier(4)
    def fn(x):
        barrier.wait(timeout=5)   # só passa se 4 threads estiverem rodando ao mesmo tempo
        return x + 1
    assert parallel_map(fn, [1, 2, 3, 4], workers=4) == [2, 3, 4, 5]

def test_respects_worker_limit():
    active, peak, lock = [0], [0], threading.Lock()
    def fn(x):
        with lock:
            active[0] += 1
            peak[0] = max(peak[0], active[0])
        import time; time.sleep(0.05)
        with lock:
            active[0] -= 1
        return x
    parallel_map(fn, list(range(12)), workers=3)
    assert peak[0] <= 3

def test_exception_and_invalid():
    def fn(x):
        if x == 3:
            raise KeyError("três")
        return x
    with pytest.raises(KeyError):
        parallel_map(fn, [1, 2, 3, 4], workers=2)
    with pytest.raises(ValueError):
        parallel_map(fn, [1], workers=0)
