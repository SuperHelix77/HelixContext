"""Reconcile the retained failed display probe offline; never starts a process."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'engine/prototype'))
from delivery_outbox import DisplayOutbox
from evidence import Store
from workflow_memory import Memory


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def initial_source(current):
    """Recover the exact pre-fix text; its recorded SHA must match before use."""
    text = current.replace("READBACK_VERSION = 'helix.codex-display-readback.v2'\n", '')
    text = text.replace('def reconcile(self, ticket, native_thread, *, native_shell=None):', 'def reconcile(self, ticket, native_thread):')
    text = text.replace("        A caller may bind an inspected native shell envelope, e.g. ('/bin/zsh',\n        '-lc'). Parse its exact argv without evaluating or rewriting the command.\n        Do not infer an envelope from the untrusted command being checked.\n", '')
    begin = text.index('        if native_shell is not None')
    end = text.index('        with self.memory.db() as db:', begin)
    text = text[:begin] + text[end:]
    text = text.replace("command_matches(item.get('command'), packet['command'])", "item.get('command') == packet['command']")
    text = text.replace('evidence = dict(schema=VERSION, readback_version=READBACK_VERSION, native_shell=native_shell,\n                            request_hash=', 'evidence = dict(schema=VERSION, request_hash=')
    return text.encode()


def audit(root):
    started = time.perf_counter(); root = Path(root).resolve()
    r = json.loads((root / 'result.json').read_text())
    assert r['state'] == 'FAILED_RETAINED' and r['error'] == 'AssertionError()'
    assert r['production_config_unchanged'] and not r['isolated_home_has_auth_file'] and not r['provider_requests']
    assert sha(root / 'catalog.json') == r['catalog_sha256']
    assert sha(HERE / 'display_outbox_probe.py') == r['source_sha256']['docs/research/continuation-contract/display_outbox_probe.py']
    wires = []
    for name, digest in r['wire_sha256'].items():
        assert sha(root / name) == digest
        wires.extend(json.loads((root / name).read_text()))
    sent = [e['sent'] for e in wires if 'sent' in e]
    assert not any(e.get('method') in ('turn/start', 'review/start', 'thread/compact/start') for e in sent)
    calls = [e for e in sent if e.get('method') == 'thread/shellCommand']
    assert len(calls) == 1 and calls[0]['params'] == {
        'threadId': r['thread_id'], 'command': r['claim']['command'], 'timeoutMs': 3000}
    assert sum(e.get('method') == 'thread/resume' for e in sent) == 1
    native = r['native_history']
    assert any(e.get('received', {}).get('result', {}).get('thread') == native for e in wires)
    assert len(native['turns']) == 1 and len(native['turns'][0]['items']) == 1
    assert native['id'] == r['thread_id'] == r['native_completion']['threadId']
    assert native['turns'][0]['id'] == r['native_completion']['turn']['id']
    source = REPO / 'engine/prototype/delivery_outbox.py'
    before = initial_source(source.read_text())
    assert hashlib.sha256(before).hexdigest() == r['source_sha256']['engine/prototype/delivery_outbox.py']
    original = Store(root / 'engine')
    packet = original.get(r['ticket']['request_hash'])
    copy_bytes = sum(p.stat().st_size for p in (root / 'engine').rglob('*') if p.is_file())
    with tempfile.TemporaryDirectory(prefix='helix-display-recovery-') as scratch:
        target = Path(scratch) / 'engine'; shutil.copytree(root / 'engine', target)
        store = Store(target); b = DisplayOutbox(Memory(store))
        args = dict(current_authority='a' * 64, explicit_user_command=True, thread_idle=True)
        assert b.claim(r['ticket'], **args) == {'state': 'RECONCILE', 'submit': False}
        delivered = b.reconcile(r['ticket'], native, native_shell=('/bin/zsh', '-lc'))
        assert delivered['state'] == 'DELIVERED'
        assert DisplayOutbox(Memory(store)).claim(r['ticket'], **args) == delivered
        assert b.reconcile(r['ticket'], native, native_shell=('/bin/zsh', '-lc')) == delivered
        receipt = json.loads(store.get(delivered['evidence']))
        metrics = dict(store.metrics)
    out = HERE / 'display-outbox-artifacts'; out.mkdir(exist_ok=True)
    (out / 'before_delivery_outbox.py').write_bytes(before)
    (out / 'request.json').write_bytes(packet)
    (out / 'native-readback.json').write_text(json.dumps({'id': native['id'], 'turns': native['turns']}, indent=2) + '\n')
    (out / 'reconciled-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    report = {'classification': 'OBSERVED real native delivery/process restart plus offline recovery; not model performance or automatic app integration',
              'initial_trial': 'FAILED_RETAINED: exact readback rejected the unbound native shell wrapper',
              'initial_result_sha256': sha(root / 'result.json'), 'initial_seconds': r['elapsed_seconds'],
              'initial_object_io': r['object_io'], 'native_shell_submissions': 1, 'native_turn_start_calls': 0,
              'loopback_provider_requests': 0, 'reported_model_tokens': None,
              'original_artifacts_mutated': False, 'additional_native_submissions_for_recovery': 0,
              'native_cli_sha256': r['cli_sha256'], 'native_wire_sha256': r['wire_sha256'],
              'readback_shell_binding': ['/bin/zsh', '-lc'], 'delivery': delivered,
              'recovery_object_io': metrics, 'recovery_copy_logical_bytes': copy_bytes,
              'recovery_seconds': time.perf_counter()-started,
              'checks': {'one_native_command': 'PASS', 'lost_local_ack_no_resubmit': 'PASS', 'process_restart': 'PASS',
                         'exact_native_readback': 'PASS', 'duplicate_after_recovery_no_resubmit': 'PASS',
                         'zero_model_requests': 'PASS', 'production_config_unchanged': 'PASS'},
              'source_after_sha256': sha(source), 'source_before_sha256': hashlib.sha256(before).hexdigest(),
              'auditor_sha256': sha(Path(__file__)),
              'artifacts': {p.name: sha(p) for p in out.iterdir() if p.is_file()},
              'limits': ['Lost local acknowledgement simulated after the real command completed; server process actually restarted.',
                         'The initial failed trial is retained; recovery used a cloned store and no live app-server.',
                         'SQLite outbox integrity and truthful caller permission/current-state assertions are assumed; no hostile-host or rollback guarantee.',
                         'Missing ambiguous native delivery is not automatically retried; an idempotent target or explicit reconciliation is required.',
                         'Idle and authority preflight are not an atomic desktop submission lock.',
                         'Display evidence is not semantic correctness, successful task effects or assistant authorship.',
                         'Physical I/O, energy and complete parent research costs remain separately unmeasured.']}
    (HERE / 'DISPLAY_OUTBOX_RECOVERY_RESULT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'checks': report['checks'], 'initial_state': r['state'], 'recovery_state': delivered['state'],
                      'recovery_native_calls': 0, 'recovery_seconds': report['recovery_seconds']}))


if __name__ == '__main__': audit(sys.argv[1])
