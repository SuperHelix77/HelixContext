import importlib.util
from pathlib import Path
import subprocess
import sys
import pytest

HERE=Path(__file__).resolve().parent


def module(name):
    s=importlib.util.spec_from_file_location('mixed_protocol_'+name,HERE/(name+'.py'))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def test_checkpoint_distribution_and_delayed_target():
    p=module('protocol');f=p.fixture()
    assert len(f['events'])==50 and f['semantic_checkpoints']==[12,25,38,50]
    assert sum(e['turn'] not in p.CHECKPOINTS for e in f['events'])==46
    tag=f['events'][37]['data']['required_inventory_tag']
    assert any(n['inventory_tag']==tag for n in f['events'][0]['data']['notes'])
    assert all('required_inventory_tag' not in e['data'] for e in f['events'][:37])


def test_reference_passes_independent_grades():
    c=module('checks')
    for stage in [25,38,50]:c.check(stage,HERE/'reference.py')


def test_public_checks_have_no_future_stage_leak(tmp_path):
    public=module('public_checks')
    assert 'label_exact' not in public.source(25) and 'previous exact bytes' not in public.source(38)
    (tmp_path/'planner.py').write_bytes((HERE/'reference.py').read_bytes())
    for stage in [25,38,50]:
        p=tmp_path/'check_current.py';p.write_text(public.source(stage))
        r=subprocess.run([sys.executable,'-B',str(p)],cwd=tmp_path,capture_output=True,timeout=10)
        assert r.returncode==0,r.stderr.decode()


def test_unimplemented_source_fails():
    with pytest.raises(NotImplementedError):module('checks').check(25,HERE/'planner.py')


@pytest.mark.parametrize('name,stage', [('adjacency',25),('normalization',38),('eager_truncation',50)])
def test_hostile_mutants_rejected(tmp_path,name,stage):
    c=module('checks');raw=(HERE/'reference.py').read_text()
    if name=='adjacency':raw=raw.replace('a<result[-1][1]','a<=result[-1][1]')
    elif name=='normalization':raw=raw.replace('k:row[k] for k in','k:row[k].strip() for k in')
    else:
        raw=raw[:raw.index('def write_plan')] + '''def write_plan(path,rows):
    with open(path,'w') as stream:json.dump(build_plan(rows),stream)
'''
    p=tmp_path/'mutant.py';p.write_text(raw)
    with pytest.raises(AssertionError):c.check(stage,p)
