"""Reconcile paired native receipts and independently replay exact staged checks."""
import json,hashlib,subprocess,sys,tempfile,shutil
from pathlib import Path
from prepared_review import validate

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(root,out):
 root=Path(root);result=json.loads((root/'results.json').read_text());assert result['state']=='AWAITING_INDEPENDENT_AUDIT'
 for manifest in (root/'manifest.json',root/'candidate/manifest.json'):
  for p,h in json.loads(manifest.read_text())['sha256'].items():assert sha(p)==h,p
 result['audit']={}
 for arm,rel in [('on','candidate/on'),('off','off')]:
  cwd=root/rel;p=cwd/'receipts/run';s=json.loads((p/'status.json').read_text());assert s['error'] is None
  for f,k in [('events.jsonl','events_sha256'),('native-events.jsonl','native_events_sha256')]:assert sha(p/f)==s[k]
  events=[json.loads(l) for l in (p/'events.jsonl').read_text().splitlines()]
  commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
  assert all(c['exit_code']==0 for c in commands)
  steps=[];previous=None
  for e in map(json.loads,(p/'native-events.jsonl').read_text().splitlines()):
   if e.get('method')=='thread/tokenUsage/updated' and e['params']['threadId']==s['thread_id']:
    u=e['params']['tokenUsage']
    if u['total']!=previous:steps.append(u['last']);previous=u['total']
  for f,k in [('inputTokens','input_tokens'),('outputTokens','output_tokens'),('cachedInputTokens','cached_input_tokens')]:assert sum(t[f] for t in steps)==s['usage'][k]
  a=json.loads(result['rows'][arm]['answer']);assert a['decision']=='ACCEPT' and a['unresolved']==[]
  if arm=='on':
   m=json.loads((root/'candidate/manifest.json').read_text());receipt=validate(cwd/'.prepared',m['receipt_hash']);stages=[Path(c['cwd']) for c in receipt['checks']]
  else:
   stages=list(cwd.glob('.queue-review-*'));assert len(stages)==1
  replay=[]
  for stage in stages:
   for n in ('proposal.py','CONTRACT.md','check.py','check_independence.py','supplemental.py'):assert (stage/n).read_bytes()==(cwd/n).read_bytes()
   assert (stage/'queue_state.py').read_bytes()==(cwd/'proposal.py').read_bytes()
  # Copy one exact reviewed stage: verification does not modify native evidence.
  with tempfile.TemporaryDirectory(prefix='helix-paired-replay-') as t:
   d=Path(t)
   for n in ('proposal.py','queue_state.py','CONTRACT.md','check.py','check_independence.py','supplemental.py'):shutil.copyfile(stages[0]/n,d/n)
   for name in ('check.py','check_independence.py','supplemental.py'):
    q=subprocess.run([sys.executable,'-B',name,'queue_state.py'],cwd=d,capture_output=True,text=True,timeout=30);assert q.returncode==0
    replay.append({'checker':name,'exit':q.returncode,'stdout':q.stdout,'stderr':q.stderr})
  result['audit'][arm]={'segments':steps,'commands':len(commands),'visible_output_bytes':sum(len(c['aggregated_output'].encode()) for c in commands),'uncached_input':s['usage']['input_tokens']-s['usage']['cached_input_tokens'],'elapsed_seconds':s['elapsed_seconds'],'independent_replay':replay,'event_hashes':{k:s[k] for k in ('events_sha256','native_events_sha256')}}
  projection={**s,'state':'completed','runner':'app-server','source_status':str(p/'status.json'),'source_status_sha256':sha(p/'status.json')};(root/(arm+'-hud-status.json')).write_text(json.dumps(projection))
 result['savings_percent']={k:100*(1-result['rows']['on']['usage'][k]/result['rows']['off']['usage'][k]) for k in ('input_tokens','output_tokens')}
 result['savings_percent']['uncached_input']=100*(1-result['audit']['on']['uncached_input']/result['audit']['off']['uncached_input'])
 result['state']='DEVELOPMENT_PAIR_COMPLETE';result['qualification']='Finite checks pass, general intelligence/agentic parity NOT_ESTABLISHED; no promotion'
 Path(out).write_text(json.dumps(result,indent=2)+'\n');(root/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['savings_percent']))
if __name__=='__main__':run(*sys.argv[1:])
