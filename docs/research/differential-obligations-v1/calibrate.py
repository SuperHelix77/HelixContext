"""Offline, exposed variant calibration. No candidate data seeds native prompts."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('differential_compare', HERE / 'compare.py')
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
VALID = HERE.with_name('astra-reuse-v1') / 'artifacts/sample_a-on/workflow_memory.py'
BEFORE = c.BASE / 'baseline/workflow_memory.py'


def replacement(raw, old, new):
    assert raw.count(old) == 1, 'Ambiguous calibration mutation'
    result = raw.replace(old, new)
    compile(result, 'calibration', 'exec')
    return result


def variants():
    raw = VALID.read_bytes()
    mode = b"        if not isinstance(match_mode,str) or match_mode not in ('all','any'):\n            raise ValueError('Invalid search match mode')\n"
    return {
        'valid': raw,
        'known_default_limit': replacement(raw, b'query,limit=10,', b'query,limit=9,'),
        'reverse_order': replacement(raw, b'ORDER BY e.ordinal DESC LIMIT', b'ORDER BY e.ordinal ASC LIMIT'),
        'wrong_default_mode': replacement(raw, b"limit=10,match_mode='all'", b"limit=10,match_mode='any'"),
        'missing_integrity': replacement(raw, b'            self._check_index(db,project)\n', b''),
        'any_wrong_limit': replacement(raw, b'        words=re.findall', b"        if match_mode=='any' and limit==10:limit=9\n        words=re.findall"),
        'late_mode_validation': replacement(replacement(raw, mode, b''), b'        if not words:return []\n', b'        if not words:return []\n' + mode),
        # Deliberately outside the frozen query corpus. Do not add its trigger to win.
        'uncovered_query': replacement(raw, b'        words=re.findall', b"        if query=='unlisted_token':return []\n        words=re.findall"),
    }


def run(root):
    started = time.perf_counter(); root = Path(root).resolve(); root.mkdir(parents=True, exist_ok=False)
    sources = root / 'sources'; sources.mkdir()
    inputs = variants()
    for name, raw in inputs.items():
        (sources / (name + '.py')).write_bytes(raw)
    manifest = {'scope': 'Exposed offline development variants; not a holdout or model benchmark',
                'sources': {name: hashlib.sha256(raw).hexdigest() for name, raw in inputs.items()},
                'design_sha256': c.sha(HERE / 'DESIGN.md'), 'runner_sha256': c.sha(Path(__file__)),
                'comparator_sha256': c.sha(HERE / 'compare.py'),
                'expected_no_difference': ['valid', 'uncovered_query'],
                'native_calls': 0}
    (root / 'MANIFEST.json').write_bytes(c.encode(manifest))
    rows = []
    for name in inputs:
        candidate = sources / (name + '.py')
        receipt = c.compare(BEFORE, candidate, root / name, c.binding(BEFORE, candidate))
        observed = receipt['difference_count'] > 0
        expected = name not in ('valid', 'uncovered_query')
        assert observed == expected, name
        if name == 'uncovered_query':
            # Separate explicit witness of coverage incompleteness; not added to suite.
            Memory = c.load(candidate, 'coverage_gap')
            Reference = c.load(VALID, 'coverage_gap_valid')
            a = Reference(c.Store(root / 'gap-reference')); b = Memory(c.Store(root / 'gap-mutant'))
            for m in (a, b): m.record('p', 's', 'one', b'unlisted_token')
            assert a.search('p', 'unlisted_token') != b.search('p', 'unlisted_token')
        rows.append({'case': name, 'expected_difference': expected,
                     'state': receipt['state'], 'difference_count': receipt['difference_count'],
                     'families': receipt['families'], 'cases': receipt['case_count'],
                     'seconds': receipt['seconds'], 'store_io': receipt['store_io'],
                     'receipt_sha256': c.sha(root / name / 'receipt.json'), 'outcomes': receipt['outcomes']})
        print(json.dumps({'case': name, 'differences': receipt['difference_count'],
                          'cases': receipt['case_count'], 'seconds': receipt['seconds']}), flush=True)
    result = {'state': 'OFFLINE_CALIBRATION_COMPLETE', 'rows': rows, 'model_calls': 0,
              'manifest_sha256': c.sha(root / 'MANIFEST.json'),
              'elapsed_seconds': time.perf_counter() - started,
              'known_and_constructed_variants_detected': 6, 'known_coverage_hole_retained': True,
              'semantic_equivalence': 'UNESTABLISHED', 'native_economics': 'UNMEASURED',
              'model_capability_parity': 'UNESTABLISHED', 'production_admission': False}
    (root / 'RESULT.json').write_bytes(c.encode(result))
    return result


if __name__ == '__main__':
    run(sys.argv[1])
