import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import pytest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('witness_adapter',HERE/'adapter.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
VALID=HERE.with_name('native-output-v1')/'artifacts/astra-xhigh/on/workflow_memory.py'


def fixture(tmp_path):
    c=tmp_path/'candidate.py';c.write_bytes(VALID.read_bytes())
    return c,a.bind(a.oblig.BASE/'TASK.md',a.oblig.BASE/'baseline/workflow_memory.py',c)


def test_original_program_exact_and_query_changes_only_literal_ast_values():
    assert a.compile_query({'query':'unlisted_token'})==a.TEMPLATE.read_bytes()
    original=list(ast.walk(ast.parse(a.TEMPLATE.read_bytes())))
    for q in ('café','a"b',"x'); __import__('os').system('false'); #"):
        compiled=list(ast.walk(ast.parse(a.compile_query({'query':q}))))
        assert len(original)==len(compiled)
        changed=0
        for old,new in zip(original,compiled):
            assert type(old) is type(new)
            if isinstance(old,ast.Constant) and old.value in (b'unlisted_token','unlisted_token','unlisted_token '):
                assert new.value=={b'unlisted_token':q.encode(),'unlisted_token':q,'unlisted_token ':q+' '}[old.value]
                changed+=1
            elif isinstance(old,ast.Constant):assert old.value==new.value
            elif isinstance(old,ast.Name):assert old.id==new.id
        assert changed==5


def test_fresh_hash_task_change_is_not_new_semantic_authority(tmp_path):
    task=tmp_path/'TASK.md';task.write_text('Allow query-specific empty returns.')
    with pytest.raises(ValueError,match='Unqualified task'):
        a.bind(task,a.oblig.BASE/'baseline/workflow_memory.py',VALID)


def test_stale_source_fails_before_execution(tmp_path):
    c,b=fixture(tmp_path);c.write_bytes(c.read_bytes()+b'\n# drift\n')
    with pytest.raises(ValueError,match='binding changed'):
        a.run({'query':'alpha'},b,tmp_path/'out',runner=lambda *a,**k:pytest.fail('executed stale input'))
    assert not (tmp_path/'out').exists()


def test_interrupted_duplicate_never_executes(tmp_path):
    _,b=fixture(tmp_path);out=tmp_path/'out';out.mkdir()
    with pytest.raises(FileExistsError):
        a.run({'query':'alpha'},b,out,runner=lambda *a,**k:pytest.fail('retry'))


def test_post_execution_binding_drift_is_failed_evidence(tmp_path):
    c,b=fixture(tmp_path)
    def drift(*args,**kwargs):
        result=subprocess.run(*args,**kwargs);c.write_bytes(c.read_bytes()+b'\n# changed\n');return result
    with pytest.raises(ValueError,match='binding changed'):
        a.run({'query':'alpha'},b,tmp_path/'out',runner=drift)
    r=json.loads((tmp_path/'out/receipt.json').read_text())
    assert r['state']=='FAILED_NO_VALID_OBSERVATIONS'
    assert (tmp_path/'out/stdout').stat().st_size>0


@pytest.mark.parametrize('code,stdout',[(1,b''),(0,b'{}'),(0,b'not json')])
def test_failed_or_malformed_output_cannot_be_success(tmp_path,code,stdout):
    _,b=fixture(tmp_path)
    def fail(*args,**kwargs):return subprocess.CompletedProcess(args[0],code,stdout,b'raw diagnostic')
    with pytest.raises((ValueError,json.JSONDecodeError)):
        a.run({'query':'alpha'},b,tmp_path/'out',runner=fail)
    r=json.loads((tmp_path/'out/receipt.json').read_text())
    assert r['state']=='FAILED_NO_VALID_OBSERVATIONS'
    assert (tmp_path/'out/stderr').read_bytes()==b'raw diagnostic'


def test_timeout_preserves_partial_output_without_retry(tmp_path):
    _,b=fixture(tmp_path);calls=[]
    def timeout(*args,**kwargs):
        calls.append(1);raise subprocess.TimeoutExpired(args[0],30,output=b'partial',stderr=b'error')
    with pytest.raises(subprocess.TimeoutExpired):a.run({'query':'alpha'},b,tmp_path/'out',runner=timeout)
    assert calls==[1] and (tmp_path/'out/stdout').read_bytes()==b'partial'
    assert json.loads((tmp_path/'out/receipt.json').read_text())['state']=='FAILED_NO_VALID_OBSERVATIONS'


def test_unsupported_request_does_not_start_process(tmp_path):
    _,b=fixture(tmp_path)
    for n,r in enumerate(({'query':'alpha','code':'print(1)'},{'query':False},{'query':''},{'query':'a'*129})):
        with pytest.raises(ValueError):a.run(r,b,tmp_path/str(n),runner=lambda *a,**k:pytest.fail('executed'))
        assert not (tmp_path/str(n)).exists()
