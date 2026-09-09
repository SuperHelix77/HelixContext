"""Reconcile terminal native receipts; semantic assessment is a separate review."""
import json
import sys
from pathlib import Path
import native_kernel_pair as driver


def audit(root, out):
    root = Path(root); m = json.loads((root/'kernel-manifest.json').read_text())
    result = json.loads((root/'amended-results.json').read_text())
    assert result['state'] == 'AWAITING_INDEPENDENT_AUDIT'
    assert len(result['rows']) == 4
    rows = []
    for variant, arm in m['order']:
        driver.bindings(root, m, variant)
        p = root/f'{variant}-{arm}-run'
        s = json.loads((p/'status.json').read_text())
        assert s['state'] == 'closed' and len(s['turns']) == 1
        assert driver.sha(p/'native-events.jsonl') == s['native_events_sha256']
        assert driver.sha(p/'events.jsonl') == s['events_sha256']
        events = [json.loads(l) for l in (p/'native-events.jsonl').read_text().splitlines()]
        updates = [e for e in events if e.get('method') == 'thread/tokenUsage/updated']
        assert all(e['params']['threadId'] == s['thread_id'] for e in updates)
        assert driver.research_session.usage(updates[-1]) == s['usage']
        for key, native in [('input_tokens', 'inputTokens'), ('output_tokens', 'outputTokens'),
                            ('cached_input_tokens', 'cachedInputTokens'), ('reasoning_output_tokens', 'reasoningOutputTokens')]:
            assert sum(e['params']['tokenUsage']['last'][native] for e in updates) == s['usage'][key]
        reqs = [json.loads(l) for l in (p/'requests.jsonl').read_text().splitlines()]
        starts = [e['params'] for e in reqs if e.get('method') == 'thread/start']
        assert len(starts) == 1
        assert starts[0]['config'].get('model_instructions_file') == (m['kernel'] if arm == 'kernel' else None)
        assert 'baseInstructions' not in starts[0]
        turn = json.loads((p/'turn-1-input.json').read_text())
        assert turn['effort'] == 'high' and turn['model'] == m['model']
        assert turn['input'][0]['text'] == (root/variant/'prompt.txt').read_text()
        assert turn['input'][1]['type'] == 'skill'
        commands = [e['params']['item'] for e in events if e.get('method') == 'item/completed'
                    and e['params']['item'].get('type') == 'commandExecution']
        answer = (p/'turn-1-answer.txt').read_text()
        row = next(r for r in result['rows'] if (r['variant'], r['arm']) == (variant, arm))
        assert answer == row['answer'] and s['usage'] == row['usage']
        rows.append({'variant': variant, 'arm': arm, 'usage': s['usage'],
                     'segments': len(updates), 'recorded_commands': len(commands),
                     'native_sha256': s['native_events_sha256'],
                     'command_hashes': [driver.research_session.sha(c['command'].encode()) for c in commands],
                     'semantic_review': 'PENDING'})
        driver.save(root/f'{variant}-{arm}-hud.json', {**s, 'state': 'completed',
            'runner': 'app-server', 'source_status_sha256': driver.sha(p/'status.json')})
    pairs = []
    for variant in ('defect', 'valid'):
        control = next(r for r in rows if r['variant'] == variant and r['arm'] == 'default')['usage']
        candidate = next(r for r in rows if r['variant'] == variant and r['arm'] == 'kernel')['usage']
        savings = {k: 100*(1-candidate[k]/control[k]) for k in ('input_tokens', 'output_tokens')}
        savings['uncached_input'] = 100*(1-(candidate['input_tokens']-candidate['cached_input_tokens'])/
                                       (control['input_tokens']-control['cached_input_tokens']))
        pairs.append({'variant': variant, 'savings_percent': savings})
    data = {'status': 'NATIVE_ACCOUNTING_VERIFIED_SEMANTICS_PENDING', 'rows': rows, 'pairs': pairs,
            'manifest_sha256': driver.sha(root/'kernel-manifest.json'),
            'amendment_sha256': driver.sha(root/'amendment.json'),
            'limits': ['Known development fixtures; no general parity claim.',
                      'Post-first-outcome harness schema amendment; no repeated model call.',
                      'Same cwd and counterbalanced order require artifact/cache audit.',
                      'Proxy text savings are not native or monetary savings.']}
    driver.save(Path(out), data)
    print(json.dumps({'rows': rows, 'pairs': pairs}, indent=2))


if __name__ == '__main__':
    audit(*sys.argv[1:])
