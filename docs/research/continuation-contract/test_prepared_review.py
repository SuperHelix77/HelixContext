import json
from pathlib import Path
import pytest
from prepared_review import prepare,validate,InvalidEvidence

def fixture(tmp_path):
    source=tmp_path/'source';source.mkdir()
    for n in ('proposal.py','CONTRACT.md','check.py','check_independence.py','supplemental.py'):(source/n).write_text('# fixture\n')
    return source,tmp_path/'evidence'

def test_valid_and_no_rerun(tmp_path):
    source,out=fixture(tmp_path);h=prepare(source,out)
    assert validate(out,h)['status']=='READY'
    with pytest.raises(FileExistsError):prepare(source,out)

@pytest.mark.parametrize('target',['source','snapshot','stdout','receipt'])
def test_staleness_or_tampering_rejected(tmp_path,target):
    source,out=fixture(tmp_path);h=prepare(source,out)
    p={'source':source/'CONTRACT.md','snapshot':out/'check/queue_state.py','stdout':out/'check/stdout.bin','receipt':out/'receipt.json'}[target]
    p.write_bytes(p.read_bytes()+b'changed')
    with pytest.raises((InvalidEvidence,json.JSONDecodeError)):validate(out,h)

def test_failure_stops_without_rerun(tmp_path):
    source,out=fixture(tmp_path);(source/'check.py').write_text('raise RuntimeError("failure")\n');h=prepare(source,out)
    r=json.loads((out/'receipt.json').read_text());assert len(r['checks'])==1 and r['status']=='NOT_READY'
    with pytest.raises(InvalidEvidence):validate(out,h)

def test_mutation_rejected(tmp_path):
    source,out=fixture(tmp_path);(source/'check.py').write_text('from pathlib import Path\nPath("queue_state.py").write_text("changed")\n');h=prepare(source,out)
    assert json.loads((out/'receipt.json').read_text())['checks'][0]['status']=='MUTATED_INPUT'
    with pytest.raises(InvalidEvidence):validate(out,h)
