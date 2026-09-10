"""Offline grader calibration and byte-exact edit composition. No model calls."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'engine/prototype'))
from evidence import Store
from literal_edits import assemble


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def calibrate(root):
    root = Path(root).resolve()
    if (root / 'calibration.json').exists(): raise ValueError('Preserve prior calibration')
    started = time.perf_counter()
    baseline = HERE / 'baseline'
    manifest = json.loads((HERE / 'BASELINE_MANIFEST.json').read_text())
    for name, info in manifest['files'].items(): assert sha(baseline / name) == info['sha256']
    source = (root / 'reference.py').read_text()
    mutations = {
        'baseline': (baseline / 'workflow_memory.py').read_text(),
        'reference': source,
        'always_all': source.replace("(' AND ' if match_mode=='all' else ' OR ')", "' AND '"),
        'always_any': source.replace("(' AND ' if match_mode=='all' else ' OR ')", "' OR '"),
        'missing_mode_validation': source.replace("        if not isinstance(match_mode,str) or match_mode not in ('all','any'):\n            raise ValueError('Invalid match mode')\n", ''),
        'cross_project_leak': source.replace('AND e.project=?', 'AND ? IS NOT NULL'),
        'ascending': source.replace('ORDER BY e.ordinal DESC LIMIT ?', 'ORDER BY e.ordinal ASC LIMIT ?'),
        'skip_integrity': source.replace('            self._check_index(db,project)', '            pass'),
        'raw_fts_operators': source.replace("match=(' AND ' if match_mode=='all' else ' OR ').join('\"'+word+'\"' for word in words)", 'match=query'),
    }
    assert len(set(mutations.values())) == len(mutations), 'A mutant did not change the reference'
    rows = []
    for name, text in mutations.items():
        cwd = root / name; shutil.copytree(baseline, cwd)
        (cwd / 'workflow_memory.py').write_text(text)
        shutil.copyfile(HERE / 'test_search_mode_public.py', cwd / 'test_search_mode_public.py')
        result = subprocess.run([sys.executable, str(HERE / 'oracle.py'), str(cwd)],
                                cwd=cwd, capture_output=True, timeout=60)
        (cwd / 'oracle.stdout').write_bytes(result.stdout); (cwd / 'oracle.stderr').write_bytes(result.stderr)
        passed = result.returncode == 0
        assert passed == (name == 'reference'), name
        row = {'variant': name, 'exit_code': result.returncode, 'source_sha256': sha(cwd / 'workflow_memory.py'),
               'expected_result': 'PASS' if name == 'reference' else 'REJECT',
               'stdout_sha256': sha(cwd / 'oracle.stdout'), 'stderr_sha256': sha(cwd / 'oracle.stderr')}
        if passed: row['oracle'] = json.loads(result.stdout)
        rows.append(row)
    reference = root / 'reference'
    tests = subprocess.run([sys.executable, '-m', 'pytest', '-q', 'test_workflow_memory.py', 'test_search_mode_public.py'],
                           cwd=reference, capture_output=True, timeout=60)
    (root / 'reference-tests.stdout').write_bytes(tests.stdout); (root / 'reference-tests.stderr').write_bytes(tests.stderr)
    assert tests.returncode == 0, tests.stdout.decode()
    store = Store(root / 'assembly-store')
    key = store.put((baseline / 'workflow_memory.py').read_bytes())['sha256']
    assembled, receipt = assemble(store, key, (root / 'reference-edits.json').read_text())
    assert assembled == (root / 'reference.py').read_bytes()
    report = {'classification': 'Offline correctness/representation gate only; no native economics or model capability claim',
              'baseline_manifest_sha256': sha(HERE / 'BASELINE_MANIFEST.json'), 'rows': rows,
              'reference_tests': tests.stdout.decode().strip(), 'exact_edit_assembly': receipt,
              'representation': json.loads((root / 'representation.json').read_text()),
              'source_sha256': {str(p.relative_to(REPO)): sha(p) for p in [Path(__file__), HERE / 'oracle.py',
                                HERE / 'TASK.md', HERE / 'test_search_mode_public.py', REPO / 'engine/prototype/literal_edits.py']},
              'elapsed_seconds': time.perf_counter()-started, 'native_model_calls': 0,
              'limits': ['Investigator-authored requirement and finite oracle; not a population holdout.',
                         'Private reference and mutations are calibration artifacts and must not enter model workspaces.',
                         'Native control may already produce smaller edits; byte savings do not predict token savings.',
                         'Model integration/reasoning, full setup, SQLite/physical I/O and research costs need separate accounting.']}
    (root / 'calibration.json').write_text(json.dumps(report, indent=2) + '\n')
    (HERE / 'OFFLINE_CALIBRATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'variants': len(rows), 'reference_tests': report['reference_tests'],
                      'oracle_cases': next(r['oracle']['finite_cases'] for r in rows if r['variant']=='reference'),
                      'exact_source_assembly': True, 'native_calls': 0, 'seconds': report['elapsed_seconds']}))


if __name__ == '__main__': calibrate(sys.argv[1])
