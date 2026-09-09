"""Preserve the failed one-segment output rescue; never repair its answer in audit."""
import json,sys
from pathlib import Path
from native_luna_ack_pair import sha,verify,save,grade
from native_luna_ack_output import render

def run(root,out):
 root=Path(root);m=json.loads((root/'manifest.json').read_text());verify(m)
 r=json.loads((root/'results.json').read_text());assert r['state']=='AWAITING_INDEPENDENT_AUDIT'
 p=root/'on/receipts/run';s=json.loads((p/'status.json').read_text());assert s['state']=='closed' and s['usage']==r['rows']['on']['usage']
 for file,key in [('events.jsonl','events_sha256'),('native-events.jsonl','native_events_sha256')]:assert sha(p/file)==s[key]
 es=list(map(json.loads,(p/'native-events.jsonl').read_text().splitlines()));us=[e['params']['tokenUsage']['last'] for e in es if e.get('method')=='thread/tokenUsage/updated'];assert len(us)==1
 for native,field in [('inputTokens','input_tokens'),('outputTokens','output_tokens'),('cachedInputTokens','cached_input_tokens'),('reasoningOutputTokens','reasoning_output_tokens')]:assert us[0][native]==s['usage'][field]
 assert not any(e.get('method','').startswith('hook/') for e in es)
 decision=json.loads((root/'decision.json').read_text());assert json.loads((p/'turn-1-answer.txt').read_text())==decision
 hist=(root/'on/history.jsonl').read_bytes().splitlines(keepends=True);raw=b''.join(hist[:49]);assert len(hist)==50
 from native_luna_ack_pair import digest
 rendered=render(decision,raw,digest(raw));assert rendered==json.loads((root/'rendered.json').read_text())
 try:grade(json.dumps(rendered))
 except AssertionError:pass
 else:raise AssertionError('Expected authoritative field failure absent')
 prior=json.loads((Path(m['prior'])/'results.json').read_text());off=prior['rows']['off']['usage'];on=s['usage'];uncached=lambda u:u['input_tokens']-u['cached_input_tokens']
 r['rows']['off']=prior['rows']['off'];r['savings_percent']={k:100*(1-on[k]/off[k]) for k in ('input_tokens','output_tokens')};r['savings_percent']['uncached_input']=100*(1-uncached(on)/uncached(off))
 r['state']='DEVELOPMENT_CANDIDATE_REJECTED';r['qualification']='SEMANTIC_OUTPUT_FAIL: renderer follows selected reverse precedence; required violet becomes amber. No promotion; savings are costs of a failing candidate.'
 r['audit']={'native_segments':1,'native_turns':1,'hook_events':0,'uncached_input':uncached(on),'semantic_check_pass':False,'wrong_field':'approver_group','expected':'violet','actual':rendered['approver_group'],'source_selection':decision['sources'],'raw_native_events_sha256':s['native_events_sha256'],'single_segment_reasoning_output':on['reasoning_output_tokens'],'80_percent_output_budget':off['output_tokens']*.2,'elapsed_seconds':s['elapsed_seconds'],'raw_receipt_storage_bytes':sum(f.stat().st_size for f in p.rglob('*') if f.is_file()),'candidate_attempts_total_usage':{k:prior['rows']['on']['usage'][k]+on[k] for k in on},'all_experiment_usage':{k:off[k]+prior['rows']['on']['usage'][k]+on[k] for k in on}}
 r['limits']=['Adaptive follow-up reuses native control; not fresh paired causal ablation.','Model final explanation semantically correct but selected source order violates declared overlay contract.','No retroactive sorting, no repaired success claim.','Reasoning count is observable; hidden reasoning contents or universal floor are not inferred.','Caller archive counters do not cover complete OS I/O, hooks, indexing, audit/development or dollar cost.']
 save(root/'results.json',r);Path(out).write_text(json.dumps(r,indent=2)+'\n');save(root/'on-hud-status.json',{**s,'state':'completed','runner':'app-server','source_status':str(p/'status.json'),'source_status_sha256':sha(p/'status.json'),'qualification':r['qualification']});print(json.dumps({'savings':r['savings_percent'],'audit':r['audit']},indent=2))
if __name__=='__main__':run(*sys.argv[1:])
