"""Verify retained public outcomes and replay only the task-admission boundary."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ART = HERE / 'artifacts'


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def verify():
    manifest = json.loads((ART / 'MANIFEST.json').read_text())
    for name, item in manifest['files'].items():
        raw = (ART / name).read_bytes()
        assert len(raw) == item['bytes'] and hashlib.sha256(raw).hexdigest() == item['sha256']
        if 'raw_sha256' in item:
            raw = gzip.decompress(raw)
            assert len(raw) == item['raw_bytes'] and hashlib.sha256(raw).hexdigest() == item['raw_sha256']
    report = json.loads((HERE / 'RESULT.json').read_text())
    cases = 0
    for r in report['rows']:
        rows = json.loads(gzip.decompress((ART / r['outcomes']['archive']).read_bytes()))
        assert len(rows) == r['cases'] == 612
        different = []
        for i, row in enumerate(rows):
            holds = (row['candidate'].get('exception') == 'ValueError'
                     if row['family'] == 'invalid_mode'
                     else encoded(row['reference']) == encoded(row['candidate']))
            assert holds == row['relation_holds']
            if not holds or not row['tables_unchanged']: different.append(i)
        receipt = json.loads((ART / (r['case'] + '-receipt.json')).read_text())
        assert different == receipt['difference_indices']
        assert len(different) == r['difference_count']
        assert bool(different) == r['expected_difference']
        cases += len(rows)
    # Exact old source bytes, evaluated with their original resource location.
    old = {'__name__': 'old_admission_replay', '__file__': str(HERE / 'compare.py')}
    source = (ART / 'initial-executor/compare.py').read_bytes()
    exec(compile(source, str(HERE / 'compare.py'), 'exec'), old)
    spec = importlib.util.spec_from_file_location('closed_admission', HERE / 'compare.py')
    current = importlib.util.module_from_spec(spec); spec.loader.exec_module(current)
    before = current.BASE / 'baseline/workflow_memory.py'
    candidate = ART / 'valid-source.py'
    base = current.BASE
    with tempfile.TemporaryDirectory(prefix='helix-obligation-admission-') as tmp:
        altered = Path(tmp); (altered / 'baseline').mkdir()
        (altered / 'TASK.md').write_text('Change default limit to9; preserving the prior default is no longer required.')
        (altered / 'baseline/evidence.py').write_bytes((base / 'baseline/evidence.py').read_bytes())
        old['BASE'] = altered
        accepted = old['binding'](before, candidate)
        assert str((altered / 'TASK.md').resolve()) in accepted['files']
        current.BASE = altered
        try:
            current.binding(before, candidate)
        except ValueError as exc:
            assert 'Unqualified relation contract' in str(exc)
        else:
            raise AssertionError('Changed task admitted')
        finally:
            current.BASE = base
    return {'state': 'PUBLIC_VERIFICATION_PASS', 'artifact_bindings': len(manifest['files']),
            'exact_archived_case_outcomes': cases, 'old_changed_task_admission': 'REPRODUCED',
            'new_changed_task_rejection': 'PASS', 'model_calls': 0,
            'scope': 'Receipt integrity, enumerated comparisons and admission repair; not general semantic parity'}


if __name__ == '__main__':
    result = verify()
    (HERE / 'PUBLIC_VERIFICATION.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
