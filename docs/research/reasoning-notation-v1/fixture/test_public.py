import importlib
import pytest

@pytest.fixture(params=["proposal_k", "proposal_r"])
def cache(request):
    return importlib.import_module(request.param).Cache()

def test_live_and_expired(cache):
    cache.put("a", "first", now=10, ttl=5)
    assert cache.get("a", now=14) == "first"
    assert cache.get("a", now=16, default="miss") == "miss"

def test_batch_order_and_missing(cache):
    cache.put("a", 7, now=0, ttl=10)
    cache.put("b", 9, now=0, ttl=10)
    assert cache.get_many(["b", "missing", "a"], now=1, default=-1) == [9, -1, 7]

def test_values_replacement_and_empty(cache):
    cache.put("a", None, now=0, ttl=3)
    assert cache.get_many(["a"], now=1, default="miss") == [None]
    cache.put("a", False, now=1, ttl=3)
    assert cache.get("a", now=2, default="miss") is False
    assert cache.get_many([], now=2) == []

def test_validation(cache):
    for bad in (True, None, float("inf"), float("nan")):
        with pytest.raises(ValueError): cache.get_many([], now=bad)
    for bad in ("a", None, ["a", ""]):
        with pytest.raises(ValueError): cache.get_many(bad, now=0)
    with pytest.raises(ValueError): cache.put("a", 1, now=0, ttl=0)
