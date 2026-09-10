import copy
from concurrent.futures import ThreadPoolExecutor
import shlex
import pytest
from evidence import Store
from workflow_memory import Memory
from delivery_outbox import DisplayOutbox


def box(path):
    return DisplayOutbox(Memory(Store(path)))


def stage(path):
    b = box(path)
    return b, b.stage('committed-E01', 'thread-1', b'ACK E01\n', 'a' * 64)


def claim(b, ticket):
    return b.claim(ticket, current_authority='a' * 64, explicit_user_command=True, thread_idle=True)


def history(submitted):
    text = submitted['command'].split("'%s' ", 1)[1][1:-1]
    return {'id': 'thread-1', 'turns': [{'id': 'turn-1', 'status': 'completed', 'items': [{
        'id': 'item-1', 'type': 'commandExecution', 'source': 'userShell',
        'command': submitted['command'], 'status': 'completed', 'exitCode': 0, 'aggregatedOutput': text}]}]}


def test_lost_ack_restart_duplicate_reconciles_without_resubmit(tmp_path):
    b, ticket = stage(tmp_path)
    sent = claim(b, ticket)
    assert sent['submit']
    b = box(tmp_path)  # Caller may have lost the submission acknowledgement.
    assert claim(b, ticket) == {'state': 'RECONCILE', 'submit': False}
    evidence = history(sent)
    first = b.reconcile(ticket, evidence)
    assert first['state'] == 'DELIVERED'
    assert box(tmp_path).reconcile(ticket, evidence) == first
    assert claim(box(tmp_path), ticket) == first


def test_two_callers_only_one_can_submit(tmp_path):
    b, ticket = stage(tmp_path)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: claim(box(tmp_path), ticket), range(2)))
    assert sum(r['submit'] for r in results) == 1


@pytest.mark.parametrize('key,value', [('current_authority', 'b' * 64), ('explicit_user_command', False), ('thread_idle', False)])
def test_preflight_cannot_spend_submission(tmp_path, key, value):
    b, ticket = stage(tmp_path)
    args = dict(current_authority='a' * 64, explicit_user_command=True, thread_idle=True)
    args[key] = value
    assert b.claim(ticket, **args) == {'state': 'HOLD', 'submit': False}
    assert claim(b, ticket)['submit']


@pytest.mark.parametrize('fault', ['missing', 'duplicate', 'command', 'output', 'source', 'turn_pending', 'item_pending', 'bool_exit', 'false_pass'])
def test_bad_native_evidence_never_delivers_or_resubmits(tmp_path, fault):
    b, ticket = stage(tmp_path)
    sent = claim(b, ticket)
    h = history(sent)
    turn = h['turns'][0]; item = turn['items'][0]
    if fault == 'missing': h['turns'] = []
    if fault == 'duplicate': turn['items'].append(copy.deepcopy(item))
    if fault == 'command': item['command'] = '/usr/bin/true'
    if fault == 'output': item['aggregatedOutput'] = 'different'
    if fault == 'source': item['source'] = 'agent'
    if fault == 'turn_pending': turn['status'] = 'inProgress'
    if fault == 'item_pending': item['status'] = 'inProgress'
    if fault == 'bool_exit': item['exitCode'] = False
    if fault == 'false_pass': item['status'] = 'completed'; item['exitCode'] = 1
    assert b.reconcile(ticket, h)['state'] == 'RECONCILE'
    assert claim(box(tmp_path), ticket)['submit'] is False


def test_failed_command_and_wrong_thread(tmp_path):
    b, ticket = stage(tmp_path); sent = claim(b, ticket); h = history(sent)
    h['id'] = 'other'
    with pytest.raises(ValueError): b.reconcile(ticket, h)
    h['id'] = 'thread-1'; item = h['turns'][0]['items'][0]
    item.update(status='failed', exitCode=1, aggregatedOutput='')
    r = b.reconcile(ticket, h)
    assert r['state'] == 'FAILED' and claim(box(tmp_path), ticket) == r


def test_conflicting_stage_and_tampered_request(tmp_path):
    b, ticket = stage(tmp_path)
    assert b.stage('committed-E01', 'thread-1', b'ACK E01\n', 'a' * 64) == ticket
    with pytest.raises(ValueError): b.stage('committed-E01', 'thread-1', b'changed', 'a' * 64)
    (b.memory.store.root / 'objects' / ticket['request_hash']).write_bytes(b'changed')
    with pytest.raises(ValueError): claim(b, ticket)


def test_failed_evidence_write_does_not_publish_delivery(tmp_path, monkeypatch):
    b, ticket = stage(tmp_path); sent = claim(b, ticket); put = b.memory.store.put
    def fail(raw): raise OSError('injected lost disk write')
    monkeypatch.setattr(b.memory.store, 'put', fail)
    with pytest.raises(OSError): b.reconcile(ticket, history(sent))
    assert claim(box(tmp_path), ticket)['state'] == 'RECONCILE'
    monkeypatch.setattr(b.memory.store, 'put', put)
    assert b.reconcile(ticket, history(sent))['state'] == 'DELIVERED'


@pytest.mark.parametrize('fault', ['none', 'extra_arg', 'different_shell', 'different_flags', 'extra_command', 'malformed'])
def test_exact_native_shell_envelope(tmp_path, fault):
    b, ticket = stage(tmp_path); sent = claim(b, ticket); h = history(sent)
    argv = ['/bin/zsh', '-lc', sent['command']]
    if fault == 'extra_arg': argv.append('additional')
    if fault == 'different_shell': argv[0] = '/bin/bash'
    if fault == 'different_flags': argv[1] = '-c'
    if fault == 'extra_command': argv[2] += '; /usr/bin/false'
    h['turns'][0]['items'][0]['command'] = shlex.join(argv) if fault != 'malformed' else "'unterminated"
    assert b.reconcile(ticket, h)['state'] == 'RECONCILE'  # No implicit wrapper stripping.
    result = b.reconcile(ticket, h, native_shell=('/bin/zsh', '-lc'))
    assert result['state'] == ('DELIVERED' if fault == 'none' else 'RECONCILE')


def test_untrusted_output_stays_one_literal_argument(tmp_path):
    import json
    b = box(tmp_path)
    raw = b"quotes ' `whoami` $(touch forbidden) ;\\n\n"
    ticket = b.stage('literal-output', 'thread-1', raw, 'a' * 64)
    sent = claim(b, ticket)
    packet = json.loads(b.memory.store.get(ticket['request_hash']))
    assert shlex.split(sent['command']) == ['/usr/bin/printf', '%s', packet['display']]
    assert packet['display'].endswith(raw.decode())
