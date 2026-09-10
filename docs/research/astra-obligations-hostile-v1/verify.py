"""Verify this public evidence closure; optionally reconcile the private native log."""
import gzip
import hashlib
import json
from pathlib import Path
import shlex
import sys

HERE = Path(__file__).resolve().parent


def sha(raw): return hashlib.sha256(raw).hexdigest()


def verify(private_root=None):
    closure = json.loads((HERE / 'CLOSURE.json').read_text())
    for name, digest in closure['files'].items():
        assert sha((HERE / name).read_bytes()) == digest, name
    a = json.loads((HERE / 'AUDIT.json').read_text())
    art = HERE / 'artifacts'
    assert sha((art / 'final-answer.md').read_bytes()) == a['final_sha256']
    usage = json.loads((art / 'usage.json').read_text())
    fields = {'input_tokens':'inputTokens','output_tokens':'outputTokens',
              'cached_input_tokens':'cachedInputTokens','cache_write_input_tokens':'cacheWriteInputTokens',
              'reasoning_output_tokens':'reasoningOutputTokens'}
    for k,v in fields.items(): assert sum(s[v] for s in usage) == a['usage'][k]
    receipt = json.loads((art / 'comparison-receipt.json').read_text())
    raw = gzip.decompress((art / 'comparison-outcomes.json.gz').read_bytes())
    assert sha(raw) == receipt['outcomes']['sha256'] and len(raw) == receipt['outcomes']['bytes']
    comparisons = json.loads(raw)
    assert len(comparisons) == receipt['case_count'] == 612
    assert all(r['relation_holds'] and r['tables_unchanged'] for r in comparisons)
    commands = json.loads((art / 'commands.json').read_text())
    for c in commands: assert sha(c['output'].encode()) == c['output_sha256']
    code = shlex.split(commands[-1]['command'])[2].split("<<'PY'\n",1)[1]
    assert code.endswith('\nPY') and code[:-3] == (art / 'probe.py').read_text()
    replay = json.loads((art / 'probe-replay.json').read_text())
    assert sha((art / 'probe.py').read_bytes()) == replay['program_sha256']
    for r in replay['rows']:
        b = (art / (r['variant'] + '-probe.stdout')).read_bytes(); assert sha(b) == r['stdout_sha256']
        values = json.loads(b)
        assert values['contract_failures'] == r['contract_failures']
        assert values['control_passes'] == r['controls_passed'] == 9
    assert json.loads(commands[-1]['output']) == json.loads((art / 'observed_defect-probe.stdout').read_text())
    result = {'state':'PASS','public_bindings':len(closure['files']),'comparison_cases':612,
              'native_inference_calls':0,'scope':'Retained evidence consistency; semantic review is separately recorded'}
    if private_root:
        root = Path(private_root)
        native = root / 'native'; raw = (native / 'raw/raw-rollout.jsonl').read_bytes()
        assert sha(raw) == a['raw_capture_sha256']
        counters = []
        for line in raw.splitlines():
            e = json.loads(line); p = e.get('payload', {})
            if e.get('type') == 'event_msg' and p.get('type') == 'token_count' and p.get('info'):
                counters.append(p['info'])
        assert len(counters) == a['segments']
        for k in fields:
            assert counters[-1]['total_token_usage'][k] == a['usage'][k]
            assert sum(c['last_token_usage'][k] for c in counters) == a['usage'][k]
        assert sha((native / 'native-events.jsonl').read_bytes()) == a['native_sha256']
        assert sha((root / 'manifest.json').read_bytes()) == a['manifest_sha256']
        manifest = json.loads((root / 'manifest.json').read_text())
        for name,digest in manifest['bindings'].items(): assert sha(Path(name).read_bytes()) == digest, name
        result['private_native_and_bound_inputs'] = 'PASS'
    print(json.dumps(result,indent=2))


if __name__ == '__main__': verify(sys.argv[1] if len(sys.argv)>1 else None)
