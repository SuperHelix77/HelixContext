"""Reconcile old W50/L40 evidence; do not promote it to current-release parity."""
import hashlib,json,sys
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(repo,rawroot,out):
 repo=Path(repo);rawroot=Path(rawroot)
 path=repo/'results/frontier-native-usage.json';receipts=json.loads(path.read_text())['receipts'];frontier=json.loads((repo/'results/frontier-v3.json').read_text());result={'classification':'Historical release receipt reconciliation; conditional call-elimination sensitivity is NOT a new benchmark','source_sha256':{'native_receipts':sha(path),'frontier':sha(repo/'results/frontier-v3.json')},'cells':{},'verified_raw_receipts':0,'verified_passive_answers':0,'native_calls_launched':0}
 for model in ('luna','sol','astra'):
  for task,short,n in [('W50','W',50),('L40','L40',41)]:
   arms={}
   for arm in ('off','on'):
    prefix=(f'{model}/W/off/' if task=='W50' and arm=='off' else f'iteration3/{model}/{short}/{arm}/')
    rr=sorted([r for r in receipts if r['path'].startswith(prefix)],key=lambda r:r['path']);assert len(rr)==n
    expected=[f'{prefix}turn-{i:02d}/status.json' for i in range(1,n+1)];assert [r['path'] for r in rr]==expected
    for turn,r in enumerate(rr,1):
     p=rawroot/r['path'];s=json.loads(p.read_text());assert s['state']=='completed' and s['exit_code']==0
     for k in ('input_tokens','output_tokens','cached_input_tokens','reasoning_output_tokens'):assert s['usage'][k]==r['usage'][k]
     assert sha(p.parent/'events.jsonl')==r['original_events_sha256']==s['events_sha256'];result['verified_raw_receipts']+=1
     if turn<n:
      expected_ack=f'ACK {"E" if task=="W50" else "L"}{turn:02d}'
      assert (p.parent/'answer.txt').read_text().strip()==expected_ack,(r['path'],'ACK mismatch');result['verified_passive_answers']+=1
    totals={k:sum(r['usage'][k] for r in rr) for k in ('input_tokens','output_tokens','cached_input_tokens','reasoning_output_tokens')}
    assert totals==frontier['models'][model]['tasks'][task][arm]['usage']
    final=rr[-1]['usage'];arms[arm]={'turns':n,'total':totals,'passive':{k:totals[k]-final[k] for k in totals},'final_semantic':{k:final[k] for k in totals},'raw_final_events_sha256':rr[-1]['original_events_sha256'],'historical_grade_pass':frontier['models'][model]['tasks'][task][arm]['passed']}
   off=arms['off']['total'];on=arms['on']['total'];last=arms['on']['final_semantic']
   result['cells'][model+'/'+task]={'arms':arms,'observed_savings_percent':{k:100*(1-on[k]/off[k]) for k in ('input_tokens','output_tokens')},'conditional_final_only_savings_percent':{k:100*(1-last[k]/off[k]) for k in ('input_tokens','output_tokens')},'final_only_clears_80_both':all(last[k]*5<=off[k] for k in ('input_tokens','output_tokens'))}
 result['limits']=['Original episodes use fresh CLI invocation per event, not persistent-session compaction.','Final historical grades reconciled, not independently rerun here.','Final-only arithmetic deletes required native ACK calls and assumes final behavior/cost unchanged; original no-call-elimination contract would change.','Caller persistence/retrieval/creation/recovery cost cannot be assigned zero.','No assertion current release inherits prior finite parity.','Known fixtures and answers are development evidence, not fresh holdout.']
 Path(out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'verified_raw_receipts':result['verified_raw_receipts'],'verified_passive_answers':result['verified_passive_answers'],'cells':{k:{'observed':v['observed_savings_percent'],'conditional':v['conditional_final_only_savings_percent']} for k,v in result['cells'].items()}},indent=2))
if __name__=='__main__':run(*sys.argv[1:])
