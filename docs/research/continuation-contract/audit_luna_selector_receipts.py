"""Close the older selector's HUD receipt gap without inference or regrading rules."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path[:0] = [str(REPO / 'engine/output'), str(REPO / 'engine/prototype')]
from app_server_native import usage
from native_luna_ack_pair import grade
from policy_realization import realize


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(root):
    root = Path(root).resolve()
    manifest = json.loads((root / 'manifest.json').read_text())
    result = json.loads((root / 'results.json').read_text())
    prior = Path(manifest['prior'])
    published = json.loads((HERE / 'MINIMAL_SELECTION_LUNA_RESULT.json').read_text())
    control = json.loads((HERE / 'ASSEMBLED_LUNA_PAIR_RESULT.json').read_text())['rows'][0]
    assert sha(root / 'manifest.json') == result['manifest_sha256'] == published['manifest_sha256']
    for path in (root / 'on/history.jsonl', root / 'fixture.json', REPO / 'engine/prototype/policy_realization.py',
                 REPO / 'benchmarks/frozen-high/evaluator/long-horizon-gold.json', prior / 'results.json'):
        assert sha(path) == manifest['sha256'][str(path)], path
    history = (root / 'on/history.jsonl').read_bytes()
    events = json.loads((root / 'fixture.json').read_text())['events']
    assert [json.loads(line)['event'] for line in history.splitlines()] == events[:49]
    rows = []
    for arm, run, expected in [('off', prior / 'off/receipts/run', control),
                               ('on', root / 'on/receipts/run', published)]:
        status = json.loads((run / 'status.json').read_text())
        assert status['state'] == 'closed' and status['model'] == 'gpt-5.6-luna' and status['effort'] == 'high'
        assert sha(run / 'native-events.jsonl') == status['native_events_sha256'] == expected['native_sha256']
        assert status['usage'] == expected['usage']
        stream = [json.loads(line) for line in (run / 'native-events.jsonl').read_text().splitlines()]
        updates = [e for e in stream if e.get('method') == 'thread/tokenUsage/updated']
        assert usage(updates[-1]) == status['usage']
        for key, native in [('input_tokens', 'inputTokens'), ('output_tokens', 'outputTokens'),
                            ('cached_input_tokens', 'cachedInputTokens'), ('reasoning_output_tokens', 'reasoningOutputTokens')]:
            assert sum(e['params']['tokenUsage']['last'][native] for e in updates) == status['usage'][key]
        items = [e['params']['item'] for e in stream if e.get('method') == 'item/completed']
        assert not any(i['type'] in ('commandExecution', 'mcpToolCall', 'dynamicToolCall') for i in items)
        answers = [i['text'] for i in items if i['type'] == 'agentMessage']
        turns = 50 if arm == 'off' else 1
        assert len(status['turns']) == len(answers) == len(updates) == turns
        assert all(t['state'] == 'completed' for t in status['turns'])
        if arm == 'off':
            assert [a.strip() for a in answers[:49]] == ['ACK ' + e['event_id'] for e in events[:49]]
            answer = answers[-1]
        else:
            selection = json.loads(answers[-1])
            assert selection == result['selection'] == published['selection']
            realized = realize(selection, history, hashlib.sha256(history).hexdigest(),
                               {'subject': 'ORION-42', 'distinct_approvers': 1, 'approver_group': 'violet'})
            assert realized == result['realized'] == published['realized']
            answer = json.dumps(realized['answer'])
        grade(answer)
        rows.append({'arm': arm, 'model': status['model'], 'effort': status['effort'], 'usage': status['usage'],
                     'native_sha256': status['native_events_sha256'], 'checks': 'PASS',
                     'segments': len(updates), 'model_answer': answers[-1], 'final_answer': answer})
    report = {'classification': 'Receipt-only re-audit of adaptive Luna selector and reused control; not a fresh pair or general release',
              'rows': rows, 'manifest_sha256': sha(root / 'manifest.json'),
              'limits': ['Older sessions have native streams but no separately captured raw rollout in these run directories.',
                         'Current re-audit checks counters, answers, bound realization and original finite grader; it does not rerun historical base/config or crash-recovery qualification.',
                         'Candidate inherited prior caller history; preceding preparation and failed candidate costs remain additional.']}
    (HERE / 'MINIMAL_SELECTION_LUNA_RECEIPT_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: native hashes/counters, 49 original control ACKs, one candidate semantic segment, exact history and bound realization; typed finite checks ready for HUD.')


if __name__ == '__main__':
    audit(sys.argv[1])
