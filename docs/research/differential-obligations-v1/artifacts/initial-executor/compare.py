"""Finite explicit Memory.search relations; observations, not semantic approval.

Trusted research modules only, disposable stores, no native model invocation.
The caller must bind the task, baseline, candidate, executor and evidence module.
"""
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import re
import sqlite3
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE = HERE.with_name('maintenance-copy-v1')
sys.path.insert(0, str(BASE / 'baseline'))
from evidence import Store


def encode(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Memory


def binding(before, candidate):
    paths = [Path(before), Path(candidate), Path(__file__), HERE / 'DESIGN.md',
             BASE / 'TASK.md', BASE / 'baseline/evidence.py', Path(sys.executable)]
    return {'files': {str(p.resolve()): sha(p) for p in paths},
            'runtime': {'python': sys.version, 'sqlite': sqlite3.sqlite_version}}


def guard(bound):
    if bound['runtime'] != {'python': sys.version, 'sqlite': sqlite3.sqlite_version}:
        raise ValueError('Runtime binding changed')
    for p, digest in bound['files'].items():
        if sha(p) != digest:
            raise ValueError('Source/task/executor binding changed: ' + p)


def state(memory):
    with memory.db() as db:
        return [db.execute('SELECT * FROM events ORDER BY ordinal').fetchall(),
                db.execute('SELECT rowid,body FROM search ORDER BY rowid').fetchall()]


def outcome(function):
    try:
        value = function()
    except (ValueError, TypeError, sqlite3.Error) as exc:
        return {'exception': type(exc).__name__, 'message': str(exc)}
    result = {'return': value}
    encode(result)  # Unsupported observation is a harness failure, not equality.
    return result


def compare(before, candidate, root, expected_binding):
    begin = time.perf_counter(); guard(expected_binding)
    if expected_binding != binding(before, candidate):
        raise ValueError('Incomplete or mismatched caller binding')
    root = Path(root); root.mkdir(parents=True, exist_ok=False)
    Old = load(before, 'helix_obligations_reference')
    New = load(candidate, 'helix_obligations_candidate')
    default = inspect.signature(Old.search).parameters['limit'].default
    if type(default) is not int or not 1 <= default <= 97:
        raise ValueError('Unsupported baseline default/corpus bound')
    queries = ['alpha beta', 'alpha OR beta', '"alpha" OR (beta*)',
               'café blue_green', 'missing', '', '!!!']
    sizes = sorted({0, 1, default - 1, default, default + 1, default + 2})
    rows = []; stores = []; observation_calls = 0

    def observe(function):
        nonlocal observation_calls
        observation_calls += 1
        return outcome(function)

    def record(family, inputs, wanted, got, unchanged):
        rows.append({'family': family, 'inputs': inputs, 'reference': wanted,
                     'candidate': got, 'relation_holds': encode(wanted) == encode(got),
                     'tables_unchanged': unchanged})

    for n in sizes:
        old_store = Store(root / ('old-' + str(n)))
        new_store = Store(root / ('new-' + str(n)))
        old = Old(old_store); new = New(new_store); stores += [old_store, new_store]
        for m in (old, new):
            for i in range(n):
                m.record('p', 's', 'n' + str(i), b'alpha beta')
            for i, raw in enumerate([b'alpha', b'beta', b'OR', b'alpha OR beta',
                                     'café blue_green'.encode(), b'unrelated\x00\xff']):
                m.record('p', 's', 'extra' + str(i), raw)
            m.record('other', 's', 'cross-project', b'alpha beta')
        baseline_state = state(old); candidate_state = state(new)
        for query in queries:
            for limit in (None, 1, default, 100):
                args = ('p', query) if limit is None else ('p', query, limit)
                wanted = observe(lambda: old.search(*args))
                got = observe(lambda: new.search(*args))
                record('legacy', {'size': n, 'args': args}, wanted, got,
                       state(old) == baseline_state and state(new) == candidate_state)
                got = observe(lambda: new.search(*args, match_mode='all'))
                record('explicit_all', {'size': n, 'args': args}, wanted, got,
                       state(new) == candidate_state)
                words = re.findall(r'\w+', query, flags=re.UNICODE)
                # Corpus <100, so each baseline single-word query is complete here.
                union = {}
                for word in words:
                    result = observe(lambda: old.search('p', word, 100))
                    if 'return' not in result:
                        raise ValueError('Reference valid query failed; relation undefined')
                    for ref in result['return']:
                        union[ref['record_hash']] = ref
                expected = sorted(union.values(), key=lambda r: r['ordinal'], reverse=True)
                expected = expected[:default if limit is None else limit]
                got = observe(lambda: new.search(*args, match_mode='any'))
                record('literal_union_any', {'size': n, 'args': args}, {'return': expected}, got,
                       state(old) == baseline_state and state(new) == candidate_state)
        # Caller-selected invalid input observations; no normalization of exceptions.
        for args in [('p', None), ('p', []), ('p', True), ('p', 'alpha', True),
                     ('p', 'alpha', 0), ('p', 'alpha', 101), ('', 'alpha')]:
            record('invalid_legacy', {'size': n, 'args': args},
                   observe(lambda: old.search(*args)), observe(lambda: new.search(*args)),
                   state(new) == candidate_state)
        for mode in (None, 1, [], 'invalid'):
            for query in ('', 'alpha'):
                got = observe(lambda: new.search('p', query, match_mode=mode))
                rows.append({'family': 'invalid_mode', 'inputs': {'size': n, 'mode': mode, 'query': query},
                             'reference': {'required_exception': 'ValueError'}, 'candidate': got,
                             'relation_holds': got.get('exception') == 'ValueError',
                             'tables_unchanged': state(new) == candidate_state})
        # Remove a nonmatching index row: legacy contract checks beyond result limit.
        for m in (old, new):
            with m.db() as db:
                db.execute("DELETE FROM search WHERE rowid=(SELECT ordinal FROM events WHERE project='p' AND event_id='extra5')")
        old_corrupt = state(old); new_corrupt = state(new)
        args = ('p', 'alpha', 1)
        wanted = observe(lambda: old.search(*args))
        if wanted.get('exception') != 'ValueError':
            raise ValueError('Reference corruption witness invalid')
        for mode in (None, 'all', 'any'):
            got = observe(lambda: new.search(*args) if mode is None else new.search(*args, match_mode=mode))
            record('nonmatching_corruption', {'size': n, 'args': args, 'mode': mode}, wanted, got,
                   state(old) == old_corrupt and state(new) == new_corrupt)
    guard(expected_binding)  # No valid receipt if observed source/contract drifted.
    raw = encode(rows); path = root / 'outcomes.json'; path.write_bytes(raw)
    differences = [i for i, r in enumerate(rows) if not r['relation_holds'] or not r['tables_unchanged']]
    metrics = {k: sum(s.metrics[k] for s in stores) for k in stores[0].metrics}
    result = {
        'schema': 'helix.differential-observations.v1',
        'state': 'DIFFERENCES_OBSERVED' if differences else 'NO_DIFFERENCE_IN_ENUMERATED_CASES',
        'case_count': len(rows), 'observation_calls': observation_calls,
        'difference_count': len(differences), 'difference_indices': differences,
        'families': {name: {'cases': sum(r['family'] == name for r in rows),
                           'differences': sum(r['family'] == name and i in differences for i, r in enumerate(rows))}
                     for name in sorted({r['family'] for r in rows})},
        'outcomes': {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw), 'path': str(path.resolve())},
        'binding': expected_binding, 'seconds': time.perf_counter() - begin,
        'store_io': metrics, 'full_physical_io': 'UNMEASURED', 'model_calls': 0,
        'semantic_adequacy': 'UNESTABLISHED; model/caller must judge relation applicability and remaining obligations',
        'execution_boundary': 'Trusted local modules in disposable stores; no hostile-code sandbox guarantee',
    }
    (root / 'receipt.json').write_bytes(encode(result))
    return result


if __name__ == '__main__':
    before, candidate, root = sys.argv[1:4]
    result = compare(before, candidate, root, binding(before, candidate))
    print(json.dumps({k: result[k] for k in ('state', 'case_count', 'difference_count', 'seconds', 'model_calls')}))
