import ast
import importlib
import inspect

mods = {name: importlib.import_module(name) for name in ('before', 'proposal_k', 'proposal_r')}

def expect_error(action, message):
    try:
        action()
    except ValueError as exc:
        assert str(exc) == message, (str(exc), message)
    else:
        raise AssertionError('ValueError not raised')

def ordinary_expiry(Cache):
    c = Cache()
    c.put('a', 'value', now=10, ttl=5)
    observed = [c.get('a', now=t, default='miss') for t in (14, 15, 16)]
    assert observed == ['value', 'miss', 'miss'], observed

def batch_expiry(Cache):
    c = Cache()
    c.put('a', 'value', now=10, ttl=5)
    observed = [c.get_many(['a'], now=t, default='miss') for t in (14, 15, 16)]
    assert observed == [['value'], ['miss'], ['miss']], observed

def repeated_positions(Cache):
    c = Cache()
    c.put('a', 7, now=0, ttl=10)
    observed = c.get_many(['a', 'missing', 'a', 'missing'], now=1, default=-1)
    assert observed == [7, -1, 7, -1], observed

def exact_values_and_defaults(Cache):
    c = Cache()
    values = [None, False, 0, 0.0, '', [], {}, set(), (), object()]
    names = [str(i) for i in range(len(values))]
    sentinel = object()
    for name, value in zip(names, values):
        c.put(name, value, now=-2.5, ttl=4.25)
        assert c.get(name, now=0, default=sentinel) is value
    observed = c.get_many(names + ['missing'], now=0, default=sentinel)
    assert all(got is want for got, want in zip(observed, values + [sentinel]))
    assert len(observed) == len(values) + 1
    assert c.get_many(['missing'], now=0) == [None]
    assert c.get_many([], now=0) == []

def validation_empty_and_populated(Cache):
    bad_numbers = [True, False, None, '1', 1j, float('inf'), -float('inf'), float('nan')]
    bad_keys = ['', None, False, 0, [], {}]
    for populated in (False, True):
        c = Cache()
        if populated:
            c.put('a', 1, now=0, ttl=10)
        for value in bad_numbers:
            expect_error(lambda: c.get('a', now=value), 'finite number required')
            expect_error(lambda: c.put('a', 2, now=value, ttl=1), 'finite number required')
            expect_error(lambda: c.put('a', 2, now=0, ttl=value), 'finite number required')
            for keys in ([], ['a']):
                expect_error(lambda: c.get_many(keys, now=value), 'finite number required')
        for value in (0, -1, -0.5):
            expect_error(lambda: c.put('a', 2, now=0, ttl=value), 'positive ttl required')
        for value in bad_keys:
            expect_error(lambda: c.get(value, now=0), 'nonempty string key required')
            expect_error(lambda: c.put(value, 2, now=0, ttl=1), 'nonempty string key required')
            expect_error(lambda: c.get_many(['a', value], now=0), 'nonempty string key required')
        for keys in ('a', None, (), {}, {'a'}, iter(['a'])):
            expect_error(lambda: c.get_many(keys, now=0), 'list of keys required')

def full_validation_before_lookup(Cache):
    class Reads(dict):
        def __init__(self, entries):
            super().__init__(entries)
            self.lookups = []
        def get(self, name, *args):
            self.lookups.append(name)
            return super().get(name, *args)
    c = Cache()
    c.put('a', 7, now=0, ttl=10)
    c.entries = Reads(c.entries)
    snapshot = dict(c.entries)
    expect_error(lambda: c.get_many(['a', ''], now=1), 'nonempty string key required')
    expect_error(lambda: c.get_many(['a'], now=True), 'finite number required')
    assert c.entries.lookups == [], c.entries.lookups
    assert c.entries == snapshot

def read_nonmutation(Cache):
    c = Cache()
    value = []
    c.put('a', value, now=0, ttl=2)
    records = c.entries
    entry = records['a']
    c.get('a', now=3)
    c.get_many(['a', 'missing', 'a'], now=3)
    assert c.entries is records and len(records) == 1 and records['a'] is entry
    assert c.get('a', now=1) is value
    assert value == []

def replacement_and_failed_writes(Cache):
    c = Cache()
    c.put('a', 'old', now=0, ttl=10)
    replacement = []
    c.put('a', replacement, now=1, ttl=20)
    assert c.get('a', now=11) is replacement
    record = c.entries['a']
    for action, message in (
        (lambda: c.put('a', 'bad', now=1, ttl=0), 'positive ttl required'),
        (lambda: c.put('a', 'bad', now=True, ttl=1), 'finite number required'),
        (lambda: c.put('a', 'bad', now=1e308, ttl=1e308), 'finite number required'),
    ):
        expect_error(action, message)
        assert c.entries['a'] is record

def signatures(Cache):
    for name in ('__init__', 'put', 'get'):
        assert inspect.signature(getattr(Cache, name)) == inspect.signature(getattr(mods['before'].Cache, name))
    assert str(inspect.signature(Cache.get_many)) == '(self, keys, *, now, default=None)'

checks = [ordinary_expiry, batch_expiry, repeated_positions, exact_values_and_defaults,
          validation_empty_and_populated, full_validation_before_lookup, read_nonmutation,
          replacement_and_failed_writes, signatures]
for name in ('proposal_k', 'proposal_r'):
    passed = 0
    for check in checks:
        try:
            check(mods[name].Cache)
            passed += 1
        except AssertionError as exc:
            print(f'{name}: FAIL {check.__name__}: {exc}')
    print(f'{name}: {passed}/{len(checks)} supplemental check groups passed')

def legacy_nodes(module):
    result = {}
    for node in ast.parse(inspect.getsource(module)).body:
        if isinstance(node, ast.FunctionDef):
            result[node.name] = ast.dump(node)
        if isinstance(node, ast.ClassDef):
            for method in node.body:
                if isinstance(method, ast.FunctionDef) and method.name != 'get_many':
                    result[f'{node.name}.{method.name}'] = ast.dump(method)
    return result
baseline = legacy_nodes(mods['before'])
for name in ('proposal_k', 'proposal_r'):
    candidate = legacy_nodes(mods[name])
    print(f'{name}: changed legacy functions = {[key for key in baseline if candidate.get(key) != baseline[key]]}')
ordinary_expiry(mods['before'].Cache)
print('before: ordinary expiry boundary probe passed')
