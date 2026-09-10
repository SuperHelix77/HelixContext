"""Frozen independent receipt audit for native/Engine task pairs."""
import hashlib
import json
from pathlib import Path
import sys
import luna_resolved_retrieval_pair as pair


def audit(root):
    root = Path(root).resolve()
    m = json.loads((root / 'manifest.json').read_text())
    pair.verify(root, m)
    result = json.loads((root / 'results.json').read_text())
    assert result['state'] == 'AWAITING_AUDIT' and result['manifest_sha256'] == pair.sha(root / 'manifest.json')
    assert len(result['rows']) == 4
    rows = []
    total = {'input_tokens': 0, 'output_tokens': 0, 'cached_input_tokens': 0, 'reasoning_output_tokens': 0}
    for row in result['rows']:
        case, arm = row['case'], row['arm']
        p = root / case
        spec = json.loads((p / 'source.json').read_text())
        output = p / (arm + '-answer.json')
        assert pair.sha(output) == row['answer_sha256'] and output.stat().st_size == row['answer_bytes']
        assert pair.equal(row['answer'], json.loads(output.read_text()))
        assert pair.equal(row['answer'], pair.expected(case, spec)) and row['checks'] == 'PASS'
        native = None
        counts = None
        if row['semantic_calls']:
            assert row['semantic_calls'] == 1
            run = p / (arm + '-run')
            status = json.loads((run / 'status.json').read_text())
            assert status['state'] == 'closed' and status['model'] == m['model'] and status['effort'] == 'high'
            binding = status['effective_config_binding']
            assert binding['other_parsed_settings_unchanged'] and binding['native_overrides_verified']
            assert pair.sha(run / 'config.initial.private.toml') == binding['initial_sha256']
            assert pair.sha(run / 'config.final.private.toml') == binding['final_sha256']
            assert pair.sha(run / 'native-events.jsonl') == status['native_events_sha256']
            wire = [json.loads(line) for line in (run / 'native-events.jsonl').read_text().splitlines()]
            updates = [e for e in wire if e.get('method') == 'thread/tokenUsage/updated']
            counts = pair.usage(updates[-1])
            assert counts == status['usage'] == row['usage']
            keys = [('input_tokens', 'inputTokens'), ('output_tokens', 'outputTokens'),
                    ('cached_input_tokens', 'cachedInputTokens'), ('reasoning_output_tokens', 'reasoningOutputTokens')]
            for key, native_key in keys:
                assert sum(e['params']['tokenUsage']['last'][native_key] for e in updates) == counts[key]
            raw = run / 'raw/raw-rollout.jsonl'
            index = json.loads((run / 'raw/raw-tool-index.json').read_text())
            assert pair.sha(raw) == index['sha256'] == status['raw_capture']['sha256']
            metadata = next(json.loads(line)['payload'] for line in raw.read_text().splitlines() if json.loads(line).get('type') == 'session_meta')
            base = metadata['base_instructions']['text'].encode()
            assert hashlib.sha256(base).hexdigest() == pair.workspace.v1.DEFAULT_HASH
            native = {'thread_id': status['thread_id'], 'native_sha256': status['native_events_sha256'],
                      'raw_sha256': index['sha256'], 'raw_tool_calls': index['calls'], 'segments': len(updates),
                      'status_sha256': pair.sha(run / 'status.json')}
            for key in total:
                total[key] += counts[key]
        else:
            assert arm == 'on' and not (p / (arm + '-run')).exists() and 'usage' not in row
            assert row['engine_result']['state'] == 'RESOLVED' and row['engine_result']['model_calls'] == 0
            prepared = m['preparation'][case + '/ingest']
            store = pair.Store(p / 'store')
            state = lambda: json.loads((p / 'task-state.json').read_text())
            called = []
            replay = pair.gate.dispatch(spec['task'], store, prepared['source_ref'],
                expected_state_root=prepared['state_root'], current_state=state, semantic=lambda *args: called.append(args))
            assert replay['state'] == 'RESOLVED' and not called and pair.equal(replay['answer'], row['answer'])
            assert pair.sha(p / 'on' / spec['filename']) == prepared['source_ref']['sha256']
        rows.append({'case': case, 'arm': arm, 'engine_active': row['engine_active'],
                     'semantic_workflows': row['semantic_calls'], 'native': native, 'native_usage': counts,
                     'model_tokens': counts if counts is not None else {key: 0 for key in total},
                     'counter_source': 'native receipt' if native else 'no semantic callback and no model invocation; Engine execution audit',
                     'checks': 'PASS', 'answer_sha256': row['answer_sha256'], 'answer_bytes': row['answer_bytes'],
                     'elapsed_seconds': row['elapsed_seconds'], 'engine': row.get('engine_result'),
                     'recovery_store_io': row.get('recovery_store_io')})
    pairs = []
    for case in m['cases']:
        off = next(r for r in rows if r['case'] == case and r['arm'] == 'off')
        on = next(r for r in rows if r['case'] == case and r['arm'] == 'on')
        assert off['native'] is not None
        savings = {key: 100 * (1 - on['model_tokens'][key] / off['model_tokens'][key])
                   for key in ('input_tokens', 'output_tokens')}
        pairs.append({'case': case, 'savings_percent': savings, 'checks': 'PASS',
                      'scope': 'Model-token savings on a recognized mechanically closed request; Engine/setup costs separate'})
    preflight = {k: {'memory_seconds': v['memory']['elapsed_seconds'], 'memory_raw_bytes': v['memory']['raw_bytes'],
                    'registration_seconds': v['registration']['elapsed_seconds'],
                    'registration_model_turns': v['registration']['turn_start_requests']}
                 for k, v in m['preparation'].items() if 'memory' in v}
    assert all(v['registration_model_turns'] == 0 for v in preflight.values())
    report = {'classification': m['classification'], 'model_control': m['model'], 'effort_control': m['effort'],
              'manifest_sha256': pair.sha(root / 'manifest.json'), 'result_sha256': pair.sha(root / 'results.json'),
              'auditor_sha256': pair.sha(Path(__file__)), 'rows': rows, 'pairs': pairs,
              'all_native_usage': total, 'prepare_seconds': m['prepare_seconds'], 'preflight': preflight,
              'archive': {case: m['preparation'][case + '/ingest'] for case in m['cases']},
              'N_pairs': len(pairs), 'general_model_parity': 'NOT_ESTABLISHED',
              'coding_75_75_qualification': 'STILL_FAILED', 'normal_codex_app_integration': False, 'limits': m['limits']}
    pair.save(root / 'audit.json', report)
    pair.save(pair.HERE / 'LUNA_RESOLVED_RETRIEVAL_RESULT.json', report)
    print(json.dumps({'pairs': pairs, 'all_native_usage': total}, indent=2))


if __name__ == '__main__':
    audit(sys.argv[1])
