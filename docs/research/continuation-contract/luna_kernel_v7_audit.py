"""Verify V7 against exact V5 interface and unchanged original control receipts."""
import json
import sys
from pathlib import Path
import native_luna_ack_output_v5 as v5
from app_server_native import usage


def audit(root, previous, out):
    root, previous = Path(root), Path(previous)
    m = json.loads((root/'manifest.json').read_text()); v5.verify(m)
    p = root/'on/receipts/run'; s = json.loads((p/'status.json').read_text())
    assert s['state'] == 'closed' and len(s['turns']) == 1
    assert v5.sha(p/'native-events.jsonl') == s['native_events_sha256']
    e = [json.loads(l) for l in (p/'native-events.jsonl').read_text().splitlines()]
    updates = [x for x in e if x.get('method') == 'thread/tokenUsage/updated']
    assert len(updates) == 1 and usage(updates[0]) == s['usage']
    inp = json.loads((p/'turn-1-input.json').read_text())
    old = json.loads((previous/'on/receipts/run/turn-1-input.json').read_text())
    assert inp['input'][0]['text'] == old['input'][0]['text']
    assert inp['effort'] == 'high' and inp['model'] == 'gpt-5.6-luna'
    req = [json.loads(l) for l in (p/'requests.jsonl').read_text().splitlines()]
    start = next(x['params'] for x in req if x.get('method') == 'thread/start')
    assert start['config']['model_instructions_file'] == m['base_file']
    history = b''.join((root/'on/history.jsonl').read_bytes().splitlines(keepends=True)[:49])
    fixture = json.loads((root/'fixture.json').read_text())['events']
    records = [json.loads(l) for l in history.splitlines()]
    assert [r['event'] for r in records] == fixture[:49]
    assert [r['answer'] for r in records] == ['ACK E%02d' % i for i in range(1, 50)]
    decision = json.loads((p/'turn-1-answer.txt').read_text())
    final = v5.render(v5.resolve({**decision, 'authorized': decision['reason'] == 'AUTHORIZED'}, history), history, v5.digest(history))
    assert final == json.loads((root/'rendered.json').read_text())
    v5.grade(json.dumps(final))
    assert v5.check_reason({'distinct_approvers': 1, 'approver_group': 'violet'}, final, decision['reason']) == 'PASS'
    prior = Path(m['prior']); control = json.loads((prior/'off/receipts/run/status.json').read_text())
    assert v5.sha(prior/'off/receipts/run/native-events.jsonl') == control['native_events_sha256']
    native = [json.loads(l) for l in (prior/'off/receipts/run/native-events.jsonl').read_text().splitlines()]
    assert usage([x for x in native if x.get('method') == 'thread/tokenUsage/updated'][-1]) == control['usage']
    a, b = s['usage'], control['usage']
    result = {'classification': 'Known-fixture V7 PASS; reused control; 80/80 not achieved',
        'usage': a, 'control_usage': b,
        'savings_percent': {k: 100*(1-a[k]/b[k]) for k in ('input_tokens', 'output_tokens')},
        'uncached_savings_percent': 100*(1-(a['input_tokens']-a['cached_input_tokens'])/(b['input_tokens']-b['cached_input_tokens'])),
        'segments': 1, 'exact_v5_task_prompt': True, 'exact_and_reason_checks': 'PASS',
        'native_sha256': s['native_events_sha256'], 'manifest_sha256': v5.sha(root/'manifest.json'),
        'base_sha256': v5.sha(Path(m['base_file'])), 'general_capability_parity': 'UNTESTED'}
    v5.save(Path(out), result)
    v5.save(root/'on-hud-status.json', {**s, 'state': 'completed', 'runner': 'app-server', 'source_status_sha256': v5.sha(p/'status.json')})
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    audit(*sys.argv[1:])
