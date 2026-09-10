"""No inference. Test recovery boundaries and source/grade integrity."""
import hashlib
from pathlib import Path
import subprocess
import pytest
import maintenance_release as r


def test_bad_edit_repair_but_stale_source_fatal():
    raw = b'original'; key = hashlib.sha256(raw).hexdigest()
    assert 'edit_error' in r.proposal('{bad', raw, key)[2]
    assert 'edit_error' in r.proposal('{"edits":[{"old":"missing","new":"x"}]}', raw, key)[2]
    with pytest.raises(RuntimeError, match='source changed'):
        r.proposal('{bad', b'stale', key)
    assert 'semantic_attention' in r.proposal('{"semantic_obligations":["missing authority"]}', raw, key)[2]


def test_scope_rejects_protected_and_untracked_files(tmp_path):
    (tmp_path / r.TARGET).write_text('old')
    (tmp_path / 'protected').write_text('constant')
    bound = r.workspace.initialize(tmp_path)
    (tmp_path / r.TARGET).write_text('new'); r.scope(tmp_path, bound)
    (tmp_path / 'protected').write_text('tamper')
    with pytest.raises(RuntimeError): r.scope(tmp_path, bound)
    (tmp_path / 'protected').write_text('constant')
    (tmp_path / 'extra').write_text('unexpected')
    with pytest.raises(RuntimeError): r.scope(tmp_path, bound)


def test_grader_rejects_actual_baseline(tmp_path):
    cwd = tmp_path / 'task'; cwd.mkdir()
    for name in r.FILES:
        source = r.INPUT / ('baseline/' + name if name != r.FILES[-1] else name)
        (cwd / name).write_bytes(source.read_bytes())
    result = r.grade(cwd, tmp_path / 'check')
    assert result['checks'] == 'FAIL' and all(x['exit_code'] != 0 for x in result['rows'])


def test_checker_mutation_is_fatal(tmp_path, monkeypatch):
    cwd = tmp_path / 'task'; cwd.mkdir()
    for name in r.FILES: (cwd / name).write_text('original')
    def mutate(*args, **kwargs):
        (cwd / r.TARGET).write_text('changed')
        return subprocess.CompletedProcess(args, 1, b'failure', b'')
    monkeypatch.setattr(r.subprocess, 'run', mutate)
    with pytest.raises(RuntimeError, match='mutated'):
        r.grade(cwd, tmp_path / 'check')


def test_actual_publication_preserves_declared_lock_scope(tmp_path):
    cwd = tmp_path / 'task'; cwd.mkdir()
    raw = b'old'; (cwd / r.TARGET).write_bytes(raw)
    lock = cwd / (r.TARGET + '.helix-lock'); lock.touch()
    bound = r.workspace.initialize(cwd)
    store = r.Store(tmp_path / 'store'); key = store.put(raw)['sha256']
    _, plan, error = r.proposal('{"edits":[{"old":"old","new":"new"}]}', raw, key)
    assert error is None
    receipt = r.renderer.publish(store, plan, cwd / r.TARGET, expected_sha256=key)
    assert receipt['sha256'] == r.sha(cwd / r.TARGET)
    r.scope(cwd, bound)
    assert lock.read_bytes() == b''
    lock.write_bytes(b'foreign metadata')
    with pytest.raises(RuntimeError): r.scope(cwd, bound)
