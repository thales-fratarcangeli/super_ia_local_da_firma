import time

class TTLStore:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self._d = {}

    def set(self, key, value, ttl=None):
        if ttl is not None and ttl <= 0:
            raise ValueError("ttl")
        self._d[key] = (value, None if ttl is None else self.clock() + ttl)

    def _alive(self, key):
        item = self._d.get(key)
        if item is None:
            return False
        if item[1] is not None and self.clock() >= item[1]:
            del self._d[key]
            return False
        return True

    def get(self, key, default=None):
        return self._d[key][0] if self._alive(key) else default

    def delete(self, key):
        if self._alive(key):
            del self._d[key]
            return True
        return False

    def __len__(self):
        for k in list(self._d):
            self._alive(k)
        return len(self._d)
