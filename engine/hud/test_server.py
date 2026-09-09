import hashlib
import json
from pathlib import Path
import threading
from http.server import ThreadingHTTPServer
from urllib.request import urlopen
from urllib.error import HTTPError

import pytest
from server import snapshot,Observer,make_handler,trace_view,engine_view


def setup(tmp_path):
    rows=[]
    for arm,count in [('off',100),('on',20)]:
        trace=(json.dumps({'type':'turn.completed','usage':{'input_tokens':count,'output_tokens':count}})+'\n').encode()
        (tmp_path/(arm+'.jsonl')).write_bytes(trace)
        digest=hashlib.sha256(trace).hexdigest()
        (tmp_path/(arm+'.json')).write_text(json.dumps({'state':'completed','model':'gpt-5.6-sol',
            'usage':{'input_tokens':count,'output_tokens':count},'events_sha256':digest}))
        rows.append({'arm':arm,'artifact_exact':True,'source_unchanged':True,'events_sha256':digest})
    (tmp_path/'result.json').write_text(json.dumps({'rows':rows}))
    return {'experiments':[{'id':'test','name':'Test','root':str(tmp_path),'classification':'Fixture only',
        'result':'result.json','runs':[{'arm':a,'status':a+'.json','events':a+'.jsonl'} for a in ['off','on']]}]}


def test_exact_pair_and_unknown_optional_categories(tmp_path):
    cfg=setup(tmp_path);data,_=snapshot(cfg)
    assert data['pairs'][0]['savings']=={'input_tokens':80,'output_tokens':80}
    assert data['pairs'][0]['artifact_check'] is True
    assert data['runs'][0]['usage']['reasoning_output_tokens'] is None
    assert data['capability_parity']=='Not established'


def test_partial_missing_and_invalid_tokens_are_not_zero(tmp_path):
    cfg=setup(tmp_path)
    (tmp_path/'on.json').write_text('{')
    data,_=snapshot(cfg)
    assert data['runs'][1]['state']=='UNAVAILABLE'
    assert data['pairs'][0]['savings']['output_tokens'] is None
    (tmp_path/'on.json').write_text(json.dumps({'state':'completed','usage':{'input_tokens':True,'output_tokens':-2}}))
    data,_=snapshot(cfg);assert data['runs'][1]['usage'] is None


def test_stale_report_and_tampered_trace_do_not_keep_pass(tmp_path):
    cfg=setup(tmp_path)
    (tmp_path/'on.jsonl').write_text('{"type":"turn.failed"}\n')
    data,_=snapshot(cfg)
    assert data['pairs'][0]['artifact_check'] is None
    assert data['problems']
    (tmp_path/'on.json').write_text(json.dumps({'state':'running','model':'gpt-5.6-sol','pid':123}))
    data,_=snapshot(cfg)
    assert data['runs'][1]['state']=='RUNNING_UNVERIFIED'
    assert data['runs'][1]['artifact_check'] is None


def test_observer_only_journals_changes(tmp_path):
    cfg=setup(tmp_path);journal=tmp_path/'journal.jsonl';observer=Observer(cfg,journal)
    observer.scan();observer.scan()
    assert observer.revision==1 and len(journal.read_text().splitlines())==1
    (tmp_path/'on.json').write_text('{"state":"failed"}')
    observer.scan();assert observer.revision==2 and len(journal.read_text().splitlines())==2


def test_command_counts_do_not_count_started_twice(tmp_path):
    item={'type':'command_execution','command':'cat engine/evidence.py','aggregated_output':'abc','exit_code':0}
    path=tmp_path/'events.jsonl';path.write_text('\n'.join(json.dumps(e) for e in [
        {'type':'item.started','item':item},{'type':'item.completed','item':item}]))
    result=trace_view(path)
    assert result['commands']==1 and result['recorded_tool_bytes']==3
    assert result['suspected_engine_read_output_bytes']==3
    assert all(e['execution_timestamp'] is None for e in result['timeline'])


def test_http_read_only_and_scoped_receipts(tmp_path):
    cfg=setup(tmp_path);observer=Observer(cfg,tmp_path/'journal.jsonl');observer.scan()
    server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(observer));server.daemon_threads=True
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base='http://127.0.0.1:'+str(server.server_port)
    try:
        assert json.load(urlopen(base+'/api/state'))['schema']=='helix.hud.v1'
        assert json.load(urlopen(base+'/api/receipt?id=test-on'))['usage']['input_tokens']==20
        with urlopen(base+'/api/events',timeout=3) as stream:
            assert json.loads(stream.readline().decode()[6:])['revision']==1
            assert stream.readline()==b'\n'
            (tmp_path/'on.json').write_text('{"state":"failed"}')
            observer.scan()
            assert json.loads(stream.readline().decode()[6:])['revision']==2
        for path in ['/api/receipt?id=../../etc/passwd','/server.py','/../../etc/passwd']:
            with pytest.raises(HTTPError):urlopen(base+path)
    finally:server.shutdown();server.server_close()


def test_engine_events_bind_exact_objects_and_show_switches(tmp_path):
    import hashlib
    (tmp_path/'objects').mkdir()
    def obj(value):
        raw=json.dumps(value).encode();key=hashlib.sha256(raw).hexdigest()
        (tmp_path/'objects'/key).write_bytes(raw);return key
    policy=obj({'policy':{'memory':True,'cold_plans':False}});evidence=obj({'result':'ok'})
    path=tmp_path/'events.jsonl'
    path.write_text(json.dumps({'schema':'helix.engine.event.v1','timestamp':'2026-09-09T00:00:00Z','type':'completion','policy_ref':policy,'evidence_ref':evidence})+'\n')
    result=engine_view(path)
    assert result['engine_event_counts']=={'completion':1}
    assert result['engine_policy']['cold_plans'] is False
    (tmp_path/'objects'/evidence).write_bytes(b'tampered')
    import pytest
    with pytest.raises(ValueError):engine_view(path)


def test_native_usage_uses_last_cumulative_update_not_sum(tmp_path):
    from server import native_cumulative
    path=tmp_path/'native.jsonl'
    def event(n):return {'method':'thread/tokenUsage/updated','params':{'threadId':'T','tokenUsage':{'total':{'inputTokens':n,'outputTokens':10,'cachedInputTokens':0,'reasoningOutputTokens':5}}}}
    path.write_text('\n'.join(json.dumps(event(n)) for n in [100,200])+'\n')
    value,digest=native_cumulative(path,'T')
    assert value['input_tokens']==200
    assert native_cumulative(path,'other')[0] is None
    path.write_text('\n'.join(json.dumps(event(n)) for n in [200,100])+'\n')
    with pytest.raises(ValueError):native_cumulative(path,'T')


@pytest.mark.parametrize('rows',[{'off':{'checks_passed':True}},[None,'invalid',12]])
def test_unrecognized_report_rows_do_not_crash_or_claim_pass(tmp_path,rows):
    cfg=setup(tmp_path)
    (tmp_path/'result.json').write_text(json.dumps({'rows':rows}))
    data,_=snapshot(cfg)
    assert data['pairs'][0]['artifact_check'] is None
    assert data['pairs'][0]['savings']['input_tokens']==80
