"""Native evidence accounting; semantic judgments require separate human review."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path[:0] = [str(HERE), str(REPO / 'engine/hud')]
import pilot
import pricing


def sha(raw): return hashlib.sha256(raw).hexdigest()
def save(path, value): path.write_text(json.dumps(value, indent=2) + '\n')


def audit(root):
    root = Path(root).resolve()
    manifest_raw = (root / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_raw)
    pilot.verify(manifest)
    results = json.loads((root / 'results.json').read_text())
    assert results['state'] == 'AWAITING_AUDIT' and len(results['rows']) == 4
    assert results['manifest_sha256'] == sha(manifest_raw)
    out = HERE / 'artifacts'; out.mkdir(exist_ok=False)
    rows = []; thread_ids = set()
    keys = {'input_tokens':'inputTokens', 'output_tokens':'outputTokens',
            'cached_input_tokens':'cachedInputTokens', 'reasoning_output_tokens':'reasoningOutputTokens',
            'cache_write_input_tokens':'cacheWriteInputTokens'}
    for row in results['rows']:
        folder = root / (row['case'] + '-' + row['arm']); native = folder / 'native'
        status = json.loads((native / 'status.json').read_text())
        assert status['state'] == 'closed'
        assert status['model'] == 'gpt-6-astra' and status['effort'] == 'xhigh'
        assert status['thread_id'] not in thread_ids; thread_ids.add(status['thread_id'])
        assert status['effective_config_binding']['native_overrides_verified']
        assert status['effective_config_binding']['changed_top_level_keys'] == []
        raw = (native / 'raw/raw-rollout.jsonl').read_bytes()
        assert sha(raw) == status['raw_capture']['sha256']
        assert status['raw_capture']['unmatched_calls'] == status['raw_capture']['orphan_outputs'] == []
        events_raw = (native / 'native-events.jsonl').read_bytes()
        assert sha(events_raw) == status['native_events_sha256']
        events = [json.loads(x) for x in events_raw.splitlines()]
        updates = [x for x in events if x.get('method') == 'thread/tokenUsage/updated']
        assert {x['params']['threadId'] for x in updates} == {status['thread_id']}
        for key, field in keys.items():
            assert sum(e['params']['tokenUsage']['last'][field] for e in updates) == row['usage'][key]
            assert updates[-1]['params']['tokenUsage']['total'][field] == row['usage'][key]
        assert status['usage'] == row['usage']
        requests = [json.loads(x) for x in (native / 'requests.jsonl').read_text().splitlines()]
        starts = [x['params'] for x in requests if x.get('method') == 'thread/start']
        assert len(starts) == 1 and 'model_instructions_file' not in starts[0].get('config', {})
        turns = [x['params'] for x in requests if x.get('method') == 'turn/start']
        assert len(turns) == 1 and turns[0]['effort'] == 'xhigh'
        answers = [(n, e['params']['item']) for n, e in enumerate(events)
                   if e.get('method') == 'item/completed'
                   and e.get('params', {}).get('item', {}).get('type') == 'agentMessage'
                   and e['params']['item'].get('phase') == 'final_answer']
        assert len(answers) == 1 and answers[0][1]['text'] == row['answer']
        assert (native / 'turn-1-answer.txt').read_text() == row['answer']
        commands = []
        for n, e in enumerate(events):
            item = e.get('params', {}).get('item', {})
            if e.get('method') == 'item/completed' and item.get('type') == 'commandExecution':
                assert n < answers[0][0]
                raw_out = item.get('aggregatedOutput') or ''
                commands.append({'event_index':n, 'command':item['command'], 'exit_status':item['exitCode'],
                                 'output_bytes':len(raw_out.encode()), 'output_sha256':sha(raw_out.encode())})
        # Exact task/skill paths remain bound. New diagnostic files are retained.
        before = json.loads((folder / 'protected.json').read_text())
        for name, digest in before.items(): assert sha((folder / 'work' / name).read_bytes()) == digest
        destination = out / (row['case'] + '-' + row['arm']); destination.mkdir()
        (destination / 'final-answer.md').write_text(row['answer'])
        save(destination / 'commands.json', commands)
        save(destination / 'usage.json', [e['params']['tokenUsage']['last'] for e in updates])
        preflight = json.loads((folder / 'preflight/receipt.json').read_text()) if row['arm'] == 'on' else None
        memory = json.loads((folder / 'memory/receipt.json').read_text())
        rows.append({'case':row['case'], 'arm':row['arm'], 'model':status['model'], 'effort':status['effort'],
                     'thread_id':status['thread_id'], 'usage':row['usage'], 'segments':len(updates),
                     'shell_commands':len(commands), 'nonzero_command_exits':sum(c['exit_status'] != 0 for c in commands),
                     'tool_return_bytes':sum(c['output_bytes'] for c in commands),
                     'source_sha256':row['source_sha256'], 'answer_sha256':sha(row['answer'].encode()),
                     'native_events_sha256':sha(events_raw), 'raw_sha256':sha(raw), 'raw_bytes':len(raw),
                     'elapsed_seconds':row['elapsed_seconds'],
                     'caller_check_seconds':sum(x['seconds'] for x in preflight['checks']) if preflight else 0,
                     'caller_check_commands':len(preflight['checks']) if preflight else 0,
                     'memory_seconds':memory['elapsed_seconds'], 'memory_raw_bytes':memory['raw_bytes'],
                     'model_authored_final_after_actual_evidence':True,
                     'unchanged_base_effort_config_and_protected_source':True,
                     'semantic_verdict':'PENDING_EXPLICIT_REVIEW'})
    raw = pricing.fetch(); (out / 'pricing-source.md').write_bytes(raw)
    rates = pricing.parse(raw)['gpt-6-astra']
    pairs = []
    for case in ('sample_a', 'sample_b'):
        arms = {r['arm']: r for r in rows if r['case'] == case}
        savings = {}
        for key in ('input_tokens', 'output_tokens', 'uncached_input_tokens'):
            def count(r):
                u = r['usage']
                return u['input_tokens'] - u['cached_input_tokens'] if key == 'uncached_input_tokens' else u[key]
            savings[key] = 100 * (1 - count(arms['on']) / count(arms['off']))
        costs = {arm: pricing.estimate(r['usage'], rates) for arm, r in arms.items()}
        cost_savings = {tier:100 * (1 - costs['on'][tier] / costs['off'][tier]) for tier in ('short','long')}
        pairs.append({'case':case, 'savings_percent':savings, 'dated_api_equivalent_cost':costs,
                      'dated_api_equivalent_saving_percent':cost_savings})
    report = {'classification':'Fresh paired exposed review diagnostic, original base; not release cohort or universal parity',
              'manifest_sha256':sha(manifest_raw), 'rows':rows, 'pairs':pairs,
              'median_savings_percent':{k:statistics.median(p['savings_percent'][k] for p in pairs)
                                        for k in pairs[0]['savings_percent']},
              'median_api_equivalent_savings_percent':{k:statistics.median(p['dated_api_equivalent_saving_percent'][k] for p in pairs)
                                                      for k in ('short','long')},
              'native_usage_all_attempts':{k:sum(r['usage'][k] for r in rows) for k in keys},
              'preparation_seconds':manifest['preparation_seconds'],
              'pricing':{'source':pricing.SOURCE, 'source_sha256':sha(raw), 'rates':rates,
                         'checked_at':datetime.now(timezone.utc).isoformat(), 'not_codex_quota_or_total_roi':True},
              'release_qualification':False, 'semantic_review':'PENDING', 'self_deployment':False,
              'complete_physical_io_cost':None, 'included_quota_saving':None,
              'limits':['Control is Engine ordinary execution with the same installed Helix skill, not pristine native.',
                        'Exposed development review cases, not the seven-task release cohort.',
                        'No shortened base, imposed output shape, effort reduction or inferred hidden reasoning.',
                        'Native usage includes failed commands and all model segments; Engine and audit costs are additional.']}
    save(root / 'audit.json', report); save(HERE / 'RESULT.json', report)
    files = {str(p.relative_to(out)):sha(p.read_bytes()) for p in out.rglob('*') if p.is_file()}
    save(out / 'MANIFEST.json', {'report_sha256':sha((HERE / 'RESULT.json').read_bytes()), 'files':files})
    print(json.dumps({'median_savings_percent':report['median_savings_percent'],
                      'median_api_equivalent_savings_percent':report['median_api_equivalent_savings_percent'],
                      'all_attempts':report['native_usage_all_attempts']}))


if __name__ == '__main__': audit(sys.argv[1])
