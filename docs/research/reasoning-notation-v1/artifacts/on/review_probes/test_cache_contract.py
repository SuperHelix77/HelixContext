"""Focused review probes; run explicitly, without changing supplied files."""
import importlib
import inspect
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from before import Cache as Before


@pytest.fixture(params=["proposal_k", "proposal_r"])
def cls(request):
    return importlib.import_module(request.param).Cache


@pytest.mark.parametrize("batch", [False, True], ids=["get", "get_many"])
def test_expiry_boundary(cls, batch):
    cache = cls()
    cache.put("a", "value", now=10, ttl=5)
    read = (lambda now: cache.get_many(["a"], now=now, default="miss")) if batch else (
        lambda now: cache.get("a", now=now, default="miss")
    )
    assert read(math.nextafter(15.0, -math.inf)) == (["value"] if batch else "value")
    assert read(15) == (["miss"] if batch else "miss")
    assert read(math.nextafter(15.0, math.inf)) == (["miss"] if batch else "miss")


def test_repeated_hits_and_misses(cls):
    cache = cls()
    cache.put("a", 7, now=0, ttl=10)
    keys = ["a", "missing", "a", "missing"]
    assert cache.get_many(keys, now=1, default=-1) == [7, -1, 7, -1]
    assert keys == ["a", "missing", "a", "missing"]


def test_exact_value_and_default_identity(cls):
    cache = cls()
    values = [None, False, 0, 0.0, "", [], {}, set(), (), object()]
    keys = [str(i) for i in range(len(values))]
    for name, value in zip(keys, values):
        cache.put(name, value, now=-5.5, ttl=10.25)
    default = []
    actual = cache.get_many(keys + ["missing"], now=-1.5, default=default)
    assert len(actual) == len(values) + 1
    for name, value, result in zip(keys, values, actual):
        assert result is value
        assert cache.get(name, now=-1.5, default=default) is value
    assert actual[-1] is default
    assert cache.get("missing", now=0, default=default) is default
    assert cache.get_many(["missing"], now=0) == [None]


def test_replacement_resets_value_and_expiry(cls):
    cache = cls()
    cache.put("a", "old", now=0, ttl=2)
    new = []
    cache.put("a", new, now=1, ttl=10)
    assert cache.get("a", now=3) is new
    assert cache.get_many(["a"], now=3)[0] is new
    assert cache.get("a", now=12, default="miss") == "miss"


def test_reads_preserve_records(cls):
    cache = cls()
    live, expired = [], {}
    cache.put("live", live, now=0, ttl=10)
    cache.put("expired", expired, now=0, ttl=1)
    records = cache.entries
    snapshot = dict(records)
    assert cache.get("expired", now=2, default="miss") == "miss"
    assert cache.get_many(["expired", "live", "missing"], now=2, default="miss") == ["miss", live, "miss"]
    with pytest.raises(ValueError):
        cache.get_many(["expired", ""], now=2)
    assert cache.entries is records
    assert records.keys() == snapshot.keys()
    assert all(records[name] is entry for name, entry in snapshot.items())
    assert live == [] and expired == {}


def test_full_validation_before_lookup(cls):
    class LookupGuard(dict):
        def get(self, *args, **kwargs):
            raise AssertionError("lookup occurred before request validation completed")

    cache = cls()
    cache.entries = LookupGuard()
    for bad in ["", None, True, 1, [], {}]:
        with pytest.raises(ValueError, match="^nonempty string key required$"):
            cache.get_many(["valid", bad], now=0)
    for bad in [True, False, None, "0", float("inf"), float("-inf"), float("nan")]:
        with pytest.raises(ValueError, match="^finite number required$"):
            cache.get_many(["valid"], now=bad)


def test_empty_request_and_container_validation(cls):
    cache = cls()
    for now in [0, -1, 0.5]:
        assert cache.get_many([], now=now) == []
    for bad in [True, False, None, "0", float("inf"), float("-inf"), float("nan")]:
        with pytest.raises(ValueError, match="^finite number required$"):
            cache.get_many([], now=bad)
    for bad in [None, "a", (), ("a",), {}, {"a"}, iter(["a"]), 1, True]:
        with pytest.raises(ValueError, match="^list of keys required$"):
            cache.get_many(bad, now=0)


def test_existing_signatures(cls):
    for name in ["__init__", "put", "get"]:
        assert inspect.signature(getattr(cls, name)) == inspect.signature(getattr(Before, name))
    assert str(inspect.signature(cls.get_many)) == "(self, keys, *, now, default=None)"


def test_existing_validation_and_error_compatibility(cls):
    invalid_numbers = [True, False, None, "0", float("inf"), float("-inf"), float("nan")]
    invalid_keys = ["", None, True, 1, [], {}]
    calls = []
    for bad in invalid_keys:
        calls.extend([("get", (bad,), {"now": 0}), ("put", (bad, 1), {"now": 0, "ttl": 1})])
    for bad in invalid_numbers:
        calls.extend([
            ("get", ("a",), {"now": bad}),
            ("put", ("a", 1), {"now": bad, "ttl": 1}),
            ("put", ("a", 1), {"now": 0, "ttl": bad}),
        ])
    calls.extend([
        ("put", ("a", 1), {"now": 0, "ttl": ttl}) for ttl in [0, -1, -0.5]
    ])
    calls.extend([
        ("put", ("a", 1), {"now": 1e308, "ttl": 1e308}),
        ("get", ("",), {"now": True}),
        ("put", ("", 1), {"now": True, "ttl": False}),
        ("get", ("a",), {}),
        ("get", ("a", 0), {}),
        ("get", (), {"key": "a", "now": 0}),
        ("put", ("a", 1), {"now": 0}),
        ("put", ("a", 1, 0, 1), {}),
    ])
    for populated in [False, True]:
        for name, args, kwargs in calls:
            errors = []
            for factory in [Before, cls]:
                cache = factory()
                if populated:
                    cache.put("a", [], now=0, ttl=10)
                snapshot = dict(cache.entries)
                with pytest.raises((ValueError, TypeError)) as caught:
                    getattr(cache, name)(*args, **kwargs)
                errors.append((type(caught.value), str(caught.value)))
                assert cache.entries.keys() == snapshot.keys()
                assert all(cache.entries[k] is v for k, v in snapshot.items())
            assert errors[0] == errors[1], (name, args, kwargs, errors)


def test_extension_keyword_only_arguments(cls):
    cache = cls()
    with pytest.raises(TypeError):
        cache.get_many([])
    with pytest.raises(TypeError):
        cache.get_many([], 0)
