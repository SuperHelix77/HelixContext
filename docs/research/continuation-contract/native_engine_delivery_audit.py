"""Audit the recorded offline delivery probe; never starts Codex or a command."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(root):
    root = Path(root).resolve()
    p = root / 'result.json'
    r = json.loads(p.read_text())
    assert r['state'] == 'OBSERVED_AWAITING_AUDIT'
    assert r['probe_sha256'] == sha(HERE / 'native_engine_delivery_probe.py')
    assert r['catalog_sha256'] == sha(root / 'catalog.json')
    assert r['production_config_initial_sha256'] == r['production_config_final_sha256']
    assert r['production_config_unchanged'] and not r['isolated_home_has_auth_file']
    assert r['provider_requests'] == []
    wires = []
    for name, digest in r['wire_sha256'].items():
        assert sha(root / name) == digest
        wires.extend(json.loads((root / name).read_text()))
    sent = [e['sent'] for e in wires if 'sent' in e]
    assert not any(e.get('method') in ('turn/start', 'review/start', 'thread/compact/start') for e in sent)
    calls = [e for e in sent if e.get('method') == 'thread/shellCommand']
    assert [e['params']['command'] for e in calls] == r['commands']
    assert len(calls) == 2 and all(e['params']['timeoutMs'] == 3000 for e in calls)
    assert sum(e.get('method') == 'thread/resume' for e in sent) == 1
    thread = r['start']['thread']['id']
    observations = r['observations']
    assert len(observations) == 2
    items = observations[-1]['items']['data']
    assert len(items) == 2 and items == r['items_after_restart']['data']
    turns = r['after_restart']['thread']['turns']
    assert len(turns) == 2 and len({t['id'] for t in turns}) == 2
    summarized = []
    for i, item_row in enumerate(items):
        item = item_row['item']
        turn = turns[i]
        expected_status = 'completed' if i == 0 else 'failed'
        assert item['type'] == 'commandExecution' and item['source'] == 'userShell'
        assert item['status'] == expected_status and item['exitCode'] == i
        assert item_row['turnId'] == turn['id'] == observations[i]['completed']['turn']['id']
        assert turn['status'] == 'completed' and turn['items'] == [item]
        assert observations[i]['completed']['threadId'] == thread
        output = item['aggregatedOutput'] or ''
        if i == 0:
            # Compare exact output with the literal command's quoted argument.
            expected = r['commands'][0].split("' '", 1)[1][:-1] + '\n'
            assert output == expected and output.startswith('HELIX ENGINE / ')
        else:
            assert output == ''
        summarized.append({'operation': 'attributed_ack' if i == 0 else 'intentional_failure',
                           'thread_id': thread, 'turn_id': turn['id'], 'item_id': item['id'],
                           'item_type': item['type'], 'source': item['source'],
                           'turn_status': turn['status'], 'item_status': item['status'],
                           'exit_code': item['exitCode'], 'output': output,
                           'output_sha256': hashlib.sha256(output.encode()).hexdigest(),
                           'same_exact_item_after_restart': True,
                           'native_turn_duration_ms': turn['durationMs']})
    report = {
        'classification': 'OBSERVED offline native execution history and restart; no model capability/economics evidence',
        'result_sha256': sha(p), 'wire_sha256': r['wire_sha256'],
        'probe_sha256': r['probe_sha256'], 'auditor_sha256': sha(Path(__file__)),
        'cli_sha256': r['cli_sha256'], 'catalog_sha256': r['catalog_sha256'],
        'model_turn_start_calls': 0, 'loopback_provider_requests': 0,
        'reported_model_usage': None, 'production_config_unchanged': True,
        'credential_files_copied': False, 'experiment_seconds': r['elapsed_seconds'],
        'rows': summarized,
        'checks': {'exact_ack': 'PASS', 'native_item_history': 'PASS', 'process_restart': 'PASS',
                   'failure_visible': 'PASS', 'turn_completion_not_execution_success': 'PASS'},
        'limits': ['Two fixed harmless user-authorized commands only',
                   'thread/shellCommand runs unsandboxed and requires explicit user-command authority',
                   'No automatic hook routing or idempotent delivery qualification',
                   'No normal desktop rendering verified',
                   'No provider usage counter arrived; zero requests is a loopback observation',
                   'Not a 75/75 model benchmark or a Luna production release']}
    (HERE / 'NATIVE_ENGINE_DELIVERY_RESULT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'checks': report['checks'], 'rows': summarized, 'provider_requests': 0}, indent=2))


if __name__ == '__main__':
    audit(sys.argv[1])
