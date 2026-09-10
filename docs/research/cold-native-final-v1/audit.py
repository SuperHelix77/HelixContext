"""Finite task/counter/final audit. Only visible operations and usage are inspected."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('cold_audit_pilot', HERE / 'pilot.py')
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
KEYS = {'input_tokens': 'inputTokens', 'output_tokens': 'outputTokens',
        'cached_input_tokens': 'cachedInputTokens', 'reasoning_output_tokens': 'reasoningOutputTokens',
        'cache_write_input_tokens': 'cacheWriteInputTokens'}


def audit(root, out):
    root = Path(root).resolve(); out = Path(out).resolve(); out.mkdir(parents=True, exist_ok=False)
    m = p.admitted(root); result = p.read(root / 'results.json')
    assert result['state'] == 'AWAITING_AUDIT' and len(result['rows']) == 2
    assert result['manifest_sha256'] == p.sha(root / 'manifest.json')
    oracle = p.fixture.expected('cold', p.read(root / 'fixture.json'))
    assert p.fixture.equal(oracle, p.read(root / 'expected.private.json'))
    rows = []
    for r in result['rows']:
        arm = r['arm']; run = root / (arm + '-run'); status = p.read(run / 'status.json')
        assert status['state'] == 'closed' and status['error'] is None
        assert status['model'] == m['model'] and status['effort'] == m['effort']
        assert status['usage'] == r['usage'] and len(status['turns']) == 1
        assert status['turns'][0]['state'] == 'completed'
        assert status['effective_config_binding']['other_parsed_settings_unchanged']
        assert status['effective_config_binding']['native_overrides_verified']
        assert status['config_sha256'] == p.sha(p.old.CONFIG)
        assert status['registration']['skill_sha256'] == p.sha(p.old.SKILL)
        raw = run / 'raw/raw-rollout.jsonl'; native = run / 'native-events.jsonl'
        assert status['native_events_sha256'] == p.sha(native)
        assert status['raw_capture']['sha256'] == p.sha(raw)
        assert status['events_sha256'] == p.sha(run / 'events.jsonl')
        xs = [json.loads(l) for l in native.open()]
        usage = [x['params']['tokenUsage'] for x in xs if x.get('method') == 'thread/tokenUsage/updated']
        segments = []; previous = {k: 0 for k in KEYS}
        for u in usage:
            total = {k: u['total'].get(v, 0) for k, v in KEYS.items()}
            if total == previous: continue
            delta = {k: total[k] - previous[k] for k in KEYS}
            assert all(n >= 0 for n in delta.values())
            assert delta['cached_input_tokens'] <= delta['input_tokens']
            assert delta['reasoning_output_tokens'] <= delta['output_tokens']
            segments.append(delta); previous = total
        assert previous == r['usage'] == status['turns'][0]['usage_delta']
        items = [x['params']['item'] for x in xs if x.get('method') == 'item/completed']
        finals = [x for x in items if x.get('type') == 'agentMessage' and x.get('phase') == 'final_answer']
        assert len(finals) == 1
        answer = (run / 'turn-1-answer.txt').read_text()
        assert answer == finals[0]['text'] == r['answer']
        p.grade(answer, oracle)
        current = p.old.protected(root / arm)
        assert all(current.get(k) == v for k, v in m['protected'][arm].items())
        assert p.sha(root / arm / 'history.json') == m['source_sha256']
        # Project only visible messages and command observations, never reasoning items.
        visible = [x for x in items if x.get('type') in ('agentMessage', 'commandExecution')]
        p.save(out / (arm + '-visible.json'), visible)
        (out / (arm + '-final.txt')).write_bytes((run / 'turn-1-answer.txt').read_bytes())
        raw_usage = []
        for line in raw.open():
            event = json.loads(line)
            payload = event.get('payload', {})
            if event.get('type') == 'event_msg' and payload.get('type') == 'token_count' and payload.get('info'):
                raw_usage.append(payload['info']['total_token_usage'])
        assert raw_usage and all(raw_usage[-1].get(k, 0) == r['usage'][k] for k in KEYS)
        commands = [x for x in items if x.get('type') == 'commandExecution']
        memory = p.read(root / (arm + '-memory/receipt.json'))
        rows.append({'arm': arm, 'checks': 'PASS', 'native_sha256': p.sha(native), 'raw_sha256': p.sha(raw),
            'final_sha256': p.sha(run / 'turn-1-answer.txt'), 'final_bytes': len(answer.encode()),
            'usage': r['usage'], 'uncached_input_tokens': r['usage']['input_tokens']-r['usage']['cached_input_tokens'],
            'model_turns': 1, 'segments': len(segments), 'segment_usage': segments,
            'command_count': len(commands), 'raw_tool_calls': status['raw_capture']['calls'],
            'completed_item_types': dict(collections.Counter(x['type'] for x in items)),
            'tool_return_utf8_bytes': sum(len((x.get('aggregatedOutput') or '').encode()) for x in commands),
            'native_elapsed_seconds': status['elapsed_seconds'], 'complete_native_final_unchanged': True,
            'source_unchanged': True, 'exact_unicode_whitespace_base64_types': 'PASS',
            'memory_recall_seconds': memory['elapsed_seconds'], 'memory_recall_raw_bytes': memory['raw_bytes'],
            'model_visible_prior_task_memories': len(memory['scoped_memories']),
            'raw_capture_io': {k:v for k,v in status['raw_capture'].items() if k.startswith('logical_capture_')},
            'semantic_review': 'Visible commands and claims require separate adjudication'})
    by = {x['arm']: x for x in rows}
    saving = {k:100*(1-by['on']['usage'][k]/by['off']['usage'][k]) if by['off']['usage'][k] else None for k in KEYS}
    saving['uncached_input_tokens'] = 100*(1-by['on']['uncached_input_tokens']/by['off']['uncached_input_tokens'])
    report = {'schema':'helix.cold-full-final-audit.v1','model':m['model'],'effort':m['effort'],
              'manifest_sha256':p.sha(root/'manifest.json'),'rows':rows,'savings_percent':saving,
              'bindings_verified':len(m['bindings']),'preparation_seconds':m['preparation_seconds'],
              'preflight':p.read(root/'PREFLIGHT.json'),'recovery':p.read(root/'recovery.json'),
              'classification':'Finite exposed cold snapshot; not new independent holdout, general parity, release median or application integration',
              'release_qualified':False,'full_physical_io_and_total_project_cost':'UNKNOWN'}
    p.save(out/'AUDIT.json',report)
    sys.path.insert(0,str(p.REPO/'engine/hud')); import pricing
    raw = pricing.fetch(); rates = pricing.parse(raw)
    (out/'pricing-source.md').write_bytes(raw)
    costs = {a:pricing.estimate(by[a]['usage'], rates[m['model']]) for a in by}
    p.save(out/'PRICING.json', {'source':pricing.SOURCE,'checked_at_unix':time.time(),
        'source_sha256':hashlib.sha256(raw).hexdigest(),'rates':rates[m['model']], 'api_equivalent_scenarios':costs,
        'savings_percent':{k:100*(1-costs['on'][k]/costs['off'][k]) for k in ['short','long']},
        'scope':'Dated standard API tariff scenarios; not included Codex quota, invoice or complete cost'})
    print(json.dumps({'mechanical_audit':'PASS','savings_percent':saving,'segments':{a:by[a]['segments'] for a in by}}))


if __name__ == '__main__': audit(sys.argv[1], sys.argv[2])
