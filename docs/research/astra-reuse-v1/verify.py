"""Public hash verification and cross-replay of the two new native probes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def verify():
    artifacts = HERE / 'artifacts'
    manifest = json.loads((artifacts / 'MANIFEST.json').read_text())
    sha = lambda b: hashlib.sha256(b).hexdigest()
    assert sha((HERE / 'RESULT.json').read_bytes()) == manifest['report_sha256']
    for name, digest in manifest['files'].items():
        assert sha((artifacts / name).read_bytes()) == digest, name
    for name, digest in manifest['shared_files'].items():
        assert sha((HERE.parent / name).read_bytes()) == digest, name
    report = json.loads((HERE / 'RESULT.json').read_text())
    rows = []
    for sample, defective in [('sample_a', False), ('sample_b', True)]:
        with tempfile.TemporaryDirectory(prefix='helix-astra-probe-replay-') as tmp:
            work = Path(tmp)
            base = HERE.with_name('maintenance-copy-v1') / 'baseline'
            (work / 'before.py').write_bytes((base / 'workflow_memory.py').read_bytes())
            (work / 'evidence.py').write_bytes((base / 'evidence.py').read_bytes())
            source = (artifacts / (sample + '-on') / 'workflow_memory.py').read_bytes()
            (work / 'workflow_memory.py').write_bytes(source)
            source_refs = {r['source_sha256'] for r in report['rows'] if r['case'] == sample}
            assert source_refs == {sha(source)}
            for arm in ('off', 'on'):
                raw = (artifacts / ('sample_b-' + arm) / 'new-semantic-probe.py').read_bytes()
                p = subprocess.run([sys.executable, '-B', '-'], input=raw, cwd=work,
                                   capture_output=True, timeout=45)
                # Ordinary probe asserts the discovered defect exists; prepared
                # probe asserts API compatibility. Their expected exits differ.
                expected_pass = defective if arm == 'off' else not defective
                assert (p.returncode == 0) == expected_pass, (sample, arm, p.stdout, p.stderr)
                assert (work / 'workflow_memory.py').read_bytes() == source
                rows.append({'case': sample, 'probe_arm': arm, 'exit_status': p.returncode,
                             'expected_pass': expected_pass, 'source_unchanged': True,
                             'stdout_sha256': sha(p.stdout), 'stderr_sha256': sha(p.stderr)})
    result = {'classification': 'Exact native-probe cross-replay, finite semantic evidence only',
              'native_model_calls': 0, 'all_expected_outcomes': True, 'rows': rows}
    (HERE / 'PUBLIC_VERIFICATION.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'artifact_hashes': 'PASS', 'native_probe_cross_replays': 4,
                      'all_expected_outcomes': True, 'native_model_calls': 0}))


if __name__ == '__main__': verify()
