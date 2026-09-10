"""Publish task-only derivatives after the frozen native audit; no inference.

Provider streams remain local. Public hashes verify these derivatives and their
connection to the locally audited stream, not independent provider attestation.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shlex
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'engine/hud'))
import pricing


def sha(raw): return hashlib.sha256(raw).hexdigest()
def save(path, value): path.write_text(json.dumps(value, indent=2) + '\n')


def main(root):
    root = Path(root).resolve(); out = HERE / 'artifacts'; out.mkdir(exist_ok=False)
    manifest = {'classification': 'Task-only derivatives of fresh known development pilots; not population parity',
                'reports': {}, 'files': {}, 'shared_files': {}, 'created_at': datetime.now(timezone.utc).isoformat()}
    anatomy = {}
    for model, report_name in [('sol-high', 'SOL_HIGH_RESULT.json')]:
        base = root; raw_report = (base / 'audit.json').read_bytes()
        assert raw_report == (HERE / report_name).read_bytes()
        report = json.loads(raw_report); manifest['reports'][report_name] = sha(raw_report)
        results = json.loads((base / 'results.json').read_text())
        assert results['state'] == 'AWAITING_AUDIT'
        anatomy[model] = []
        for row in report['rows']:
            arm = row['arm']; directory = out / model / arm; directory.mkdir(parents=True)
            events_raw = (base / (arm + '-run') / 'native-events.jsonl').read_bytes()
            assert sha(events_raw) == row['native_sha256']
            events = [json.loads(line) for line in events_raw.splitlines()]
            native_row = next(r for r in results['rows'] if r['arm'] == arm)
            answer = native_row['turns'][-1]['answer']
            source = (base / arm / 'workflow_memory.py').read_bytes()
            assert sha(source) == row['source_sha256']
            (directory / 'workflow_memory.py').write_bytes(source)
            (directory / 'final-answer.md').write_text(answer)
            updates = [e for e in events if e.get('method') == 'thread/tokenUsage/updated']
            (directory / 'usage.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in updates))
            calls = []; probes = []; segments = []; pending = []
            for i, event in enumerate(events):
                method = event.get('method'); item = event.get('params', {}).get('item', {})
                if method == 'item/tool/call':
                    calls.append(event); pending.append({'kind': 'internal_edit', 'event': i})
                elif method == 'item/completed' and item.get('type') == 'dynamicToolCall':
                    calls.append(event)
                elif method == 'item/completed' and item.get('type') == 'commandExecution':
                    command = item['command']; output = item.get('aggregatedOutput') or ''
                    pending.append({'kind': 'command', 'event': i, 'command': command,
                                    'output_bytes': len(output.encode()), 'exit_code': item['exitCode']})
                    if ('Supplemental checks passed:' in output or '12 additional semantic assertions passed:' in output
                            or 'literal-operator probe passed' in output or 'focused search-mode checks passed' in output):
                        assert item['exitCode'] == 0
                        outer = shlex.split(command); assert outer[0] == '/bin/zsh' and outer[1] == '-lc'
                        shell = outer[2]
                        if "<<'PY'\n" in shell:
                            code = shell.split("<<'PY'\n", 1)[1].rsplit('\nPY', 1)[0] + '\n'
                        else:
                            inner = shlex.split(shell); at = inner.index('-c'); code = inner[at + 1] + '\n'
                        name = f'probe-{len(probes)+1}.py'; (directory / name).write_text(code)
                        probes.append({'path': name, 'event_index': i, 'command': command,
                                       'observed_stdout': output, 'sha256': sha(code.encode())})
                elif method == 'thread/tokenUsage/updated':
                    segments.append({'usage': event['params']['tokenUsage']['last'], 'observable_operations': pending})
                    pending = []
            assert not pending
            save(directory / 'internal-calls.json', calls)
            save(directory / 'probe-provenance.json', probes)
            anatomy[model].append({'arm': arm, 'segments': segments, 'final_answer_bytes': len(answer.encode()),
                                   'probes': len(probes), 'native_sha256': row['native_sha256'],
                                   'attribution_limit': 'Operations grouped by observed usage update; not causal token allocation or hidden reasoning'})
    save(out / 'ANATOMY.json', anatomy)
    raw = pricing.fetch(); (out / 'pricing-source.md').write_bytes(raw)
    rates = pricing.parse(raw)
    costs = {'source': pricing.SOURCE, 'source_sha256': sha(raw), 'checked_at': datetime.now(timezone.utc).isoformat(),
             'scope': 'Dated Standard API-equivalent scenarios, not Codex quota/bills or total effective cost', 'models': {}}
    for model, name in [('sol-high', 'SOL_HIGH_RESULT.json')]:
        report = json.loads((HERE / name).read_text()); values = {r['arm']: pricing.estimate(r['usage'], rates[r['model']]) for r in report['rows']}
        costs['models'][model] = {'costs': values, 'saved_percent': {k: (1-values['on'][k]/values['off'][k])*100 for k in ('short', 'long')}}
    save(out / 'COST.json', costs)
    for path in out.rglob('*'):
        if path.is_file(): manifest['files'][str(path.relative_to(out))] = sha(path.read_bytes())
    for name in ('baseline/evidence.py','baseline/workflow_memory.py','baseline/test_workflow_memory.py','test_search_mode_public.py','oracle.py'):
        path = HERE.with_name('maintenance-copy-v1') / name
        manifest['shared_files'][str(path.relative_to(HERE.parent))] = sha(path.read_bytes())
    save(out / 'MANIFEST.json', manifest)
    print(json.dumps({'artifacts': str(out), 'files': len(manifest['files']), 'model_calls': 0}))


if __name__ == '__main__': main(sys.argv[1])
