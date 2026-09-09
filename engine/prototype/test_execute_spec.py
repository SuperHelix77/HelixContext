import json
from pathlib import Path

from test_named_plans import setup
from test_plan_cli import call


def spec_file(tmp_path,root,opts,**changes):
    spec={k:v for k,v in opts.items() if k!='environment'}
    spec.update(cwd=str(root),plan_id='execute-spec',plan_version=1,env_names=[])
    spec.update(changes)
    path=tmp_path/'spec.json';path.write_text(json.dumps(spec));return path


def test_execute_spec_preserves_registration_cost_and_step_receipts(tmp_path):
    store,root,opts,_=setup(tmp_path)
    path=spec_file(tmp_path,root,opts)
    proc,packet=call(store,'execute-spec',str(path))
    assert proc.returncode==0 and packet['status']=='SUCCEEDED'
    assert packet['semantic_success'] is None
    detail=store.receipt(packet['details'])
    assert detail['registration']['reference']==packet['plan']
    assert detail['registration']['creation_cost']['bytes_hashed']>0
    assert store.retrieve(packet['steps'][0]['receipt'])['text']=='000.250\n'


def test_failed_registration_does_not_execute_or_silently_rebind(tmp_path):
    store,root,opts,_=setup(tmp_path)
    path=spec_file(tmp_path,root,opts)
    proc,packet=call(store,'execute-spec',str(path))
    assert proc.returncode==0
    before=set((store.root/'plan-runs').iterdir())
    (root/'input.txt').write_text('changed')
    proc,packet=call(store,'execute-spec',str(path))
    assert proc.returncode==2 and packet['status']=='ERROR'
    assert set((store.root/'plan-runs').iterdir())==before


def test_execute_spec_failure_keeps_evidence_and_stops_remaining_steps(tmp_path):
    store,root,opts,_=setup(tmp_path,code='print("fault");raise SystemExit(7)')
    steps=[*opts['steps'],{'name':'forbidden','argv':['python','-c','open("bad","w").close()']}]
    path=spec_file(tmp_path,root,opts,steps=steps)
    proc,packet=call(store,'execute-spec',str(path))
    assert proc.returncode==1 and packet['failed_steps']==['job']
    assert packet['steps_completed']==1 and not (Path(packet['workspace'])/'bad').exists()
    assert store.retrieve(packet['steps'][0]['receipt'])['text']=='fault\n'
