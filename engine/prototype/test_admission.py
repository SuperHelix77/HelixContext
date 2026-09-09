import json
import pytest
from admission import Request,decide,dispatch,encode,sha


def fixture(tmp_path):
    evidence={'rows':[{'arm':a,'usage':{'input_tokens':i,'output_tokens':o},'artifact_exact':True,'source_unchanged':True,'passed':True} for a,i,o in [('off',100,100),('on',20,20)]]}
    (tmp_path/'evidence.json').write_bytes(encode(evidence));(tmp_path/'impl.py').write_text('pass\n')
    profile={'model':'test','effort':'high','frozen':True,'evidence':'evidence.json','evidence_sha256':sha(encode(evidence)),'source_hashes':{'impl.py':sha(b'pass\n')}}
    (tmp_path/'profile.json').write_bytes(encode(profile))
    q={'model':'test','effort':'high','contract_hash':'exact','scope':'finite_fixture_only','profile':'profile.json','profile_sha256':sha(encode(profile))}
    return Request('test','high','exact','qualified_fixture_research'),q


def test_production_and_unknown_dispatch_no_preparation_or_reads(tmp_path):
    calls=[];payload=object();request=Request('gpt-6-astra','high','novel-code')
    def native(r,p):assert r is request and p is payload;calls.append('native');return p
    def optimized(*args):raise AssertionError('must not prepare Helix')
    result,d=dispatch(request,payload,native=native,optimized=optimized,repo=tmp_path)
    assert result is payload and calls==['native'] and d['logical_bytes_read']==0 and d['savings_claim'] is None


def test_exact_research_admits_and_failure_does_not_rerun(tmp_path):
    r,q=fixture(tmp_path);calls=[]
    def native(*args):calls.append('native')
    def optimized(*args):calls.append('optimized');raise RuntimeError('after mutation')
    assert decide(r,qualification=q,repo=tmp_path)['route']=='optimized'
    with pytest.raises(RuntimeError):dispatch(r,None,native=native,optimized=optimized,qualification=q,repo=tmp_path)
    assert calls==['optimized']


@pytest.mark.parametrize('field,value',[('model','different'),('effort','low'),('contract_hash','other')])
def test_no_cross_model_effort_or_task_transfer(tmp_path,field,value):
    r,q=fixture(tmp_path);q[field]=value
    d=decide(r,qualification=q,repo=tmp_path)
    assert d['route']=='native' and d['read_operations']==0


def test_stale_source_and_profile_bypass(tmp_path):
    r,q=fixture(tmp_path);(tmp_path/'impl.py').write_text('changed')
    assert decide(r,qualification=q,repo=tmp_path)['route']=='native'
    (tmp_path/'profile.json').write_text('{}')
    assert decide(r,qualification=q,repo=tmp_path)['route']=='native'


def test_no_aggregate_or_cached_token_substitution(tmp_path):
    r,q=fixture(tmp_path);p=json.loads((tmp_path/'profile.json').read_text());e=json.loads((tmp_path/'evidence.json').read_text())
    e['rows'][1]['usage']['output_tokens']=21
    (tmp_path/'evidence.json').write_bytes(encode(e));p['evidence_sha256']=sha(encode(e))
    (tmp_path/'profile.json').write_bytes(encode(p));q['profile_sha256']=sha(encode(p))
    assert decide(r,qualification=q,repo=tmp_path)['route']=='native'


def test_non_object_profile_bypasses_without_crash(tmp_path):
    r,q=fixture(tmp_path);(tmp_path/'profile.json').write_bytes(b'[]');q['profile_sha256']=sha(b'[]')
    assert decide(r,qualification=q,repo=tmp_path)['route']=='native'
