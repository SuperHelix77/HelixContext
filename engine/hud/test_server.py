import hashlib
import json
from pathlib import Path
import threading
from http.server import ThreadingHTTPServer
from urllib.request import urlopen
from urllib.error import HTTPError

import pytest
from server import snapshot,Observer,make_handler,trace_view,engine_view,engine_replays


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


def test_coordinator_usage_never_changes_benchmark_denominators(tmp_path):
    cfg=setup(tmp_path);before,_=snapshot(cfg)
    values={'input_tokens':1000,'cached_input_tokens':900,'cache_write_input_tokens':0,
            'output_tokens':100,'reasoning_output_tokens':50,'total_tokens':1100}
    trace=tmp_path/'coordinator.jsonl'
    trace.write_text(json.dumps({'type':'event_msg','payload':{'type':'token_count',
        'info':{'total_token_usage':values,'last_token_usage':values}}})+'\n')
    cfg['research_usage']=[{'id':'coordinator','name':'Research','path':str(trace)}]
    after,_=snapshot(cfg)
    assert after['pairs']==before['pairs'] and after['observed_totals']==before['observed_totals']
    assert after['research_usage'][0]['usage']['uncached_input_tokens']==100
    assert after['inference_calls_by_hud']==0


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


def test_config_reload_preserves_last_snapshot_on_interrupted_write(tmp_path):
    cfg=setup(tmp_path);path=tmp_path/'config.json';path.write_text(json.dumps(cfg))
    observer=Observer(cfg,tmp_path/'journal.jsonl',path);observer.scan()
    first=observer.current
    path.write_text('{')
    with pytest.raises(ValueError):observer.scan()
    assert observer.current is first and observer.revision==1
    updated={'experiments':[]};path.write_text(json.dumps(updated));observer.scan()
    assert observer.config==updated and observer.current['runs']==[] and observer.revision==2


def test_engine_replay_keeps_zero_inference_separate_and_rejects_tamper(tmp_path):
    raw=b'[]';answer=b'{}';h=hashlib.sha256(raw).hexdigest();case=tmp_path/'selection'
    objects=case/'store/objects';objects.mkdir(parents=True);(objects/h).write_bytes(raw)
    (case/'answer.json').write_bytes(answer)
    report={'classification':'Offline Engine replay, not model parity','rows':[{'case':'selection','source_ref':{'sha256':h,'bytes':len(raw)},'answer_sha256':hashlib.sha256(answer).hexdigest(),'answer_bytes':len(answer),'model_calls':0,'elapsed_seconds':0.1,'checks':{'exact_selection':'PASS'}}]}
    path=tmp_path/'result.json';path.write_text(json.dumps(report))
    config={'engine_replays':[{'id':'r','root':str(tmp_path),'result':'result.json','sha256':hashlib.sha256(path.read_bytes()).hexdigest()}]}
    rows=engine_replays(config);assert rows[0]['model_calls']==0 and rows[0]['state']=='VERIFIED_ARTIFACTS'
    (case/'answer.json').write_bytes(b'changed')
    rows=engine_replays(config);assert rows[0]['model_calls'] is None and rows[0]['state']=='UNVERIFIED'


def test_costs_include_closed_and_failed_verified_usage(tmp_path):
    observer=Observer({'experiments':[]},tmp_path/'journal.jsonl')
    counters={'input_tokens':100,'cached_input_tokens':50,'cache_write_input_tokens':0,'output_tokens':10}
    observer.current={'runs':[{'id':state,'state':state,'model':'luna','usage':counters,
        'usage_source':'Native app-server cumulative update'} for state in ('CLOSED','FAILED')]}
    observer.prices.state=lambda:{'rates':{'luna':{'short':[1,0.1,1,10],'long':[2,0.2,2,20]}}}
    assert set(observer.state()['costs'])=={'CLOSED','FAILED'}
    assert observer.state()['costs']['CLOSED']['short']==pytest.approx(0.000155)


