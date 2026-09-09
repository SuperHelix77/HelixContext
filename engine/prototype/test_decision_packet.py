import copy
import pytest
from evidence import Store
from decision_packet import metadata,verify_metadata,history,preflight
from integrated_runtime import Runtime
import sys


def test_exact_fields_and_mutated_type_rejected(tmp_path):
    s=Store(tmp_path);raw=b'{"id":"A","approved":false,"payload":"opaque"}\n'
    view=metadata(s,raw,['id','approved'],['payload'])
    assert view['records']==1 and view['metadata'][0]['approved'] is False
    corrupt=copy.deepcopy(view);corrupt['metadata'][0]['approved']=0
    with pytest.raises(ValueError):verify_metadata(s,corrupt)
    (tmp_path/'objects'/view['source']['sha256']).write_bytes(b'changed')
    with pytest.raises(ValueError):verify_metadata(s,view)


@pytest.mark.parametrize('raw',[b'{"id":"A","id":"B","payload":1}',b'{"id":"A","payload":1,"new_decision_field":1}',b'{"id":"A","payload":NaN}'])
def test_new_unknown_or_ambiguous_information_is_not_silently_omitted(tmp_path,raw):
    with pytest.raises(ValueError):metadata(Store(tmp_path),raw,['id'],['payload'])


def test_history_keeps_superseded_and_latent_facts(tmp_path):
    r=Runtime(tmp_path,'p','b','s');refs=[r.record(str(i),v)['record_hash'] for i,v in enumerate([b'cutoff 29 old',b'cutoff 30 current',b'latent 000.250'])]
    packet=history(r.retrieve(refs))
    assert [v['text'] for v in packet['events']]==['cutoff 29 old','cutoff 30 current','latent 000.250']


def test_preflight_keeps_failure_evidence_without_telemetry(tmp_path):
    r=Runtime(tmp_path/'s','p','b','s')
    result=r.command([sys.executable,'-c',"print('notice\\n'*1000+'FAILED test_one - defect\\n==== 1 failed, 2 passed in 0.02s ====');raise SystemExit(7)"],tmp_path,'test',format_hint='pytest')
    packet=preflight(r.store,result['visible'])
    assert packet['exit_code']==7 and packet['streams']['stdout']['diagnostics'][0]['text'].startswith('FAILED test_one')
    assert 'middleware_io' not in packet and 'store' not in packet
    assert r.store.retrieve(packet['receipt'])['text'].endswith('==== 1 failed, 2 passed in 0.02s ====\n')
