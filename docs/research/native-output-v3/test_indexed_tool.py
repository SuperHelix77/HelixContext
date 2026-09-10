import json
import subprocess
import pytest
import indexed_tool as m

BINDING='a'*64


def request(call='c',version=0,insert='new\n',at=1,count=1):
    return {'threadId':'t','turnId':'u','callId':call,'tool':'helix_apply_edits',
            'arguments':{'expected_version':version,'edits':[
                {'start_line':at,'delete_lines':count,'insert':insert}]}}


def setup(tmp_path,checker=None):
    cwd=tmp_path/'workspace';cwd.mkdir();target=cwd/'a.py';target.write_bytes(b'old\n')
    protected=cwd/'protected';protected.write_bytes(b'unchanged');(cwd/'a.py.helix-lock').touch()
    subprocess.run(['git','init','-q'],cwd=cwd,check=True)
    subprocess.run(['git','add','.'],cwd=cwd,check=True)
    subprocess.run(['git','-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','initial'],cwd=cwd,check=True)
    def authority():
        if protected.read_bytes()!=b'unchanged':raise ValueError('protected changed')
        return BINDING
    observed=lambda:m.scope_snapshot(cwd,['a.py','protected'])
    tool=m.IndexedEditTool(tmp_path/'tool',target,b'old\n',authority,checker or (lambda *a:{'checks':'PASS'}),
                          expected_binding=BINDING,scope_observer=observed)
    return tool,observed


def test_exact_application_scope_duplicate_and_restart(tmp_path):
    calls=[];tool,observer=setup(tmp_path,lambda *a:calls.append(1) or {'checks':'PASS'})
    assert observer()['status_z']==''
    reply=tool(request());packet=json.loads(reply['contentItems'][0]['text'])
    assert reply['success'] and tool.target.read_bytes()==b'new\n'
    assert packet['scope']['status_z']==' M a.py\0' and packet['scope']['diff_check_exit']==0
    assert packet['scope']['source_bound'] and 'not' not in packet['review']['exact_diff']
    scope=json.loads(tool.store.get(packet['scope']['evidence_ref']))
    assert len(scope['commands'])==3 and scope['files']['a.py']==packet['source_sha256']
    again=m.IndexedEditTool(tool.directory,tool.target,b'old\n',tool.authority,
        lambda *a:pytest.fail('reran'),expected_binding=BINDING,scope_observer=observer)
    assert again(request())==reply and calls==[1]
    with pytest.raises(ValueError,match='Conflicting'):again(request(insert='foreign\n'))


def test_failed_checker_and_wrong_address_never_publish(tmp_path):
    tool,_=setup(tmp_path,lambda *a:{'checks':'FAIL'})
    assert not tool(request())['success'] and tool.target.read_bytes()==b'old\n'
    assert not tool(request('bad-index',at=4))['success']
    assert not tool(request('stale-version',version=7))['success']


def test_stale_source_rejects_before_checks(tmp_path):
    tool,_=setup(tmp_path,lambda *a:pytest.fail('checked stale input'))
    tool.target.write_bytes(b'foreign\n')
    with pytest.raises(ValueError,match='drift'):tool(request())


def test_scope_observation_failure_recovers_exact_publication_without_retry(tmp_path):
    calls=[];tool,observer=setup(tmp_path,lambda *a:calls.append(1) or {'checks':'PASS'})
    tool.scope_observer=lambda:(_ for _ in ()).throw(OSError('lost observation'))
    with pytest.raises(OSError):tool(request())
    assert tool.target.read_bytes()==b'new\n' and calls==[1]
    with pytest.raises(ValueError,match='Uncertain'):tool(request())
    tool.scope_observer=observer
    from checked_tool import encoded
    reply=tool.recover_published(m.digest(encoded(['t','c'])))
    assert reply['success'] and calls==[1] and tool(request())==reply


def test_protected_change_and_false_scope_cannot_be_certified(tmp_path):
    tool,observer=setup(tmp_path)
    def false_scope():
        observed=observer();observed['files']['a.py']='b'*64;return observed
    tool.scope_observer=false_scope
    with pytest.raises(ValueError,match='Observed scope'):tool(request())
    assert tool.target.read_bytes()==b'new\n'  # Already published; not falsely called success.
    tool.scope_observer=observer;(tool.target.parent/'protected').write_bytes(b'altered')
    from checked_tool import encoded
    with pytest.raises(ValueError,match='protected changed'):
        tool.recover_published(m.digest(encoded(['t','c'])))


def test_semantically_wrong_correct_hash_is_not_a_semantic_certificate(tmp_path):
    tool,_=setup(tmp_path) # Deliberately inadequate checker.
    result=tool(request(insert='wrong_semantics\n'))
    p=json.loads(result['contentItems'][0]['text'])
    assert result['success'] and p['semantic_adequacy']=='Model responsibility'
    assert p['source_sha256']==m.digest(b'wrong_semantics\n')
    assert tool.target.read_bytes()!=b'new\n' # Independent semantic oracle still rejects.


def test_diff_check_failure_is_reported_not_silently_promoted(tmp_path):
    tool,_=setup(tmp_path)
    p=json.loads(tool(request(insert='trailing  \n'))['contentItems'][0]['text'])
    assert p['scope']['diff_check_exit']!=0


@pytest.mark.parametrize('insert',['λ\u2028still_same_line\n','x\ry\n','x\r\ny\r\n','no final newline'])
def test_diff_independently_applies_exact_unicode_crlf_and_eof(tmp_path,insert):
    tool,_=setup(tmp_path)
    p=json.loads(tool(request(insert=insert))['contentItems'][0]['text'])
    other=tmp_path/'diff';other.mkdir();(other/'a.py').write_bytes(b'old\n')
    applied=subprocess.run(['git','apply','--whitespace=nowarn','-'],cwd=other,
        input=p['review']['exact_diff'].encode(),capture_output=True)
    assert applied.returncode==0,(applied.stdout,applied.stderr)
    assert (other/'a.py').read_bytes()==insert.encode()