def test_audit_requires_pinned_report_and_bound_native_hash(tmp_path):
    from server import audit_checks
    native='a'*64
    path=tmp_path/'audit.json';path.write_text(json.dumps({'finite_checks':'PASS','rows':[{'native_sha256':native}]}))
    config={'audit_reports':[{'root':str(tmp_path),'path':'audit.json','sha256':hashlib.sha256(path.read_bytes()).hexdigest()}]}
    assert audit_checks(config)=={native:True}
    path.write_text(json.dumps({'finite_checks':'FAIL','rows':[{'native_sha256':native}]}))
    assert audit_checks(config)=={}


def test_replay_authority_mutation_withholds_verified_zero(tmp_path):
    raw=b'[]';answer=b'{}';h=hashlib.sha256(raw).hexdigest();case=tmp_path/'selection'
    objects=case/'store/objects';objects.mkdir(parents=True);(objects/h).write_bytes(raw)
    (case/'answer.json').write_bytes(answer)
    state={'constraints':[]};state_path=case/'task-state.json';state_path.write_text(json.dumps(state))
    state_root=hashlib.sha256(json.dumps(state,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    report={'classification':'Offline only','rows':[{'case':'selection','source_ref':{'sha256':h,'bytes':len(raw)},'answer_sha256':hashlib.sha256(answer).hexdigest(),'answer_bytes':len(answer),'model_calls':0,'elapsed_seconds':0.1,'checks':{},'state_root':state_root,'state_file_sha256':hashlib.sha256(state_path.read_bytes()).hexdigest()}]}
    path=tmp_path/'result.json';path.write_text(json.dumps(report))
    config={'engine_replays':[{'id':'r','root':str(tmp_path),'result':'result.json','sha256':hashlib.sha256(path.read_bytes()).hexdigest()}]}
    assert engine_replays(config)[0]['state']=='VERIFIED_ARTIFACTS'
    state_path.write_text('{"constraints":["changed"]}')
    assert engine_replays(config)[0]['state']=='UNVERIFIED'


def test_engine_model_tokens_need_bound_completed_native_control(tmp_path):
    raw=b'[]';answer=b'{}';h=hashlib.sha256(raw).hexdigest();case=tmp_path/'selection'
    objects=case/'store/objects';objects.mkdir(parents=True);(objects/h).write_bytes(raw)
    (case/'answer.json').write_bytes(answer)
    counters={'input_tokens':100,'output_tokens':20,'cached_input_tokens':40,'reasoning_output_tokens':10,'cache_write_input_tokens':0}
    expected={'run_id':'control','native_sha256':'a'*64,'model':'gpt-5.6-luna','effort':'high','usage':counters}
    report={'classification':'Finite closed request only','rows':[{'case':'selection','source_ref':{'sha256':h,'bytes':2},'answer_sha256':hashlib.sha256(answer).hexdigest(),'answer_bytes':2,'model_calls':0,'elapsed_seconds':0.1,'checks':{'exact':'PASS'},'matched_native_control':expected}]}
    path=tmp_path/'result.json';path.write_text(json.dumps(report))
    cfg={'engine_replays':[{'id':'r','root':str(tmp_path),'result':'result.json','sha256':hashlib.sha256(path.read_bytes()).hexdigest()}]}
    control={'id':'control','native_sha256':'a'*64,'model':'gpt-5.6-luna','effort':'high','usage':counters,'state':'CLOSED','artifact_check':True,'usage_source':'Native app-server cumulative update'}
    result=engine_replays(cfg,[control])[0]
    assert result['model_token_savings_percent']=={'input_tokens':100,'output_tokens':100}
    for change in [{'state':'RUNNING'},{'native_sha256':'b'*64},{'effort':'low'},{'artifact_check':None},{'usage_source':'estimated'},{'usage':{**counters,'input_tokens':101}}]:
        result=engine_replays(cfg,[{**control,**change}])[0]
        assert result['comparison_state']=='UNVERIFIED_COMPARISON' and 'model_token_savings_percent' not in result
    for change in [{'checks':{'exact':'FAIL'}},{'checks':{}},{'checks':None},{'model_calls':False},{'model_calls':1}]:
        altered={**report,'rows':[{**report['rows'][0],**change}]}
        path.write_text(json.dumps(altered))
        cfg['engine_replays'][0]['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        result=engine_replays(cfg,[control])[0]
        assert result['comparison_state']=='UNVERIFIED_COMPARISON' and 'model_token_savings_percent' not in result
    path.write_text(json.dumps(report))
    cfg['engine_replays'][0]['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    (case/'answer.json').write_bytes(b'changed')
    assert engine_replays(cfg,[control])[0]['state']=='UNVERIFIED'


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


def test_native_tool_coverage_detects_missing_command_receipts(tmp_path):
    from server import native_tool_coverage
    path=tmp_path/'wire.jsonl'
    hook={'method':'hook/completed','params':{'threadId':'t','run':{'eventName':'preToolUse','id':'pre-tool-use:0:config:exec-one'}}}
    path.write_text(json.dumps(hook)+'\n'+json.dumps(hook)+'\n')
    value=native_tool_coverage(path,'t')
    assert value['observed_pretool_hooks']==1
    assert value['unmatched_pretool_hooks']==1
    assert value['command_trace_coverage'].startswith('UNKNOWN')
    command={'method':'item/completed','params':{'threadId':'t','item':{'type':'commandExecution','id':'exec-one'}}}
    with path.open('a') as f:f.write(json.dumps(command)+'\n')
    value=native_tool_coverage(path,'t')
    assert value['unmatched_pretool_hooks']==0
    assert 'completeness unproven' in value['command_trace_coverage']
    assert native_tool_coverage(path,'other')['observed_pretool_hooks']==0


def test_native_helix_calls_include_failures_and_deduplicate_delivery(tmp_path):
    from server import native_tool_coverage
    path=tmp_path/'wire.jsonl'
    def item(identity,success):return {'method':'item/completed','params':{'threadId':'t','item':{'type':'dynamicToolCall','tool':'helix_apply_edits','id':identity,'success':success,'contentItems':[{'type':'inputText','text':'actual result'}]}}}
    a=item('exec-a',False);b=item('exec-b',True)
    hook={'method':'hook/completed','params':{'threadId':'t','run':{'eventName':'preToolUse','id':'pre:exec-a'}}}
    path.write_text(''.join(json.dumps(e)+'\n' for e in [hook,a,a,b]))
    row=native_tool_coverage(path,'t')
    assert row['native_helix_tool_calls']==2 and row['native_helix_failed_calls']==1
    assert row['native_helix_result_bytes']==26 and row['unmatched_pretool_hooks']==0
    assert native_tool_coverage(path,'other')['native_helix_tool_calls']==0
    with path.open('a') as f:f.write(json.dumps(item('exec-a',True))+'\n')
    row=native_tool_coverage(path,'t')
    assert row['native_helix_tool_calls'] is None and row['native_helix_failed_calls'] is None
    invalid=item('exec-c',True);invalid['params']['item']['contentItems']=[None]
    path.write_text(json.dumps(invalid)+'\n')
    assert native_tool_coverage(path,'t')['native_helix_result_bytes'] is None


def test_hook_gap_surfaces_as_snapshot_alert(tmp_path):
    cfg=setup(tmp_path);wire=tmp_path/'native.jsonl'
    wire.write_text(json.dumps({'method':'hook/completed','params':{'threadId':'t','run':{'eventName':'preToolUse','id':'pre-tool-use:0:config:exec-missing'}}})+'\n')
    status=json.loads((tmp_path/'on.json').read_text());status.update(thread_id='t',native_events_sha256=hashlib.sha256(wire.read_bytes()).hexdigest());(tmp_path/'on.json').write_text(json.dumps(status))
    cfg['experiments'][0]['runs'][1]['native_events']='native.jsonl'
    data,_=snapshot(cfg)
    assert data['runs'][1]['commands']==0
    assert data['runs'][1]['unmatched_pretool_hooks']==1
    assert any('zero recorded commands' in p['message'] for p in data['problems'])
