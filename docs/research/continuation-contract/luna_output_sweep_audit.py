"""Audit authorized V4/V5/V6 attempts against unchanged original control."""
import json,sys
from pathlib import Path
from native_luna_ack_pair import sha,verify,digest,grade,save
from native_luna_ack_output_v3 import render
from luna_event_id_adapter import resolve
from reason_obligation_check import check

def run(base,out):
 base=Path(base);prior=json.loads((base/'native-luna-ack-pair-v1-20260909/results.json').read_text());control=prior['rows']['off']['usage'];rows=[]
 for v in (4,5,6):
  root=base/f'native-luna-ack-output-v{v}-20260909';m=json.loads((root/'manifest.json').read_text());verify(m);r=json.loads((root/'results.json').read_text());assert r['state']=='AWAITING_INDEPENDENT_AUDIT';p=root/'on/receipts/run';s=json.loads((p/'status.json').read_text());assert s['state']=='closed' and s['error'] is None
  for f,k in [('events.jsonl','events_sha256'),('native-events.jsonl','native_events_sha256')]:assert sha(p/f)==s[k]
  native=list(map(json.loads,(p/'native-events.jsonl').read_text().splitlines()));steps=[e['params']['tokenUsage']['last'] for e in native if e.get('method')=='thread/tokenUsage/updated'];assert len(steps)==1
  for k,n in [('input_tokens','inputTokens'),('output_tokens','outputTokens'),('cached_input_tokens','cachedInputTokens'),('reasoning_output_tokens','reasoningOutputTokens')]:assert steps[0][n]==s['usage'][k]
  raw=b''.join((root/'on/history.jsonl').read_bytes().splitlines(keepends=True)[:49]);fixture=json.loads((root/'fixture.json').read_text())['events'];history=list(map(json.loads,raw.splitlines()));assert [x['event'] for x in history]==fixture[:49]
  assert [x['answer'] for x in history]==['ACK E%02d'%i for i in range(1,50)]
  decision=json.loads((root/'decision.json').read_text());actual=(p/'turn-1-answer.txt').read_text().strip()
  if v==4:assert json.loads(actual)==decision
  elif v==5:assert {**json.loads(actual),'authorized':json.loads(actual)['reason']=='AUTHORIZED'}==decision
  else:assert actual==decision['reason']
  final=render(resolve(decision,raw),raw,digest(raw));assert final==json.loads((root/'rendered.json').read_text());grade(json.dumps(final));assert check({'distinct_approvers':1,'approver_group':'violet'},final,decision['reason'])=='PASS'
  inp=json.loads((p/'turn-1-input.json').read_text())['input'][0]['text'];packet=b''.join(l for l in raw.splitlines(keepends=True) if b'ORION-42' in l);assert inp.endswith(packet.decode())
  u=s['usage'];delta={k:100*(1-u[k]/control[k]) for k in ('input_tokens','output_tokens')};delta['uncached_input']=100*(1-(u['input_tokens']-u['cached_input_tokens'])/(control['input_tokens']-control['cached_input_tokens']))
  row={'version':v,'usage':u,'savings_percent':delta,'exact_and_reason_checks':'PASS','native_segments':1,'native_sha256':s['native_events_sha256'],'manifest_sha256':sha(root/'manifest.json'),'caller':r['rows']['on']['caller'],'answer':final};rows.append(row)
  r.update(state='DEVELOPMENT_CANDIDATE_COMPLETE',qualification='Known development fixture PASS; adaptive reused control, general capability and80/80 not established',savings_percent=delta,audit=row);r['rows']['off']=prior['rows']['off'];save(root/'results.json',r);save(root/'on-hud-status.json',{**s,'state':'completed','runner':'app-server','source_status':str(p/'status.json'),'source_status_sha256':sha(p/'status.json')})
 result={'classification':'Three adaptive authorized development candidates; same original control reused','control_usage':control,'rows':rows,'best_output_version':5,'80_output_pass':False,'new_native_calls_by_audit':0,'limits':['No fresh paired replication or capability benchmark.','Subject-text filtering is fixture-specific; general late-relevance/authority coverage unqualified.','Full history remains available; storage is not proof of retrieval under a surprise.','V6 proposal selection before inference adds review work on this run; attribution not causally isolated.','Caller byte/time counters are partial, not complete effective-cost or monetary savings.','All failed and superseded attempts retained; no favorable-only accounting.']}
 Path(out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps([{'v':r['version'],'output':r['usage']['output_tokens'],'savings':r['savings_percent']} for r in rows],indent=2))
if __name__=='__main__':run(*sys.argv[1:])
