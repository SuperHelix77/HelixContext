"""Read-only receipt audit; no model calls, fixture changes or final repair."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('w50_v2', HERE / 'pilot.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)
KEYS = {
    'input_tokens': 'inputTokens', 'output_tokens': 'outputTokens',
    'cached_input_tokens': 'cachedInputTokens',
    'reasoning_output_tokens': 'reasoningOutputTokens',
    'cache_write_input_tokens': 'cacheWriteInputTokens',
}


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text())


def audit(root):
    root = Path(root).resolve()
    manifest = read(root / 'manifest.json')
    pilot.original.verify(manifest)
    result = read(root / 'results.json')
    assert result['state'] == 'AWAITING_AUDIT'
    assert result['manifest_sha256'] == digest(root / 'manifest.json')
    assert len(result['rows']) == 2
    events = read(root / 'fixture.json')['events']
    rows = []
    for r in result['rows']:
        arm = r['arm']; run = root / (arm + '-run')
        status = read(run / 'status.json')
        assert status['state'] == 'closed' and status['error'] is None
        assert status['model'] == manifest['model']
        assert status['effort'] == manifest['effort']
        assert status['usage'] == r['usage']
        assert status['effective_config_binding']['other_parsed_settings_unchanged']
        assert status['effective_config_binding']['native_overrides_verified']
        assert status['config_sha256'] == digest(pilot.original.CONFIG)
        assert status['registration']['skill_sha256'] == digest(pilot.original.SKILL)
        native = run / 'native-events.jsonl'; raw = run / 'raw/raw-rollout.jsonl'
        assert status['native_events_sha256'] == digest(native)
        assert status['events_sha256'] == digest(run / 'events.jsonl')
        assert status['raw_capture']['sha256'] == digest(raw)
        # Only usage, visible messages and item type metadata are inspected.
        xs = [json.loads(line) for line in native.open()]
        updates = [x['params']['tokenUsage'] for x in xs
                   if x.get('method') == 'thread/tokenUsage/updated']
        segments = []; previous = {k: 0 for k in KEYS}
        for u in updates:
            total = {k: u['total'].get(v, 0) for k, v in KEYS.items()}
            if total == previous:
                continue
            delta = {k: total[k] - previous[k] for k in KEYS}
            assert all(n >= 0 for n in delta.values())
            segments.append(delta); previous = total
        assert previous == r['usage']
        turns = status['turns']
        assert len(turns) == (1 if arm == 'on' else 50)
        assert all(t['state'] == 'completed' for t in turns)
        assert {k: sum(t['usage_delta'][k] for t in turns) for k in KEYS} == r['usage']
        items = [x['params']['item'] for x in xs if x.get('method') == 'item/completed']
        finals = [x['text'] for x in items
                  if x['type'] == 'agentMessage' and x.get('phase') == 'final_answer']
        answer = (run / ('turn-' + str(len(turns)) + '-answer.txt')).read_text()
        assert answer == r['answer'] == r['model_answer'] == finals[-1]
        decoded = pilot.original.grade(answer)
        assert decoded['authorized'] is False
        assert decoded['minimum_distinct_approvers'] == 2
        assert decoded['approver_group'] == 'violet'
        assert {1, 17}.issubset(decoded['evidence_turns'])
        assert isinstance(decoded['explanation'], str) and decoded['explanation'].strip()
        assert r['acks'] == ['ACK ' + e['event_id'] for e in events[:49]]
        if arm == 'off':
            assert len(finals) == 50
            assert [s.strip() for s in finals[:49]] == r['acks']
        history = root / arm / 'history.jsonl'
        assert digest(history) == r['history_sha256']
        records = [json.loads(line) for line in history.open()]
        assert [x['event'] for x in records] == events[:49]
        assert [x['answer'] for x in records] == r['acks']
        store = pilot.original.Store(root / arm / '.helix/workflow')
        flow = pilot.original.PassiveWorkflow(
            pilot.original.CompletionLedger(pilot.original.Memory(store)),
            'W50', digest(root / 'fixture.json'))
        assert [json.loads(x) for x in flow.exact_events(r['ledger_head'])] == events[:49]
        delivery = read(root / (arm + '-delivery.json'))
        assert delivery['snapshot'] == r['ledger_head']
        assert len(delivery['deliveries']) == 49
        assert len({d['delivery_id'] for d in delivery['deliveries']}) == 49
        memories = [read(root / (arm + '-' + phase + '-memory') / 'receipt.json')
                    for phase in ('initial', 'final')]
        assert all(m['state'] == 'completed' and m['exit_code'] == 0 for m in memories)
        assert all(not m['scoped_memories'] for m in memories)
        rows.append({
            'arm': arm, 'checks': 'PASS', 'native_sha256': digest(native),
            'raw_sha256': digest(raw), 'answer_sha256': hashlib.sha256(answer.encode()).hexdigest(),
            'history_sha256': digest(history), 'ledger_head': r['ledger_head'],
            'usage': r['usage'], 'uncached_input_tokens': r['usage']['input_tokens'] - r['usage']['cached_input_tokens'],
            'model_turns': len(turns), 'segments': len(segments), 'segment_usage': segments,
            'completed_item_types': dict(collections.Counter(x['type'] for x in items)),
            'model_tool_calls': status['raw_capture']['calls'],
            'ack_count': len(r['acks']), 'exact_restart_recovery': 'PASS',
            'delivery_scope': delivery['delivery_status'],
            'complete_model_final_unchanged': 'PASS', 'mechanical_final_grade': 'PASS',
            'engine_object_io': r['engine_object_io'], 'history_io': r['history_io'],
            'raw_capture_io': {k: v for k, v in status['raw_capture'].items() if k.startswith('logical_capture_')},
            'post_run_audit_object_io_separate': dict(store.metrics),
            'arm_elapsed_seconds': r['elapsed_seconds'], 'preparation_seconds': r['preparation_seconds'],
            'native_session_elapsed_seconds': status['elapsed_seconds'],
            'memory_recall_seconds': sum(m['elapsed_seconds'] for m in memories),
            'memory_recall_raw_bytes': sum(m['raw_bytes'] for m in memories),
            'memory_scope': 'No matched prior task memories injected; out-of-scope recall retained cold',
        })
    by = {r['arm']: r for r in rows}; off = by['off']; on = by['on']
    assert off['history_sha256'] == on['history_sha256']
    assert off['ledger_head'] == on['ledger_head']
    savings = {k: 100 * (1 - on['usage'][k] / off['usage'][k])
               if off['usage'][k] else None for k in KEYS}
    savings['uncached_input_tokens'] = 100 * (1 - on['uncached_input_tokens'] / off['uncached_input_tokens'])
    return {'classification': 'Finite known W50 task; complete model final. Not coding/general parity or Codex-app deployment.',
            'manifest_sha256': digest(root / 'manifest.json'), 'bindings_verified': len(manifest['bindings']),
            'model': manifest['model'], 'effort': manifest['effort'], 'rows': rows,
            'savings_percent': savings, 'same_history_and_ledger_root': True,
            'manifest_preparation_seconds': manifest['preparation_seconds'],
            'full_physical_io_and_total_project_cost': 'UNMEASURED',
            'semantic_review': 'Separate explicit review required; hashes do not establish semantic adequacy',
            'release_qualified': False}


if __name__ == '__main__':
    output = audit(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'mechanical_audit': 'PASS', 'savings_percent': output['savings_percent']}))
