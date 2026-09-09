"""Within-thread exact-request opportunity census; necessary, not sufficient gate."""
import collections,hashlib,json,sys
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def run(root,out):
 root=Path(root);streams=[];groups=collections.defaultdict(list);cross=collections.defaultdict(set);errors=[]
 for p in sorted(root.glob('*/**/requests.jsonl')):
  try:
   raw=p.read_bytes();records=[json.loads(l) for l in raw.splitlines()];statuspath=p.with_name('status.json')
   status=json.loads(statuspath.read_text()) if statuspath.exists() else {}
   if str(status.get('state','')).lower() not in ('completed','closed'):
    errors.append({'stream':str(p.relative_to(root)),'reason':'not a terminal completed/closed receipt; excluded'});continue
   binding='unavailable'
   native=p.with_name('native-events.jsonl')
   if status.get('native_events_sha256') and native.exists():
    assert sha(native.read_bytes())==status['native_events_sha256'];binding='raw_native_hash_verified'
   turns=[]
   for n,r in enumerate(records):
    if r.get('method')!='turn/start':continue
    par=r['params'];tid=par.get('threadId')
    if not tid:raise ValueError('missing thread identity')
    # Keep text, attachments and tool output exact. Ignore only transport identity.
    body={k:par[k] for k in ('model','effort','input','toolOutput') if k in par}
    h=sha(json.dumps(body,sort_keys=True,separators=(',',':')).encode())
    entry={'index':len(turns)+1,'signature':h,'kind':'tool_output' if 'toolOutput' in par else 'input','model':par.get('model',status.get('model'))}
    turns.append(entry);groups[(str(p),tid)].append(entry);cross[h].add(tid)
   streams.append({'path':str(p.relative_to(root)),'request_sha256':sha(raw),'status_sha256':sha(statuspath.read_bytes()),'native_binding':binding,'turns':turns})
  except (OSError,ValueError,KeyError,AssertionError) as e:errors.append({'stream':str(p.relative_to(root)),'reason':str(e) or type(e).__name__})
 duplicates=[]
 for (path,tid),turns in groups.items():
  seen={}
  for row in turns:
   if row['signature'] in seen:duplicates.append({'stream':str(Path(path).relative_to(root)),'prior_index':seen[row['signature']],'repeat_index':row['index'],'signature':row['signature']})
   else:seen[row['signature']]=row['index']
 result={'classification':'OBSERVED exact-request necessary-condition census; not complete semantic equivalence search','native_calls':0,'terminal_streams':len(streams),'turn_requests':sum(len(s['turns']) for s in streams),'multi_turn_threads':sum(len(g)>1 for g in groups.values()),'within_thread_exact_repeats':duplicates,'cross_thread_repeated_signatures':sum(len(ids)>1 for ids in cross.values()),'streams':streams,'excluded':errors,'limits':['Only current local research requests.jsonl streams; not all user workflows or old CLI receipts.','Exact request equality is necessary for the narrowly proposed exact-bound reuse, not sufficient: world/history/authority may differ.','Changed text may be semantically equivalent, but safe equivalence is not established by this audit.','Cross-thread benchmark arms and replications are not reusable workload invocations.','Tool-loop model segments are not new user turn requests; redundant internal computation is not measured here.','No raw prompt text is published.']}
 Path(out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('terminal_streams','turn_requests','multi_turn_threads','within_thread_exact_repeats','cross_thread_repeated_signatures','excluded')},indent=2))
if __name__=='__main__':run(*sys.argv[1:])
