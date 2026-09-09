import json
from integrated_v2 import prepare


def test_v2_closes_evidence_and_admission_contract_without_answer_key(tmp_path):
    root,m,prompts,runtimes,catalog,expected=prepare(tmp_path/'pair')
    assert m['schema'].endswith('.v2')
    assert m['v2']['complete_history_events']==4
    assert 'SHA256 '+m['source_sha256'] in prompts['on']
    assert 'caller declares' in prompts['on']
    assert 'middleware_io' not in prompts['on']
    assert 'runtime-b09051' not in prompts['on']
    assert json.loads((root/'manifest.json').read_text())['prompts']['on']==m['prompts']['on']
    assert (root/'tasks/on/AGENTS.md').read_bytes()==(root/'tasks/off/AGENTS.md').read_bytes()
    assert m['preparation']['on']['source_hashes']['helixcontext/SKILL.md']==m['preparation']['off']['source_hashes']['helixcontext/SKILL.md']


def test_caller_registers_real_emitted_identity_without_global_database(tmp_path,monkeypatch):
    import integrated_v2 as v2
    cwd=tmp_path/'tasks/on';cwd.mkdir(parents=True)
    (cwd/'helixcontext').mkdir();(cwd/'helixcontext/SKILL.md').write_text('---\nname: helixcontext\n---\nExact skill\n')
    out=tmp_path/'receipts/on'
    def fake_native(model,cwd,prompt,out):
        out.mkdir(parents=True)
        (out/'events.jsonl').write_text(json.dumps({'type':'thread.started','thread_id':'offline-fixture-thread'})+'\n')
        import time
        time.sleep(.15)
        return '[]',{'state':'completed'}
    monkeypatch.setattr(v2,'BASE_NATIVE',fake_native)
    answer,status=v2.native('fixture',cwd,'prompt',out)
    receipt=json.loads((tmp_path/'registration.json').read_text())
    assert receipt['native_thread_id']=='offline-fixture-thread' and receipt['state']=='registered'
    assert receipt['observer_read_bytes']>0 and (cwd/'.helix/continuity.sqlite3').exists()


def test_registration_failure_cannot_be_qualified(tmp_path,monkeypatch):
    import integrated_v2 as v2
    import pytest
    cwd=tmp_path/'tasks/on';cwd.mkdir(parents=True);out=tmp_path/'receipts/on'
    def fake_native(model,cwd,prompt,out):
        out.mkdir(parents=True)
        (out/'events.jsonl').write_text(json.dumps({'type':'thread.started','thread_id':'offline-fixture-thread'})+'\n')
        import time
        time.sleep(.15)
        return '[]',{'state':'completed'}
    monkeypatch.setattr(v2,'BASE_NATIVE',fake_native)
    with pytest.raises(RuntimeError):v2.native('fixture',cwd,'prompt',out)
    assert json.loads((tmp_path/'registration.json').read_text())['state']=='failed'
