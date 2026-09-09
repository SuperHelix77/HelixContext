import hashlib
import json
import pytest
import delivery


def args():
    stdout=b'PASS 2745 sequences / 8282 transitions\n';stderr=b''
    return dict(before=b'x=1\n',after=b'x=2\n',assessment='Reason supplied by the model.',unresolved=[],
        grade={'exit_code':0,'stdout_sha256':hashlib.sha256(stdout).hexdigest(),'stderr_sha256':hashlib.sha256(stderr).hexdigest()},stdout=stdout,stderr=stderr)


def test_preserves_assessment_exact_diff_and_execution_receipt(tmp_path):
    a=args();p=tmp_path/'delivery.json';r=delivery.publish(p,**a);d=json.loads(p.read_text())
    assert d['assessment']==a['assessment'] and '-x=1\n+x=2\n' in d['diff']
    assert d['artifact_sha256']==hashlib.sha256(a['after']).hexdigest()
    assert r['bytes']==len(p.read_bytes()) and r['inference_calls']==0
    with pytest.raises(ValueError):delivery.publish(p,**a)


@pytest.mark.parametrize('failure',['exit','incomplete','tamper','unresolved','no_assessment'])
def test_never_publishes_success_for_failed_or_unresolved_work(tmp_path,failure):
    a=args()
    if failure=='exit':a['grade']['exit_code']=1
    if failure=='incomplete':a['stdout']=b''
    if failure=='tamper':a['grade']['stdout_sha256']='0'*64
    if failure=='unresolved':a['unresolved']=['Alias semantics unclear']
    if failure=='no_assessment':a['assessment']=''
    p=tmp_path/'delivery.json'
    with pytest.raises(ValueError):delivery.publish(p,**a)
    assert not p.exists()
