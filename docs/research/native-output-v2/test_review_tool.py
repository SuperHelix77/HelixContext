import json
import pytest
from review_tool import ReviewEditTool, exact_diff, digest

BINDING='a'*64
def request(call='c',old='old',new='new'):
    return {'threadId':'t','turnId':'u','callId':call,'tool':'helix_apply_edits',
            'arguments':{'expected_version':0,'edits':[{'old':old,'new':new}]}}


def setup(tmp_path):
    p=tmp_path/'a.py';p.write_bytes(b'old');calls=[]
    t=ReviewEditTool(tmp_path/'tool',p,b'old',lambda:BINDING,lambda *args:calls.append(1) or {'checks':'PASS'},expected_binding=BINDING)
    return t,calls


def test_exact_review_duplicate_and_restart(tmp_path):
    tool,calls=setup(tmp_path);r=tool(request());packet=json.loads(r['contentItems'][0]['text']);view=packet['review']
    assert view['diff_complete'] and view['prior_source_sha256']==digest(b'old')
    assert tool.store.get(view['diff_sha256']).decode()==exact_diff(b'old',b'new','a.py')==view['exact_diff']
    assert '\\ No newline at end of file' in view['exact_diff'] and tool.target.read_bytes()==b'new'
    again=ReviewEditTool(tool.directory,tool.target,b'old',lambda:BINDING,lambda *args:pytest.fail('rerun'),expected_binding=BINDING)
    assert again(request())==r and calls==[1]


def test_large_diff_retained_exactly_and_not_silently_truncated(tmp_path):
    tool,_=setup(tmp_path);r=tool(request(new='x'*5000));v=json.loads(r['contentItems'][0]['text'])['review']
    assert not v['diff_complete'] and v['exact_diff'] is None and v['diff_bytes']>5000
    assert len(tool.store.get(v['diff_sha256']))==v['diff_bytes']


def test_invalid_edit_no_false_review_or_publication(tmp_path):
    tool,calls=setup(tmp_path);r=tool(request(old='wrong'))
    assert not r['success'] and 'review' not in json.loads(r['contentItems'][0]['text'])
    assert not calls and tool.target.read_bytes()==b'old'


def test_diff_integrity_failure_after_publication_can_recover_without_reexecution(tmp_path,monkeypatch):
    tool,calls=setup(tmp_path);original=tool.store.put;failed=[False]
    def fault(raw):
        if raw.startswith(b'--- before/') and not failed[0]:failed[0]=True;raise OSError('Interrupted diff archival')
        return original(raw)
    monkeypatch.setattr(tool.store,'put',fault)
    with pytest.raises(OSError):tool(request())
    assert tool.target.read_bytes()==b'new' and calls==[1]
    from bound_edit_tool import encoded
    result=tool.recover_published(digest(encoded(['t','c'])))
    assert result['success'] and calls==[1] and tool(request())==result
