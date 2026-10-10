from solution import RateLimiter

class Clock:
    def __init__(self): self.t = 100.0
    def __call__(self): return self.t

def test_burst_and_refill():
    clk = Clock()
    r = RateLimiter(rate=2, capacity=3, clock=clk)
    assert [r.allow() for _ in range(4)] == [True, True, True, False]
    clk.t += 0.5
    assert r.allow() is True and r.allow() is False
    clk.t += 10
    assert [r.allow() for _ in range(4)] == [True, True, True, False]

def test_cost_does_not_consume_on_fail():
    clk = Clock()
    r = RateLimiter(rate=1, capacity=5, clock=clk)
    assert r.allow(4) is True
    assert r.allow(2) is False
    assert r.allow(1) is True
