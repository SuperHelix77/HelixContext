"""Original frozen failure and post-hoc exact identity adapter recovery, separately."""
import json,sys,time
from pathlib import Path
from native_luna_ack_pair import sha,verify,save,grade,digest
from native_luna_ack_output_v3 import render
from luna_event_id_adapter import resolve,test

def run(root,out):
 root=Path(root);m=json.loads((root/'manifest.json').read_text());verify(m);test()
 p=root/'on/receipts/run';s=json.loads((p/'status.json').read_text());assert s['state']=='closed'
 for f,k in [('events.jsonl','events_sha256'),('native-events.jsonl','native_events_sha256')]:assert sha(p/f)==s[k]
 events=list(map(json.loads,(p/'native-events.jsonl').read_text().splitlines()));steps=[e['params']['tokenUsage']['last'] for e in events if e.get('method')=='thread/tokenUsage/updated'];assert len(steps)==1
 for k,n in [('input_tokens','inputTokens'),('output_tokens','outputTokens'),('cached_input_tokens','cachedInputTokens'),('reasoning_output_tokens','reasoningOutputTokens')]:assert s['usage'][k]==steps[0][n]
 decision=json.loads((p/'turn-1-answer.txt').read_text());raw=(root/'on/history.jsonl').read_bytes();fixture=json.loads((root/'fixture.json').read_text())['events'];history=list(map(json.loads,raw.splitlines()));assert [x['event'] for x in history]==fixture[:49];assert [x['answer'] for x in history]==['ACK E%02d'%i for i in range(1,50)]
 assert list(map(json.loads,(root/'on/received.jsonl').read_text().splitlines()))==fixture
 try:render(decision,raw,digest(raw))
 except ValueError as e:assert str(e)=='invalid policy'
 else:raise AssertionError('original failure not reproduced')
 start=time.perf_counter();normalized=resolve(decision,raw);final=render(normalized,raw,digest(raw));seconds=time.perf_counter()-start;grade(json.dumps(final))
 # Retain original history/failure. Publish recovery separately; no rewritten receipt.
 save(root/'recovered-final.json',final)
 prior=json.loads((Path(m['prior'])/'results.json').read_text());off=prior['rows']['off']['usage'];on=s['usage'];uncached=lambda u:u['input_tokens']-u['cached_input_tokens'];v2=json.loads((root.parent/'native-luna-ack-output-v2-20260909/results.json').read_text())['rows']['on']['usage']
 r={'state':'DEVELOPMENT_RECOVERY_COMPLETE','qualification':'Frozen V3 schema FAIL; subsequent exact-ID adapter recovery PASS on known fixture. Post-hoc development recovery, not original-policy success, independent pair, production admission or80/80.','manifest_sha256':sha(root/'manifest.json'),'rows':{'off':prior['rows']['off'],'on':{'usage':on,'answer':json.dumps(final),'original_semantic_decision':decision,'resolved_decision':normalized}},'savings_percent':{k:100*(1-on[k]/off[k]) for k in ('input_tokens','output_tokens')},'audit':{'original_failure':json.loads((root/'failure.json').read_text()),'raw_native_sha256':s['native_events_sha256'],'native_turns':1,'native_segments':1,'native_hook_events':sum(e.get('method','').startswith('hook/') for e in events),'uncached_input':uncached(on),'recovery_semantic_checks':True,'recovery_seconds':seconds,'recovery_logical_read_bytes':len(raw),'raw_receipt_storage_bytes':sum(f.stat().st_size for f in p.rglob('*') if f.is_file()),'source_history_sha256':digest(raw),'adapter_sha256':sha(Path(__file__).with_name('luna_event_id_adapter.py')),'80_percent_output_budget':off['output_tokens']*.2,'candidate_attempts_total_usage':{k:prior['rows']['on']['usage'][k]+v2[k]+on[k] for k in on},'all_research_usage':{k:off[k]+prior['rows']['on']['usage'][k]+v2[k]+on[k] for k in on}},'limits':['Reused control; two post-result candidate adaptations.','Engine resolves exact identities only; no reinterpretation of source roles, reason or authorization.','Recovery was not pre-registered; original failed trace retained.','Caller full-path metrics were not persisted by failing driver; recovery-only byte/time counts are partial, not total effective-cost accounting.','Reported reasoning tokens are included in output, never discounted; no universal floor or hidden reasoning claims.','Known W50 receipt-only fixture, not broad coding or intelligence/workflow qualification.']}
 r['savings_percent']['uncached_input']=100*(1-uncached(on)/uncached(off));save(root/'recovery-results.json',r);Path(out).write_text(json.dumps(r,indent=2)+'\n');save(root/'on-hud-status.json',{**s,'state':'completed','runner':'app-server','source_status':str(p/'status.json'),'source_status_sha256':sha(p/'status.json'),'qualification':r['qualification']});print(json.dumps({'savings':r['savings_percent'],'audit':r['audit']},indent=2))
if __name__=='__main__':run(*sys.argv[1:])
