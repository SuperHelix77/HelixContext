import importlib.util
import json
from pathlib import Path
import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('hostile_pilot', HERE / 'pilot.py')
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)


def gate(tmp_path, monkeypatch):
    source = tmp_path / 'source'; source.write_text('bound source')
    m = {'model': p.MODEL, 'effort': p.EFFORT, 'native_turns_authorized': 1,
         'bindings': {str(source): p.sha(source)}, 'comparison_binding': {}}
    p.save(tmp_path / 'manifest.json', m)
    p.save(tmp_path / 'PREFLIGHT.json', {'state': 'PASS', 'model_turns': 0,
        'manifest_sha256': p.sha(tmp_path / 'manifest.json')})
    monkeypatch.setattr(p.compare, 'guard', lambda b: None)
    monkeypatch.setattr(p.old.native, 'Session', lambda *a, **k: pytest.fail('native call escaped gate'))
    return m, source


def test_fresh_source_hash_cannot_reuse_old_preflight(tmp_path, monkeypatch):
    m, source = gate(tmp_path, monkeypatch)
    source.write_text('new source'); m['bindings'][str(source)] = p.sha(source)
    p.save(tmp_path / 'manifest.json', m)
    with pytest.raises(ValueError, match='Preflight'):
        p.run(tmp_path)
    assert not (tmp_path / 'result.json').exists()


def test_changed_source_rejects_before_native(tmp_path, monkeypatch):
    _, source = gate(tmp_path, monkeypatch); source.write_text('drift')
    with pytest.raises(ValueError, match='Binding changed'):
        p.run(tmp_path)
    assert not (tmp_path / 'result.json').exists()


def test_interrupted_or_duplicate_start_has_no_retry(tmp_path, monkeypatch):
    gate(tmp_path, monkeypatch)
    (tmp_path / 'result.json').write_text('{"state":"RUNNING"}')
    with pytest.raises(FileExistsError): p.run(tmp_path)
    assert json.loads((tmp_path / 'result.json').read_text()) == {'state': 'RUNNING'}
