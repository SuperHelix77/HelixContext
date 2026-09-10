"""Offline native-counter, source, effective-config and finite-check audit."""
import hashlib
import json
from pathlib import Path
import sys
import maintenance_release as r


def audit(root):
    root = Path(root).resolve(); m = json.loads((root / 'manifest.json').read_text()); r.configure(m['model'], m['effort']); r.verify(m)
    results = json.loads((root / 'results.json').read_text())
    assert results['state'] == 'AWAITING_AUDIT' and results['manifest_sha256'] == r.sha(root / 'manifest.json')
    assert [x['arm'] for x in results['rows']] == m['order']
    rows = []; identities = set()
    for row in results['rows']:
        arm = row['arm']; cwd = root / arm; run = root / (arm + '-run')
        r.scope(cwd, m['git'][arm])
        assert r.workspace.git(cwd, 'rev-parse', m['git'][arm]['initial_commit'] + '^{tree}') == m['git'][arm]['initial_tree']
        s = json.loads((run / 'status.json').read_text()); assert s['state'] == 'closed'
        assert s['model'] == m['model'] and s['effort'] == m['effort'] and s['thread_id'] not in identities
        identities.add(s['thread_id']); assert 1 <= len(s['turns']) <= 2
        assert len(s['turns']) == len(row['turns'])
        assert r.sha(run / 'native-events.jsonl') == s['native_events_sha256']
        assert r.sha(run / 'events.jsonl') == s['events_sha256']
        events = [json.loads(x) for x in (run / 'native-events.jsonl').read_text().splitlines()]
        updates = [e for e in events if e.get('method') == 'thread/tokenUsage/updated']
        assert r.usage(updates[-1]) == s['usage'] == row['usage']
        for key, native in [('input_tokens', 'inputTokens'), ('output_tokens', 'outputTokens'),
                            ('cached_input_tokens', 'cachedInputTokens'), ('reasoning_output_tokens', 'reasoningOutputTokens')]:
            assert sum(e['params']['tokenUsage']['last'][native] for e in updates) == s['usage'][key]
            assert sum(t['usage_delta'][key] for t in s['turns']) == s['usage'][key]
        raw = (run / 'raw/raw-rollout.jsonl').read_bytes()
        idx = json.loads((run / 'raw/raw-tool-index.json').read_text())
        assert hashlib.sha256(raw).hexdigest() == idx['sha256'] == s['raw_capture']['sha256']
        for item in idx['records']:
            assert hashlib.sha256(raw[item['start']:item['end']]).hexdigest() == item['line_sha256']
        records = [json.loads(x) for x in raw.splitlines()]
        metas = [e['payload'] for e in records if e.get('type') == 'session_meta']
        assert len(metas) == 1 and metas[0]['id'] == s['thread_id']
        meta = metas[0]; base = meta['base_instructions']['text'].encode()
        if arm == 'on':
            assert base == r.BASE.read_bytes().rstrip(b'\n') and meta['base_instructions']['provenance']['type'] == 'custom'
        else: assert hashlib.sha256(base).hexdigest() == m['default_base_sha256']
        requests = [json.loads(x) for x in (run / 'requests.jsonl').read_text().splitlines()]
        starts = [x['params'] for x in requests if x.get('method') == 'thread/start']; assert len(starts) == 1
        assert starts[0]['model'] == m['model'] and starts[0]['config']['model_reasoning_effort'] == m['effort']
        turns = [x['params'] for x in requests if x.get('method') == 'turn/start']
        assert len(turns) == len(row['turns'])
        prompt = (root / (arm + '-prompt.txt')).read_text()
        texts = [x['text'] for x in turns[0]['input'] if x['type'] == 'text']
        assert len(texts) == 1 and (texts[0].endswith(prompt) if arm == 'on' else texts[0] == prompt)
        assert all(x['model'] == m['model'] and x['effort'] == m['effort'] for x in turns)
        skills = [x for x in turns[0]['input'] if x['type'] == 'skill']
        assert len(skills) == (1 if arm == 'on' else 0)
        if skills: assert skills[0]['path'] == str(cwd / '.agents/skills/helixcontext/SKILL.md')
        binding = s['effective_config_binding']
        assert binding['native_overrides_verified'] and binding['other_parsed_settings_unchanged']
        assert binding['model'] == m['model'] and binding['effort'] == m['effort']
        assert r.sha(run / 'config.initial.private.toml') == binding['initial_sha256']
        assert r.sha(run / 'config.final.private.toml') == binding['final_sha256']
        r.native.validate(Path(m['config_snapshot']).read_bytes(), (run / 'config.initial.private.toml').read_bytes())
        for i, attempt in enumerate(row['turns'], 1):
            assert (run / f'turn-{i}-answer.txt').read_text() == attempt['answer']
            assert attempt['native'] == s['turns'][i-1]
            completion = attempt.get('completion', {})
            for check in completion.get('rows', []):
                folder = root / f'{arm}-check-{i}'
                for kind in ('stdout', 'stderr'):
                    assert r.sha(folder / (check['check'] + '.' + kind)) == check[kind + '_sha256']
        if arm == 'on' and row['checks'] == 'PASS':
            store = r.Store(root / (arm + '-store'))
            before = dict(store.metrics)
            text, plan, error = r.proposal(row['turns'][-1]['answer'],
                                         (r.INPUT / 'baseline' / r.TARGET).read_bytes(), m['inputs'][r.TARGET])
            assert error is None
            exact, _ = r.renderer.assemble(store, plan)
            assert exact == (cwd / r.TARGET).read_bytes()
            reconstruction_io = {k: store.metrics[k]-before[k] for k in before}
        else: reconstruction_io = None
        assert r.sha(cwd / r.TARGET) == row['source_sha256']
        recheck = r.grade(cwd, root / (arm + '-audit-check'))
        assert recheck['checks'] == row['checks']
        mem = json.loads((root / (arm + '-memory') / 'receipt.json').read_text())
        rows.append({'arm': arm, 'model': m['model'], 'effort': m['effort'], 'thread_id': s['thread_id'],
                     'usage': row['usage'], 'segments': len(updates), 'turns': len(s['turns']),
                     'raw_tool_calls': idx['calls'], 'raw_sha256': idx['sha256'], 'raw_bytes': len(raw),
                     'native_sha256': s['native_events_sha256'], 'source_sha256': row['source_sha256'],
                     'checks': row['checks'], 'elapsed_seconds': row['elapsed_seconds'],
                     'caller_check_seconds': sum(t.get('completion', {}).get('seconds', 0) for t in row['turns']),
                     'store_io': row['store_io'], 'post_audit_reconstruction_io': reconstruction_io,
                     'post_audit_check_seconds': recheck['seconds'], 'memory_seconds': mem['elapsed_seconds'],
                     'memory_raw_bytes': mem['raw_bytes'], 'prompt_bytes': len(texts[0].encode()),
                     'base_bytes': len(base), 'config_binding': binding})
    off = next(x for x in rows if x['arm'] == 'off'); on = next(x for x in rows if x['arm'] == 'on')
    savings = {k: 100*(1-on['usage'][k]/off['usage'][k]) for k in ('input_tokens', 'output_tokens')}
    savings['uncached_input_tokens'] = 100*(1-(on['usage']['input_tokens']-on['usage']['cached_input_tokens']) /
                                           (off['usage']['input_tokens']-off['usage']['cached_input_tokens']))
    passed = all(x['checks'] == 'PASS' for x in rows)
    report = {'classification': m['classification'], 'N': 1, 'manifest_sha256': r.sha(root / 'manifest.json'),
              'rows': rows, 'savings_percent': savings, 'finite_checks': 'PASS' if passed else 'FAIL',
              'meets_75_75': passed and min(savings['input_tokens'], savings['output_tokens']) >= 75,
              'meets_80_80': passed and min(savings['input_tokens'], savings['output_tokens']) >= 80,
              'preparation_seconds': m['preparation_seconds'], 'general_release': False, 'reused_controls': False,
              'normal_codex_app_integration': False, 'model': m['model'], 'effort': m['effort'],
              'release_threshold': 65 if m['model']=='gpt-6-astra' else 75,
              'meets_requested_economic_gate': passed and min(savings['input_tokens'],savings['output_tokens']) >= (65 if m['model']=='gpt-6-astra' else 75),
              'native_usage_all_attempts': {k: sum(x['usage'][k] for x in rows) for k in off['usage']},
              'limits': ['Composite kernel/skill/caller-edits test; no individual mechanism attribution',
                         'One known development maintenance task; not population parity or prior coding qualification',
                         'Setup, caller checks, storage and private evidence capture cost nonzero',
                         'Execution is a research caller; production delivery and hostile-host atomicity unproven']}
    r.save(root / 'audit.json', report); r.save(r.HERE / (('ASTRA_XHIGH' if m['effort']=='xhigh' else 'SOL_HIGH') + '_RESULT.json'), report)
    print(json.dumps({'savings_percent': savings, 'finite_checks': report['finite_checks'],
                      'meets_75_75': report['meets_75_75'], 'meets_80_80': report['meets_80_80']}))


if __name__ == '__main__': audit(sys.argv[1])
