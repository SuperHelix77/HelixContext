"""Audit reported per-call usage and a fixed-prefix intervention bound."""
import argparse,hashlib,json
from pathlib import Path


def audit(root):
 rows=[]
 for label in ['baseline_large','hook_observe_large','hook_compact_replace_large','hook_compact_allow_large','hook_compact_fail_large']:
  p=root/f'events_{label}.jsonl';raw=p.read_bytes();events=[json.loads(l) for l in raw.splitlines()]
  updates=[e['params']['tokenUsage'] for e in events if e.get('method')=='thread/tokenUsage/updated']
  assert len(updates)==2,'This frozen audit expects two reported native calls'
  for k in ['inputTokens','outputTokens','cachedInputTokens','reasoningOutputTokens']:
   assert updates[0]['last'][k]==updates[0]['total'][k]
   assert sum(u['last'][k] for u in updates)==updates[-1]['total'][k]
  first=updates[0]['last'];total=updates[-1]['total']
  rows.append({'arm':label,'trace_sha256':hashlib.sha256(raw).hexdigest(),'reported_calls':[u['last'] for u in updates],'total':total,'fixed_first_call_max_input_saving':1-first['inputTokens']/total['inputTokens'],'fixed_first_call_max_output_saving':1-first['outputTokens']/total['outputTokens']})
 return {'schema':'helix.fixed_prefix_cost_bound.v1','rows':rows,'new_model_calls':0,'assumption':'Candidate leaves first native call and its cost unchanged; every subsequent token is optimistically removed with zero additional overhead.','claim_scope':'Conditional limit for these recorded runs and that restricted intervention class only; not a limit on redesigned first calls or long-horizon Helix.','observability':'Reported per-call usage is verified against totals; context content and precise component attribution remain unobserved.'}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--traces',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 result=audit(a.traces);a.output.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result['rows'][0],indent=2))
