import base64
import sys
import pytest
from evidence import Store
import reducer_runtime as rt


def command(tmp_path,log):
    script=tmp_path/'job.py'
    script.write_text('from pathlib import Path\nimport sys\np=Path("count");p.write_text(str(int(p.read_text())+1) if p.exists() else "1")\nsys.stdout.buffer.write('+repr(log)+')\nsys.exit(7)\n')
    return [sys.executable,str(script)]


def test_large_known_format_reduced_with_nonzero_status_and_exact_raw(tmp_path):
    store=Store(tmp_path/'store');raw=b'INFO cache populated\n'*2000+b'FAILED test_one - x\n==== 1 failed, 12 passed in 1.00s ====\n'
    result=rt.execute(store,command(tmp_path,raw),tmp_path,'test',format_hint='pytest')
    assert result['mode']=='reduced' and result['visible']['exit_code']==7
    assert store.retrieve(result['command_receipt'])['text'].encode()==raw
    assert (tmp_path/'count').read_text()=='1'


def test_reducer_failure_never_reruns_side_effecting_command(tmp_path,monkeypatch):
    store=Store(tmp_path/'store');raw=b'notice\n'*2000
    monkeypatch.setattr(rt.verification,'verify',lambda *a:(_ for _ in ()).throw(RuntimeError('falsifier')))
    result=rt.execute(store,command(tmp_path,raw),tmp_path,'test',format_hint='pytest')
    assert result['mode']=='native' and result['visible']['stdout']['text'].encode()==raw
    assert result['visible']['exit_code']==7 and 'falsifier' in result['error']
    assert (tmp_path/'count').read_text()=='1'


@pytest.mark.parametrize('enabled,hint,raw,reason',[(False,'pytest',b'x'*3000,'disabled'),
    (True,None,b'x'*3000,'unsupported producer'),(True,'pytest',b'\xff\x00','small output')])
def test_bypass_preserves_all_bytes(tmp_path,enabled,hint,raw,reason):
    result=rt.execute(Store(tmp_path/'store'),command(tmp_path,raw),tmp_path,'test',enabled=enabled,format_hint=hint)
    value=result['visible']['stdout']
    actual=value['text'].encode() if 'text' in value else base64.b64decode(value['base64'])
    assert result['mode']=='native' and result['reason']==reason and actual==raw
    assert (tmp_path/'count').read_text()=='1'


def test_unknown_shell_and_custom_formats_bypass():
    assert rt.choose(['sh','-c','pytest -q']) is None
    assert rt.choose(['pytest','--json-report']) is None
    assert rt.choose(['python3','-m','pytest','-q','tests'])=='pytest'
    assert rt.choose(['clang','-fdiagnostics-format=json','a.c']) is None


def test_invalid_policy_cannot_execute(tmp_path):
    with pytest.raises(ValueError):rt.execute(Store(tmp_path/'store'),command(tmp_path,b'x'),tmp_path,'test',enabled='yes')
    assert not (tmp_path/'count').exists()
