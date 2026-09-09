import json,subprocess
from types import SimpleNamespace
import pytest
from caller_memory_receipt import prepare,attach,digest


def test_receipt_binds_task_scope_and_exact_evidence(tmp_path):
    def runner(args,**kw):
        return SimpleNamespace(stdout=json.dumps({'query':'q','cwd':str(tmp_path),'memories':[{'id':1,'cwd':'/different/run','content':'answer leak'}]}).encode(),stderr=b'',returncode=0)
    out=tmp_path/'receipt';r=prepare(tmp_path,'task','q',out,runner)
    pin=digest((out/'receipt.json').read_bytes())
    assert r['state']=='completed' and r['excluded_other_scope_count']==1
    assert 'answer leak' not in attach(tmp_path,'task',out,pin)
    with pytest.raises(ValueError):attach(tmp_path,'different task',out,pin)
    with pytest.raises(ValueError):attach(tmp_path/'other','task',out,pin)
    (out/'raw.json').write_bytes(b'altered')
    with pytest.raises(ValueError):attach(tmp_path,'task',out,pin)


@pytest.mark.parametrize('kind',['failed','timeout','wrong_response'])
def test_optional_memory_failure_is_not_false_success(tmp_path,kind):
    def runner(*a,**k):
        if kind=='timeout':raise subprocess.TimeoutExpired('synthetic',30)
        return SimpleNamespace(stdout=b'{}',stderr=b'error',returncode=1 if kind=='failed' else 0)
    out=tmp_path/'receipt';r=prepare(tmp_path,'task','q',out,runner)
    pin=digest((out/'receipt.json').read_bytes())
    assert r['state']=='unavailable' and 'unavailable' in attach(tmp_path,'task',out,pin)
    (out/'receipt.json').write_text('{}')
    with pytest.raises(ValueError):attach(tmp_path,'task',out,pin)
