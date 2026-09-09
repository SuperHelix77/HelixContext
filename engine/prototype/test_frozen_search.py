import importlib
import pytest
from evidence import Store
from workflow_memory import Memory


def setup(tmp_path):
    m=Memory(Store(tmp_path));m.record('p','s','1',b'Violet envelope code 000.250')
    m.record('p','s','2',b'Other note')
    api=importlib.import_module('frozen_search');return m,api,api.build(m,'p')


def test_exact_query_and_absence_from_frozen_snapshot(tmp_path):
    m,api,ref=setup(tmp_path)
    assert [r['event_id'] for r in api.search(m,'p',ref,'VIOLET envelope')]==['1']
    assert api.search(m,'p',ref,'purple')==[]


def test_stale_snapshot_does_not_silently_omit_new_fact(tmp_path):
    m,api,ref=setup(tmp_path);m.record('p','s','3',b'violet updated')
    with pytest.raises(ValueError,match='Stale'):api.search(m,'p',ref,'violet')


def test_catalog_deletion_is_rejected(tmp_path):
    m,api,ref=setup(tmp_path)
    with m.db() as db:db.execute("DELETE FROM events WHERE event_id='1'")
    with pytest.raises(ValueError,match='Stale'):api.search(m,'p',ref,'violet')


def test_index_corruption_and_wrong_project_rejected(tmp_path):
    m,api,ref=setup(tmp_path)
    with pytest.raises(ValueError):api.search(m,'other',ref,'violet')
    (m.store.root/'objects'/ref['index_hash']).write_bytes(b'{}')
    with pytest.raises(ValueError):api.search(m,'p',ref,'violet')


def test_selected_source_corruption_still_fails_exact_retrieval(tmp_path):
    m,api,ref=setup(tmp_path);found=api.search(m,'p',ref,'violet')
    (m.store.root/'objects'/found[0]['source_hash']).write_bytes(b'bad')
    with pytest.raises(ValueError):m.retrieve('p',[found[0]['record_hash']])
