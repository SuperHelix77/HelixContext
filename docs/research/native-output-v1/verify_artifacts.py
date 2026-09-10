"""Regrade all four artifacts and cross-apply all observed semantic probes."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
FILES = HERE / 'artifacts'
BASE = HERE.with_name('maintenance-copy-v1')


def sha(raw): return hashlib.sha256(raw).hexdigest()


def verify(destination=None):
    manifest = json.loads((FILES / 'MANIFEST.json').read_text())
    for name, digest in manifest['files'].items(): assert sha((FILES / name).read_bytes()) == digest, name
    for name, digest in manifest['shared_files'].items(): assert sha((HERE.parent / name).read_bytes()) == digest, name
    probes = sorted(FILES.glob('*/*/probe-*.py')); assert len(probes) == 3
    rows = []; identities = set()
    for model, name in [('astra-xhigh', 'ASTRA_XHIGH_RESULT.json'), ('sol-high', 'SOL_HIGH_RESULT.json')]:
        raw = (HERE / name).read_bytes(); assert sha(raw) == manifest['reports'][name]
        report = json.loads(raw)
        for row in report['rows']:
            folder = FILES / model / row['arm']
            updates = [json.loads(x) for x in (folder / 'usage.jsonl').read_text().splitlines()]
            assert len(updates) == row['segments']
            assert row['thread_id'] not in identities; identities.add(row['thread_id'])
            assert {u['params']['threadId'] for u in updates} == {row['thread_id']}
            for label, native in [('input_tokens','inputTokens'),('output_tokens','outputTokens'),
                                  ('cached_input_tokens','cachedInputTokens'),('reasoning_output_tokens','reasoningOutputTokens')]:
                assert sum(e['params']['tokenUsage']['last'][native] for e in updates) == row['usage'][label]
                assert updates[-1]['params']['tokenUsage']['total'][native] == row['usage'][label]
            assert sha((folder / 'workflow_memory.py').read_bytes()) == row['source_sha256']
            with tempfile.TemporaryDirectory(prefix='helix-native-final-check-') as tmp:
                cwd = Path(tmp); shutil.copyfile(folder / 'workflow_memory.py', cwd / 'workflow_memory.py')
                for n in ('evidence.py', 'test_workflow_memory.py'): shutil.copyfile(BASE / 'baseline' / n, cwd / n)
                shutil.copyfile(BASE / 'test_search_mode_public.py', cwd / 'test_search_mode_public.py')
                commands = [(sys.executable,'-B','-m','pytest','-q'), (sys.executable,'-B',str(BASE / 'oracle.py'),str(cwd))]
                receipts = []
                for command in commands:
                    p = subprocess.run(command, cwd=cwd, capture_output=True, timeout=45)
                    assert p.returncode == 0, (p.stdout,p.stderr)
                    receipts.append({'exit': p.returncode, 'stdout': p.stdout.decode(), 'stderr':p.stderr.decode()})
                assert '23 passed' in receipts[0]['stdout'] and json.loads(receipts[1]['stdout'])['finite_cases'] == 94
                for probe in probes:
                    p = subprocess.run([sys.executable,'-B','-'],input=probe.read_bytes(),cwd=cwd,capture_output=True,timeout=45)
                    assert p.returncode == 0, (probe,p.stdout,p.stderr)
                    receipts.append({'probe':str(probe.relative_to(FILES)), 'exit':0,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()})
                assert sha((cwd / 'workflow_memory.py').read_bytes()) == row['source_sha256']
                rows.append({'model':model,'arm':row['arm'],'checks':receipts})
    result = {'classification':'Offline cross-replay of finite behavioral checks; no universal capability claim',
              'artifacts':4,'public_tests_each':23,'independent_cases_each':94,'semantic_probe_programs_each':3,
              'all_observed_semantic_probes_pass_on_all_artifacts':True,'native_model_calls':0,'rows':rows}
    if destination:
        with Path(destination).open('x') as handle: handle.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'}))


if __name__ == '__main__': verify(sys.argv[1] if len(sys.argv)>1 else None)
