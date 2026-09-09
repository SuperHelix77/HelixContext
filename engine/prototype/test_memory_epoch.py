import base64
import json
import random
import pytest
from evidence import Store
from workflow_memory import Memory
import memory_epoch as epoch


def setup(tmp_path):
    m=Memory(Store(tmp_path))
    refs=[];raws=[]
    rng=random.Random(831910)
    # No priority or relevance selection: every early observation has equal form.
    for n in range(50):
        raw=(f'object {n:02d}; opaque receipt {rng.getrandbits(96):024x}; spelling 000.{n:03d}\r\n').encode()
        raws.append(raw);refs.append(m.record('P','early' if n<25 else 'late',str(n),raw)['record_hash'])
    root=epoch.freeze(m,'P',refs)['epoch_sha256']
    return m,refs,raws,root


@pytest.mark.parametrize('future_seed',[1,37,109,908])
def test_future_choice_after_capture_recovers_after_entire_index_loss(tmp_path,future_seed):
    m,refs,raws,root=setup(tmp_path)
    # Future selector is introduced after epoch creation, not used by compressor.
    selected=random.Random(future_seed).sample(range(50),7)
    with m.db() as db:
        db.execute('DELETE FROM search');db.execute('DELETE FROM events')
    fresh=Memory(Store(tmp_path))
    with pytest.raises(ValueError):fresh.retrieve('P',[refs[selected[0]]])
    with pytest.raises(ValueError):epoch.verify_live_catalog(fresh,root,'P')
    assert [r['raw'] for r in epoch.read(fresh.store,root,'P',[refs[i] for i in selected])]==[raws[i] for i in selected]
    assert fresh.timeline('P','early')==[] # Recovery does not silently rewrite DB.


def test_partial_deletion_is_not_successful_complete_history(tmp_path):
    m,refs,raws,root=setup(tmp_path)
    with m.db() as db:db.execute('DELETE FROM events WHERE record_hash=?',(refs[0],))
    with pytest.raises(ValueError):epoch.verify_live_catalog(m,root,'P')
    assert epoch.read(m.store,root,'P',[refs[0]])[0]['raw']==raws[0]


def test_later_events_do_not_mutate_old_epoch_or_get_smuggled_into_it(tmp_path):
    m,refs,raws,root=setup(tmp_path);before=m.store.get(root)
    later=m.record('P','later','51',b'new generation')
    assert epoch.verify_live_catalog(m,root,'P')['covered']==50
    assert m.store.get(root)==before
    with pytest.raises(ValueError):epoch.read(m.store,root,'P',[later['record_hash']])


def test_scope_and_tampered_source_fail_without_partial_result(tmp_path):
    m,refs,raws,root=setup(tmp_path)
    with pytest.raises(ValueError):epoch.read(m.store,root,'other',[refs[0]])
    source=epoch.load(m.store,root,'P')['records'][1]['source_hash']
    (m.store.root/'objects'/source).write_bytes(b'corrupt')
    with pytest.raises(ValueError):epoch.read(m.store,root,'P',refs[:2])
    assert epoch.read(m.store,root,'P',[refs[0]])[0]['raw']==raws[0]


def test_binary_pages_limits_and_end_cursor(tmp_path):
    m=Memory(Store(tmp_path));ref=m.record('P','s','x',b'\x00\xff\r\n')['record_hash'];root=epoch.freeze(m,'P',[ref])['epoch_sha256']
    p=epoch.page(m.store,root,'P',limit=1)
    assert base64.b64decode(p['records'][0]['base64'])==b'\x00\xff\r\n' and not p['has_more']
    assert epoch.page(m.store,root,'P',offset=1)['records']==[]
    with pytest.raises(ValueError):epoch.page(m.store,root,'P',max_bytes=1)
    with pytest.raises(ValueError):epoch.page(m.store,root,'P',offset=2)


def test_failed_freeze_does_not_return_a_published_root(tmp_path):
    m,refs,raws,root=setup(tmp_path)
    source=epoch.load(m.store,root,'P')['records'][0]['source_hash']
    (m.store.root/'objects'/source).write_bytes(b'changed')
    with pytest.raises(ValueError):epoch.freeze(m,'P',refs)
    assert epoch.load(m.store,root,'P')['count']==50


def test_pinned_manifest_tampering_and_wrong_root_type(tmp_path):
    m,refs,raws,root=setup(tmp_path)
    invalid=m.store.put(b'[]')['sha256']
    with pytest.raises(ValueError):epoch.load(m.store,invalid,'P')
    (m.store.root/'objects'/root).write_bytes(b'{}')
    with pytest.raises(ValueError):epoch.read(m.store,root,'P',[refs[0]])
