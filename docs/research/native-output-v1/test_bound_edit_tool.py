import json
import pytest
import bound_edit_tool as m

BINDING = 'a' * 64


def setup(tmp_path, checker=None, authority=None):
    target = tmp_path / 'workflow_memory.py'; target.write_bytes(b'old')
    return m.BoundEditTool(tmp_path/'tool', target, b'old', authority or (lambda: BINDING), checker or (lambda *args: {'checks': 'PASS'}), expected_binding=BINDING)


def request(call='c', old='old', new='new', version=0):
    return {'threadId': 't', 'turnId': 'u', 'tool': 'helix_apply_edits', 'callId': call,
            'arguments': {'expected_version': version, 'edits': [{'old': old, 'new': new}]}}


def test_success_duplicate_and_restart(tmp_path):
    checks = []; tool = setup(tmp_path, lambda *args: checks.append(1) or {'checks': 'PASS'})
    result = tool(request()); assert tool.target.read_bytes() == b'new' and result['success']
    assert tool(request()) == result and len(checks) == 1
    other = m.BoundEditTool(tool.directory, tool.target, b'old', lambda: BINDING, lambda *args: pytest.fail('Reexecuted'), expected_binding=BINDING)
    assert other(request()) == result
    with pytest.raises(ValueError, match='Conflicting'): tool(request(new='changed'))


def test_failed_checks_and_stale_version_preserve_source(tmp_path):
    tool = setup(tmp_path, lambda *args: {'checks': 'FAIL', 'error': 'actual failure'})
    assert not tool(request())['success'] and tool.target.read_bytes() == b'old'
    assert not tool(request('second', version=5))['success'] and tool.target.read_bytes() == b'old'


def test_protected_drift_and_uncertain_checker_do_not_repeat(tmp_path):
    calls = []
    def broken(*args): calls.append(1); raise RuntimeError('checker interrupted')
    tool = setup(tmp_path, broken)
    with pytest.raises(RuntimeError): tool(request())
    with pytest.raises(ValueError, match='Uncertain'): tool(request())
    with pytest.raises(ValueError, match='Unreconciled'): tool(request('another'))
    assert len(calls) == 1 and tool.target.read_bytes() == b'old'


def test_lost_publication_ack_recovers_without_reexecution(tmp_path, monkeypatch):
    checks = []; tool = setup(tmp_path, lambda *args: checks.append(1) or {'checks': 'PASS'})
    original = m.renderer.publish
    def lost(*args, **kwargs): original(*args, **kwargs); raise RuntimeError('lost ack after effect')
    monkeypatch.setattr(m.renderer, 'publish', lost)
    with pytest.raises(RuntimeError): tool(request())
    assert tool.target.read_bytes() == b'new'
    key = m.digest(m.encoded(['t', 'c']))
    reply = tool.recover_published(key)
    assert reply['success'] and len(checks) == 1 and tool(request()) == reply


def test_stale_source_and_recovery_are_rejected(tmp_path, monkeypatch):
    tool = setup(tmp_path); tool.target.write_bytes(b'foreign')
    with pytest.raises(ValueError, match='drift'): tool(request())
    with pytest.raises(ValueError): tool.recover_published(m.digest(m.encoded(['t', 'c'])))


def test_changed_authority_before_publication_stops(tmp_path):
    root = [BINDING]
    def checker(*args): root[0] = 'b'*64; return {'checks': 'PASS'}
    tool = setup(tmp_path, checker, lambda: root[0])
    with pytest.raises(ValueError, match='authority changed'): tool(request())
    assert tool.target.read_bytes() == b'old'


def test_restart_cannot_change_authority_or_target(tmp_path):
    tool = setup(tmp_path)
    with pytest.raises(ValueError, match='differs'):
        m.BoundEditTool(tool.directory, tool.target, b'old', lambda: 'b'*64, lambda *args: {'checks': 'PASS'}, expected_binding='b'*64)
