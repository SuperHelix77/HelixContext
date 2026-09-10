"""Verify published hashes and run six frozen implementations without inference."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    grader = ROOT.parent / 'varied_coding_tasks.py'
    audit_path = ROOT.parent / 'LUNA_VARIED_CODING_CONTINUATION_RESULT.json'
    assert digest(grader) == manifest['grader_sha256'], 'Grader changed'
    assert digest(audit_path) == manifest['paired_audit_sha256'], 'Paired audit changed'
    for rel, sha in manifest['files'].items():
        assert digest(ROOT / rel) == sha, rel
    audit = json.loads(audit_path.read_text())
    rows = []
    with tempfile.TemporaryDirectory(prefix='helix-varied-verify-') as temporary:
        stage = Path(temporary)
        for binding in manifest['native_sources']:
            case, arm = binding['case'], binding['arm']
            native = next(r for r in audit['rows'] if (r['case'], r['arm']) == (case, arm))
            for key in ('source_sha256', 'native_sha256'):
                assert binding[key] == native[key], (case, arm, key)
            assert digest(ROOT / case / arm / 'solution.py') == binding['source_sha256']
            source = json.loads((ROOT / case / 'source.json').read_text())
            for name in ('settings.json', 'test_solution.py'):
                assert (ROOT / case / arm / name).read_bytes() == source['files'][name].encode()
            target = stage / case / arm
            shutil.copytree(ROOT / case / arm, target, ignore=shutil.ignore_patterns('__pycache__'))
            # One fresh process per artifact avoids solution/test module-name reuse.
            result = subprocess.run([sys.executable, '-B', str(grader), case, str(target)],
                                    capture_output=True, text=True, check=True, timeout=30)
            checked = json.loads(result.stdout)
            assert checked == native['checks'], (case, arm, checked)
            rows.append({'case': case, 'arm': arm, **checked})
    for rel, sha in manifest['files'].items():
        assert digest(ROOT / rel) == sha, 'Published data mutated: ' + rel
    print(json.dumps({'scope': 'Reproduced finite code checks; native token claims remain extracted receipts, not provider attestations',
                      'rows': rows, 'new_model_calls': 0}, indent=2))


if __name__ == '__main__':
    main()
