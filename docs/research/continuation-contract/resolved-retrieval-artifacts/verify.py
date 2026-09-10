"""Offline artifact/Engine verification, never a model invocation.

Native counters are commitments to local receipts, not provider attestations.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path[:0] = [str(HERE.parent), str(REPO / 'engine/prototype')]
from luna_resolved_retrieval_pair import expected, equal
from bound_retrieval import dispatch, state_root
from evidence import Store


def main():
    manifest = json.loads((HERE / 'manifest.json').read_text())
    for group, base in [('files', HERE), ('implementation', REPO)]:
        for name, digest in manifest[group].items():
            path = (base / name).resolve()
            if not path.is_relative_to(base) or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError('Artifact or implementation changed: ' + name)

    def unexpected_semantics(*_):
        raise AssertionError('Closed request unexpectedly requested inference')

    results = []
    for case in ('selection', 'cold'):
        root = HERE / case
        spec = json.loads((root / 'source.json').read_text())
        state = json.loads((root / 'task-state.json').read_text())
        raw = (root / spec['filename']).read_bytes()
        assert equal(json.loads(raw), spec['source'])
        with tempfile.TemporaryDirectory() as tmp:
            reference = Store(tmp).put(raw)
            assert reference == state['source_ref']
            store = Store(tmp)
            actual = dispatch(spec['task'], store, reference,
                              expected_state_root=state_root(state),
                              current_state=lambda: state, semantic=unexpected_semantics)
            oracle = expected(case, spec)
            assert actual['state'] == 'RESOLVED' and actual['model_calls'] == 0
            assert equal(actual['answer'], oracle)
            for arm in ('off', 'on'):
                assert equal(json.loads((root / (arm + '-answer.json')).read_text()), oracle)
            results.append({'case': case, 'exact_answers': 2, 'replay': 'PASS',
                            'model_calls': 0, 'source_bytes': len(raw),
                            'recovery_bytes_read': store.metrics['object_bytes_read']})
    print(json.dumps({'checks': 'PASS', 'cases': results,
                      'native_usage_independently_authenticated': False}, indent=2))


if __name__ == '__main__':
    main()
