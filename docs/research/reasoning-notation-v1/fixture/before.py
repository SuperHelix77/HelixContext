"""Small in-process cache; the caller supplies its clock."""
import math


def number(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("finite number required")


def key(value):
    if not isinstance(value, str) or not value:
        raise ValueError("nonempty string key required")


class Cache:
    def __init__(self):
        self.entries = {}

    def put(self, name, value, *, now, ttl):
        key(name)
        number(now)
        number(ttl)
        if ttl <= 0:
            raise ValueError("positive ttl required")
        expiry = now + ttl
        number(expiry)
        self.entries[name] = (expiry, value)

    def get(self, name, *, now, default=None):
        key(name)
        number(now)
        entry = self.entries.get(name)
        if entry is None or now >= entry[0]:
            return default
        return entry[1]
