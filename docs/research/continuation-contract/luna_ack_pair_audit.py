"""Post-run accounting; raw events retained, no hidden-command zero claims."""
import json,sys,time
from pathlib import Path
from native_luna_ack_pair import sha,grade,verify,save

def run(root,out):
 root=Path(root);r=json.loads((root/'results.json').read_text());assert r['state']=='AWAITING_INDEPENDENT_AUDIT';m=json.loads((root/'manifest.json').read_text());verify(m);assert r['manifest_sha256']==sha(root/'manifest.json')
 fixture=json.loads((root/'fixture.json').read_text())['events'];r['audit']={}
 for arm in ('off','on'):
  p=root/arm/'receipts/run';s=json.loads((p/'status.json').read_text());assert s['state']=='closed' and s['error'] is None
  assert s['usage']==r['rows'][arm]['usage']
  for file,key in [('native-events.jsonl','native_events_sha256'),('events.jsonl','events_sha256')]:assert sha(p/file)==s[key]
  native=list(map(json.loads,(p/'native-events.jsonl').read_text().splitlines()));steps=[];last=None
  for e in native:
   if e.get('method')=='thread/tokenUsage/updated':
    assert e['params']['threadId']==s['thread_id'];u=e['params']['tokenUsage']
    if u['total']!=last:steps.append(u['last']);last=u['total']
  for k,n in [('input_tokens','inputTokens'),('output_tokens','outputTokens'),('cached_input_tokens','cachedInputTokens'),('reasoning_output_tokens','reasoningOutputTokens')]:assert sum(x[n] for x in steps)==s['usage'][k]
  assert len(s['turns'])==(50 if arm=='off' else 1)
  received=list(map(json.loads,(root/arm/'received.jsonl').read_text().splitlines()));assert received==fixture
  history=list(map(json.loads,(root/arm/'history.jsonl').read_text().splitlines()));assert [x['event'] for x in history]==fixture
  assert [x['answer'] for x in history[:49]]==['ACK E%02d'%i for i in range(1,50)]
  grade(history[-1]['answer']);assert history[-1]['answer']==r['rows'][arm]['answer']
  if arm=='off':
   for i in range(1,50):assert (p/f'turn-{i}-answer.txt').read_text().strip()==f'ACK E{i:02d}'
  else:
   inp=json.loads((p/'turn-1-input.json').read_text())['input'][0]['text'];recovered=''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n' for x in history[:49]);assert inp.endswith(recovered)
  commands=[e['params']['item'] for e in native if e.get('method')=='item/completed' and e['params']['item']['type']=='commandExecution']
  hooks=[e for e in native if e.get('method')=='hook/completed'];u=s['usage']
  r['audit'][arm]={'native_turns':len(s['turns']),'segments':steps,'recorded_command_items':len(commands),'completed_hooks':len(hooks),'uncached_input':u['input_tokens']-u['cached_input_tokens'],'native_events_sha256':s['native_events_sha256'],'history_sha256':sha(root/arm/'history.jsonl'),'received_sha256':sha(root/arm/'received.jsonl'),'exact_ack_count':49,'history_bytes':(root/arm/'history.jsonl').stat().st_size,'caller_preparation':r['rows'][arm]['caller'],'continuity_store_bytes':sum(x.stat().st_size for x in (root/arm/'.helix').rglob('*') if x.is_file()) if (root/arm/'.helix').exists() else 0,'raw_receipt_storage_bytes':sum(x.stat().st_size for x in p.rglob('*') if x.is_file()),'session_elapsed_seconds':s['elapsed_seconds'],'final_turn_usage':s['turns'][-1]['usage_delta']}
  save(root/f'{arm}-hud-status.json',{**s,'state':'completed','runner':'app-server','source_status':str(p/'status.json'),'source_status_sha256':sha(p/'status.json')})
 r['savings_percent']['uncached_input']=100*(1-r['audit']['on']['uncached_input']/r['audit']['off']['uncached_input'])
 r['qualification']='Known development episode behavior PASS; general intelligence/agentic parity and complete monetary savings NOT_ESTABLISHED.'
 r['limitations']=['Changed old protocol: 49 typed passive native ACK calls replaced with deterministic durable ACKs.','Persistent control avoids deliberate fresh-thread inflation; no matched independent replicate or holdout.','Candidate has two pre-tool hooks despite missing commandExecution items; do not claim zero actual commands or complete execution observability.','Caller logical bytes cover dispatcher and archive path, not OS physical I/O, model tools/hooks/registry or all Python processing.','Setup, audit/development inference cost and storage/CPU pricing not converted to equivalent tokens or silently zeroed.','Passive recognition applies trusted exact request envelope only; general semantic event classification is not implemented.','Append/fsync and reopen were tested; crash-midwrite, concurrent writers and full restart-resume not qualified.']
 r['state']='DEVELOPMENT_PAIR_COMPLETE';save(root/'results.json',r);Path(out).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'savings':r['savings_percent'],'audit':r['audit']},indent=2))
if __name__=='__main__':run(*sys.argv[1:])
