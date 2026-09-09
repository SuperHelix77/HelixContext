from pathlib import Path
import argparse,json,re,subprocess,sys,hashlib,tempfile
ROOT=Path(__file__).resolve().parent;WORKSPACE=ROOT.parents[1]
def load(p):return json.loads(p.read_text())
def parse_answer(p):
 s=p.read_text().strip();m=re.fullmatch(r'```(?:json)?\s*([\s\S]*?)\s*```',s)
 return json.loads(m.group(1) if m else s)
def identical(a,b):
 if type(a) is not type(b):return False
 if isinstance(a,dict):return a.keys()==b.keys() and all(identical(a[k],b[k]) for k in a)
 if isinstance(a,list):return len(a)==len(b) and all(identical(x,y) for x,y in zip(a,b))
 return a==b

def grade(alias):
 base=WORKSPACE/'outputs/helix-frontier'/alias;result={}
 for task in ['Q','A','W']:
  result[task]={}
  for condition in ['off','on']:
   p=base/task/condition
   if not (p/'summary.json').exists():result[task][condition]={'status':'pending'};continue
   summary=load(p/'summary.json');checks={}
   try:
    if task=='Q':checks['exact_reasoning_answer']=identical(parse_answer(p/'turn-01/answer.txt'),load(ROOT/'evaluator/reasoning-gold.json'))
    elif task=='A':
     spec=load(ROOT/'protocol/agentic-v1.json')
     checks['unrelated_and_tests_preserved']=all((p/name).exists() and (p/name).read_text()==spec['files'][name] for name in ['settings.json','test_allocation.py'])
     source=(p/'allocation.py').read_text()
     test='''
import random
rng=random.Random(193751)
def ref(total,weights):
 s=sum(weights)
 if not total:return [0]*len(weights)
 base=[total*w//s for w in weights]
 for i in sorted(range(len(weights)),key=lambda i:(-(total*weights[i]%s),i))[:total-sum(base)]:base[i]+=1
 return base
for total,weights in [(0,[]),(0,[0,0]),(5,[1,1,1]),(9007199254740993,[1,2,3]),(7,[0,2,0,2])]:assert allocate(total=total,weights=weights)==ref(total,weights)
for _ in range(100):
 w=[rng.randrange(10) for _ in range(rng.randrange(1,15))];t=rng.randrange(10000)
 if not sum(w):w[0]=1
 assert allocate(t,w)==ref(t,w)
for t,w in [(True,[1]),(False,[1]),(-1,[1]),(1.5,[1]),(1,[]),(1,[0,0]),(1,[-1]),(1,[True]),(1,[1.5]),(0,[False]),(0,[-1])]:
 try:allocate(t,w)
 except ValueError:pass
 else:raise AssertionError(('invalid accepted',t,w))
print('116 semantic cases passed')
'''
     with tempfile.TemporaryDirectory() as tmp:
      f=Path(tmp)/'check.py';f.write_text(source+'\n'+test)
      proc=subprocess.run([sys.executable,'-I','-S',str(f)],capture_output=True,text=True,timeout=20,cwd=tmp)
     checks['allocation_semantics_116_cases']=proc.returncode==0
     (p/'semantic-check.txt').write_text(proc.stdout+proc.stderr)
     events=[json.loads(l) for l in (p/'turn-01/events.jsonl').read_text().splitlines()]
     checks['existing_suite_executed']=any(e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution' and e['item'].get('exit_code')==0 and 'Ran 4 tests' in e['item'].get('aggregated_output','') and 'OK' in e['item'].get('aggregated_output','') for e in events)
    else:
     checks['fifty_native_turns']=summary['turns']==50
     checks['all_acknowledgements']=all((p/f'turn-{i:02d}/answer.txt').read_text().strip()==f'ACK E{i:02d}' for i in range(1,50))
     obj=parse_answer(p/'turn-50/answer.txt');gold=load(ROOT/'evaluator/long-horizon-gold.json')
     checks['final_historical_facts']=all(identical(obj.get(k),v) for k,v in gold.items() if k!='required_evidence_turns')
     checks['evidence_provenance']=isinstance(obj.get('evidence_turns'),list) and all(i in obj['evidence_turns'] for i in gold['required_evidence_turns'])
     checks['explanation_present']=isinstance(obj.get('explanation'),str) and bool(obj['explanation'].strip())
     history=[json.loads(l) for l in (p/'history.jsonl').read_text().splitlines()];spec=load(ROOT/'protocol/long-horizon-v1.json')
     checks['complete_history']=len(history)==100 and [h['event'] for h in history if h['role']=='user']==spec['events']
     if condition=='on':
      events=[json.loads(l) for l in (p/'turn-50/events.jsonl').read_text().splitlines()]
      checks['actual_cold_retrieval']=any(e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution' and e['item'].get('exit_code')==0 and gold['recovery_nonce'] in e['item'].get('aggregated_output','') for e in events)
   except Exception as e:checks['grading_exception']=str(e)
   result[task][condition]={'status':'graded','passed':bool(checks) and all(v is True for v in checks.values()),'checks':checks,'usage':summary['usage'],'turns':summary['turns']}
  if all(result[task][c].get('status')=='graded' for c in ['off','on']):
   a,b=(result[task][c] for c in ['off','on']);result[task]['comparison']={'observed_parity':a['passed'] and b['passed'],'reduction_pct':{k:round(100*(1-b['usage'][k]/a['usage'][k]),3) for k in ['input_tokens','output_tokens']}}
 (base/'grading.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--model',required=True,choices=['luna','sol','astra']);grade(a.parse_args().model)
