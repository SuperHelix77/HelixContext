import json
import sys
import pytest
from integrated_runtime import Runtime,Policy
from copy_handles import freeze


def test_restart_exact_skill_and_latent_evidence_recovery(tmp_path):
    r=Runtime(tmp_path,'p','main','old')
    first=r.record('1',b'000.250 cobalt\xff')
    checkpoint=r.checkpoint('Ship',{'helixcontext':b'Exact skill\n'},['Keep source unchanged'],[first['record_hash']])
    for i in range(2,51):r.record(str(i),f'Routine {i}'.encode())
    other=Runtime(tmp_path,'p','main','new')
    restored=other.restore(checkpoint)
    assert restored['skills']['helixcontext']==b'Exact skill\n'
    assert restored['records'][0]['raw']==b'000.250 cobalt\xff'
    assert other.search('cobalt')[0]['record_hash']==first['record_hash']
    with pytest.raises(ValueError):Runtime(tmp_path,'p','other','new').restore(checkpoint)
    with pytest.raises(ValueError):Runtime(tmp_path,'p','main','new',Policy(reducers=False)).restore(checkpoint)


def test_switches_completion_failure_and_events(tmp_path):
    r=Runtime(tmp_path/'store','p','main','s')
    raw=b'exact\r\n';key=r.store.put(raw)['sha256']
    catalog,_=freeze(r.store,{'A':{'source_sha256':key,'start_byte':0,'end_byte':len(raw)}})
    out=tmp_path/'result';out.write_bytes(b'prior')
    with pytest.raises(ValueError):r.complete(catalog,'["missing"]',out)
    assert out.read_bytes()==b'prior'
    import hashlib
    r.complete(catalog,'["A"]',out,hashlib.sha256(b'prior').hexdigest())
    assert out.read_bytes()==raw
    assert json.loads((r.store.root/'events.jsonl').read_text().splitlines()[-1])['type']=='completion'
    with pytest.raises(ValueError):Runtime(tmp_path/'store','p','main','s',Policy(completion=False)).complete(catalog,'["A"]',out)


@pytest.mark.parametrize('args',[{'minimum_saving_bytes':-1},{'minimum_saving_fraction':float('nan')},{'max_bytes':0},{'unknown':3}])
def test_all_policy_errors_precede_command(tmp_path,args):
    r=Runtime(tmp_path/'store','p','main','s')
    with pytest.raises((ValueError,TypeError)):
        r.command([sys.executable,'-c','open("side-effect","w").write("x")'],tmp_path,'test',**args)
    assert not (tmp_path/'side-effect').exists()


def test_memory_switch_and_miss_keep_recovery(tmp_path):
    r=Runtime(tmp_path,'p','main','s')
    refs=[r.record(str(i),raw)['record_hash'] for i,raw in enumerate([b'cobalt 31',b'other'])]
    assert len(r.working_set('cobalt',refs)['records'])==1
    miss=r.working_set('purple',refs)
    assert miss['recovery_required'] and miss['all_history_refs']==refs
    assert len(Runtime(tmp_path,'p','main','s',Policy(memory=False)).working_set('cobalt',refs)['records'])==2
