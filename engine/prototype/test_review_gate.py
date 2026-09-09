import sys
import pytest
from evidence import Store
from review_gate import Gate


def setup(tmp_path):
    gate=Gate(Store(tmp_path));root=gate.bundle({'code.py':b'old','CONTRACT.md':b'contract-v1'})
    head=gate.initialize('task',root);review=gate.store.put(b'Explicit fixture semantic review, not a model result')['sha256']
    return gate,head,review


def stage(g,h,key='attempt',success=True):
    return g.stage(key,'task',h,{'code.py':b'new'},steps=[{'name':'check','argv':[sys.executable,'-c','import sys;sys.exit('+('0' if success else '1')+')']}],environment_id='offline-fixture',env={},timeout=5)


def test_pass_requires_review_and_keeps_original_files(tmp_path):
    g,h,r=setup(tmp_path);a=stage(g,h)
    assert a['status']=='AWAITING_REVIEW' and g.head('task')==h
    assert g.files(h['root'])['code.py']==b'old'
    assert g.review('attempt',approve=True,reviewer='fixture',evidence_ref=r)['status']=='ACCEPTED'
    assert g.files(g.head('task')['root'])['code.py']==b'new'
    with pytest.raises(ValueError):g.review('attempt',approve=True,reviewer='fixture',evidence_ref=r)


def test_semantic_rejection_keeps_committed_state(tmp_path):
    g,h,r=setup(tmp_path);stage(g,h)
    assert g.review('attempt',approve=False,reviewer='fixture',evidence_ref=r)['status']=='REJECTED'
    assert g.head('task')==h


def test_changed_authority_and_aba_cannot_accept_old_review(tmp_path):
    g,h,r=setup(tmp_path);stage(g,h)
    changed=g.bundle({'code.py':b'old','CONTRACT.md':b'contract-v2'})
    second=g.advance('task',h,changed);third=g.advance('task',second,h['root'])
    assert third['root']==h['root'] and third['revision']!=h['revision']
    assert g.review('attempt',approve=True,reviewer='fixture',evidence_ref=r)['status']=='CONFLICT'
    assert g.head('task')==third


def test_second_candidate_cannot_overwrite_first_accepted_candidate(tmp_path):
    g,h,r=setup(tmp_path);stage(g,h,'one');stage(g,h,'two')
    g.review('one',approve=True,reviewer='fixture',evidence_ref=r);accepted=g.head('task')
    assert g.review('two',approve=True,reviewer='fixture',evidence_ref=r)['status']=='CONFLICT'
    assert g.head('task')==accepted


def test_failed_checker_is_cold_evidence_not_committed_source(tmp_path):
    g,h,r=setup(tmp_path);a=stage(g,h,success=False)
    assert a['status']=='CHECK_FAILED' and g.head('task')==h and a['evidence']
    with pytest.raises(ValueError):g.review('attempt',approve=True,reviewer='fixture',evidence_ref=r)
    with pytest.raises(Exception):stage(g,h) # Existing attempt cannot execute twice.


def test_stale_preflight_reserves_nothing(tmp_path):
    g,h,r=setup(tmp_path);g.advance('task',h,h['root'])
    with pytest.raises(ValueError):stage(g,h)
    with pytest.raises(ValueError):g.attempt('attempt')


def test_snapshot_modification_fails_even_when_process_exits_zero(tmp_path):
    g,h,r=setup(tmp_path)
    a=g.stage('attempt','task',h,{'code.py':b'new'},steps=[{'name':'check','argv':[sys.executable,'-c',"from pathlib import Path;Path('CONTRACT.md').write_text('changed')"]}],environment_id='fixture',env={})
    assert a['status']=='CHECK_FAILED' and g.head('task')==h


def test_restart_and_corrupt_candidate_do_not_publish(tmp_path):
    g,h,r=setup(tmp_path);a=stage(g,h);g=Gate(Store(tmp_path))
    candidate=g.store.receipt(a['candidate']);(g.store.root/'objects'/candidate['files']['code.py']).write_bytes(b'tampered')
    with pytest.raises(ValueError):g.review('attempt',approve=True,reviewer='fixture',evidence_ref=r)
    assert g.head('task')==h and g.attempt('attempt')['status']=='AWAITING_REVIEW'


@pytest.mark.parametrize('key',['.','..','../escape','a/b'])
def test_unsafe_identity_rejected_before_reservation(tmp_path,key):
    g,h,r=setup(tmp_path)
    with pytest.raises(ValueError):stage(g,h,key)
    with pytest.raises(ValueError):g.bundle({key:b'bad'})
    assert g.head('task')==h


def test_cross_task_expected_state_rejected(tmp_path):
    g,h,r=setup(tmp_path);other=g.initialize('other',h['root'])
    with pytest.raises(ValueError):stage(g,other)
    with pytest.raises(ValueError):g.advance('task',other,h['root'])
    assert g.head('task')==h


def test_mismatched_valid_evidence_cannot_publish(tmp_path):
    g,h,r=setup(tmp_path);a=stage(g,h,'one');b=stage(g,h,'two')
    # Both evidence objects are intact, but belong to different attempts.
    with g.db() as db:db.execute('UPDATE attempts SET evidence=? WHERE id=?',(b['evidence'],'one'))
    with pytest.raises(ValueError,match='Evidence does not certify'):g.review('one',approve=True,reviewer='fixture',evidence_ref=r)
    assert g.head('task')==h


def test_interruption_after_effect_remains_started_and_never_replays(tmp_path,monkeypatch):
    import checked_steps
    real_execute=checked_steps.execute
    g,h,r=setup(tmp_path)
    def interrupt(*args,**kwargs):
        real_execute(*args,**kwargs)
        raise KeyboardInterrupt('after process, before gate receipt')
    monkeypatch.setattr(checked_steps,'execute',interrupt)
    with pytest.raises(KeyboardInterrupt):
        g.stage('attempt','task',h,{'code.py':b'new'},steps=[{'name':'effect','argv':[sys.executable,'-c',"from pathlib import Path;Path('effect').write_text('once')"]}],environment_id='fixture',env={})
    g=Gate(Store(tmp_path))
    assert g.attempt('attempt')['status']=='STARTED'
    assert (tmp_path/'review-attempts'/'attempt'/'effect').read_text()=='once'
    monkeypatch.setattr(checked_steps,'execute',lambda *a,**kw:pytest.fail('must not replay'))
    with pytest.raises(Exception):stage(g,h)
    with pytest.raises(ValueError):g.review('attempt',approve=True,reviewer='fixture',evidence_ref=r)
    assert g.head('task')==h


def test_concurrent_approvals_publish_only_one_revision(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    g,h,r=setup(tmp_path);stage(g,h,'one');stage(g,h,'two');barrier=Barrier(2)
    def approve(key):
        local=Gate(Store(tmp_path));barrier.wait(timeout=5)
        return local.review(key,approve=True,reviewer='fixture',evidence_ref=r)['status']
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(approve,['one','two']))
    assert sorted(results)==['ACCEPTED','CONFLICT']
    assert g.head('task')['revision']==h['revision']+1
