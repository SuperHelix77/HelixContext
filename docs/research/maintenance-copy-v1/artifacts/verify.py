"""Verify public derivatives and recheck both artifacts, without inference.

Native excerpt hashes bind the released excerpts, not independently attest the
private provider stream. The separate original audit binds full raw receipts.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
REPO = PARENT.parents[2]
sys.path.insert(0, str(REPO / 'engine/prototype'))
from evidence import Store
from literal_edits import assemble


def verify():
    bound = json.loads((HERE / 'MANIFEST.json').read_text())
    for name, h in bound['files'].items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == h, name
    report = json.loads((PARENT / 'RECONCILED_RESULT.json').read_text())
    assert hashlib.sha256((PARENT / 'RECONCILED_RESULT.json').read_bytes()).hexdigest() == bound['report_sha256']
    totals = {}; identities = set()
    for row in report['rows']:
        arm = row['arm']
        events = [json.loads(x) for x in (HERE / (arm + '-usage.jsonl')).read_text().splitlines()]
        assert len(events) == row['segments']
        assert {e['params']['threadId'] for e in events} == {row['thread_id']}
        assert row['thread_id'] not in identities; identities.add(row['thread_id'])
        pairs = [('input_tokens', 'inputTokens'), ('output_tokens', 'outputTokens'),
                 ('cached_input_tokens', 'cachedInputTokens'), ('reasoning_output_tokens', 'reasoningOutputTokens'),
                 ('cache_write_input_tokens', 'cacheWriteInputTokens')]
        for public, native in pairs:
            assert sum(e['params']['tokenUsage']['last'][native] for e in events) == row['usage'][public]
            assert events[-1]['params']['tokenUsage']['total'][native] == row['usage'][public]
        totals[arm] = row['usage']
        source = HERE / (arm + '-workflow_memory.py')
        assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
        with tempfile.TemporaryDirectory(prefix='helix-maintenance-public-') as folder:
            cwd = Path(folder)
            shutil.copyfile(source, cwd / 'workflow_memory.py')
            for name in ('evidence.py', 'test_workflow_memory.py'):
                shutil.copyfile(PARENT / 'baseline' / name, cwd / name)
            shutil.copyfile(PARENT / 'test_search_mode_public.py', cwd / 'test_search_mode_public.py')
            p = subprocess.run([sys.executable, '-B', '-m', 'pytest', '-q'], cwd=cwd, capture_output=True)
            assert p.returncode == 0 and b'23 passed' in p.stdout, (p.stdout, p.stderr)
            p = subprocess.run([sys.executable, '-B', str(PARENT / 'oracle.py'), str(cwd)], capture_output=True)
            assert p.returncode == 0 and json.loads(p.stdout)['finite_cases'] == 94, (p.stdout, p.stderr)
            p = subprocess.run([sys.executable, '-B', '-'], cwd=cwd,
                               input=(HERE / 'control-semantic-probes.py').read_bytes(), capture_output=True)
            assert p.returncode == 0, (p.stdout, p.stderr)
            if arm == 'on':
                store = Store(cwd / 'copy-store')
                key = store.put((PARENT / 'baseline/workflow_memory.py').read_bytes())['sha256']
                raw, _ = assemble(store, key, (HERE / 'on-answer.json').read_text())
                assert raw == source.read_bytes()
    for key in ('input_tokens', 'output_tokens'):
        assert abs(report['savings_percent'][key] - 100*(1-totals['on'][key]/totals['off'][key])) < 1e-10
    assert not report['clean_frozen_protocol_pass'] and not report['general_release']
    print(json.dumps({'public_derivatives': 'PASS', 'native_segments': sum(x['segments'] for x in report['rows']),
                      'artifacts': 2, 'public_tests_each': 23, 'independent_cases_each': 94,
                      'control_semantic_probes': 'PASS_BOTH', 'exact_candidate_reconstruction': 'PASS',
                      'native_inference_calls': 0, 'original_runner_stop_preserved': True}))


if __name__ == '__main__': verify()
