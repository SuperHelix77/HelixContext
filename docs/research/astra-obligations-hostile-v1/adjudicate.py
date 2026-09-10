"""Audit completed candidate facts. Semantic acceptance requires explicit review.

Retain raw native evidence privately. Publish only ordinary final text, tool
operations, counters and exact evidence bindings; never private reasoning text.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[2] / 'engine/hud')]
import pilot
import pricing


def digest(raw): return hashlib.sha256(raw).hexdigest()
def save(p, value): p.write_text(json.dumps(value, indent=2) + '\n')


def audit(root):
    root = Path(root).resolve(); manifest = pilot.admitted(root)
    result = json.loads((root / 'result.json').read_text()); native = root / 'native'
    assert result['state'] == 'AWAITING_SEMANTIC_AUDIT'
    assert result['manifest_sha256'] == pilot.sha(root / 'manifest.json')
    status = json.loads((native / 'status.json').read_text())
    assert status['state'] == 'closed' and status['model'] == pilot.MODEL and status['effort'] == pilot.EFFORT
    assert status['effective_config_binding']['native_overrides_verified']
    assert status['effective_config_binding']['changed_top_level_keys'] == []
    raw = (native / 'raw/raw-rollout.jsonl').read_bytes()
    assert digest(raw) == status['raw_capture']['sha256']
    assert status['raw_capture']['unmatched_calls'] == status['raw_capture']['orphan_outputs'] == []
    events_raw = (native / 'native-events.jsonl').read_bytes()
    assert digest(events_raw) == status['native_events_sha256']
    events = [json.loads(line) for line in events_raw.splitlines()]
    updates = [e for e in events if e.get('method') == 'thread/tokenUsage/updated']
    assert {e['params']['threadId'] for e in updates} == {status['thread_id']}
    usage = result['usage']; assert usage == status['usage']
    keys = {'input_tokens':'inputTokens', 'output_tokens':'outputTokens',
            'cached_input_tokens':'cachedInputTokens', 'reasoning_output_tokens':'reasoningOutputTokens',
            'cache_write_input_tokens':'cacheWriteInputTokens'}
    for k, field in keys.items():
        assert sum(e['params']['tokenUsage']['last'][field] for e in updates) == usage[k]
        assert updates[-1]['params']['tokenUsage']['total'][field] == usage[k]
    requests = [json.loads(line) for line in (native / 'requests.jsonl').read_text().splitlines()]
    starts = [e['params'] for e in requests if e.get('method') == 'thread/start']
    turns = [e['params'] for e in requests if e.get('method') == 'turn/start']
    assert len(starts) == len(turns) == 1
    assert 'model_instructions_file' not in starts[0].get('config', {})
    assert turns[0]['model'] == pilot.MODEL and turns[0]['effort'] == pilot.EFFORT
    expected = (root / 'prompt.txt').read_text()
    prompt = turns[0]['input'][0]['text']; assert prompt.endswith(expected)
    assert turns[0]['input'][1] == {'type':'skill','name':'helixcontext',
        'path':str(root / 'work/.agents/skills/helixcontext/SKILL.md')}
    answers = [(i, e['params']['item']) for i,e in enumerate(events)
        if e.get('method') == 'item/completed' and e.get('params',{}).get('item',{}).get('type') == 'agentMessage'
        and e['params']['item'].get('phase') == 'final_answer']
    assert len(answers) == 1 and answers[0][1]['text'] == result['answer']
    assert (native / 'turn-1-answer.txt').read_text() == result['answer']
    commands = []; messages = []
    for i,e in enumerate(events):
        item = e.get('params',{}).get('item',{})
        if e.get('method') != 'item/completed': continue
        if item.get('type') == 'commandExecution':
            assert i < answers[0][0]
            text = item.get('aggregatedOutput') or ''
            commands.append({'event_index':i,'command':item['command'],'exit_status':item['exitCode'],
                'output':text,'output_bytes':len(text.encode()),'output_sha256':digest(text.encode())})
        if item.get('type') == 'agentMessage':
            messages.append({'event_index':i,'phase':item.get('phase'),'text':item['text']})
    now = pilot.old.protected(root / 'work')
    assert all(now.get(k) == v for k,v in manifest['protected'].items())
    c = json.loads((root / 'comparisons/receipt.json').read_text())
    assert pilot.sha(Path(c['outcomes']['path'])) == c['outcomes']['sha256']
    outcomes = json.loads(Path(c['outcomes']['path']).read_text())
    assert len(outcomes) == 612 and all(x['relation_holds'] and x['tables_unchanged'] for x in outcomes)
    out = HERE / 'artifacts'; out.mkdir(exist_ok=False)
    (out / 'final-answer.md').write_text(result['answer'])
    save(out / 'commands.json', commands); save(out / 'visible-messages.json', messages)
    segments = [e['params']['tokenUsage']['last'] for e in updates]; save(out / 'usage.json', segments)
    raw_price = pricing.fetch(); (out / 'pricing-source.md').write_bytes(raw_price)
    rates = pricing.parse(raw_price)[pilot.MODEL]
    price = {'checked_at':datetime.now(timezone.utc).isoformat(),'source':pricing.SOURCE,
             'source_sha256':digest(raw_price),'rates':rates,
             'api_equivalent':pricing.estimate(usage,rates),
             'scope':'Dated API tariff scenarios only; not included-plan quota, bill or total ROI'}
    save(HERE / 'PRICING.json', price)
    m = json.loads((root / 'memory/receipt.json').read_text())
    reg = json.loads((root / 'regressions/receipt.json').read_text())
    report = {'state':'NATIVE_FACTS_VERIFIED_SEMANTIC_REVIEW_PENDING',
        'classification':'One exposed candidate-only diagnostic; no paired denominator or release cohort',
        'manifest_sha256':pilot.sha(root / 'manifest.json'),'model':pilot.MODEL,'effort':pilot.EFFORT,
        'thread_id':status['thread_id'],'usage':usage,'segments':len(segments),'user_turns':1,
        'uncached_input_tokens':usage['input_tokens']-usage['cached_input_tokens'],
        'shell_commands':len(commands),'nonzero_command_exits':sum(c['exit_status']!=0 for c in commands),
        'returned_command_bytes':sum(c['output_bytes'] for c in commands),
        'native_seconds':status['elapsed_seconds'],'preparation_seconds':manifest['preparation_seconds'],
        'prompt_bytes':manifest['prompt_bytes'],'caller_registration_prefix_bytes':len(prompt.encode())-len(expected.encode()),
        'comparison_seconds':c['seconds'],'comparison_store_io':c['store_io'],
        'comparison_raw_bytes':c['outcomes']['bytes'],'memory_seconds':m['elapsed_seconds'],
        'memory_raw_bytes':m['raw_bytes'],'regression_seconds':sum(c['seconds'] for c in reg['checks']),
        'raw_capture_bytes':len(raw),'raw_capture_sha256':digest(raw),'native_sha256':digest(events_raw),
        'final_sha256':digest(result['answer'].encode()),'final_bytes':len(result['answer'].encode()),
        'request_sha256':pilot.sha(native / 'turn-1-input.json'),'native_raw_tool_calls':status['raw_capture']['calls'],
        'config_unchanged':True,'protected_source_unchanged':True,'model_written_final_unchanged':True,
        'extra_files':result['extra_files'],'saving_percent':None,'api_equivalent':price['api_equivalent'],
        'physical_io_bytes':None,'research_coordinator_cost':'Additional, not included in candidate native usage'}
    save(HERE / 'AUDIT.json', report)
    print(json.dumps(report,indent=2))


if __name__ == '__main__': audit(sys.argv[1])
