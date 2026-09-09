from pathlib import Path
import argparse,json,subprocess,sys,tempfile
from run_benchmark import ROOT,WORKSPACE,load,save
from grade_benchmark import identical,parse_answer

def grade(alias):
 base=WORKSPACE/'outputs/helix-frontier/iteration2'/alias;result={}
 for task in ['Q3','A2']:
  result[task]={}
  for condition in ['off','on']:
   p=base/task/condition
   if not (p/'summary.json').exists():result[task][condition]={'status':'pending'};continue
   s=load(p/'summary.json');checks={}
   try:
    if task=='Q3':checks['exact_answer']=identical(parse_answer(p/'turn-01/answer.txt'),load(ROOT/'evaluator/Q3-gold.json'))
    else:
     spec=load(ROOT/'iteration2/A2.json');checks['preserved']=all((p/name).read_text()==spec['files'][name] for name in ['settings.json','test_allocation.py'])
     test='''
import random
rng=random.Random(932109)
def ref(n,w):
 if not n:return [0]*len(w)
 s=sum(w);v=[n*x//s for x in w]
 for i in sorted(range(len(w)),key=lambda i:(-(n*w[i]%s),-i))[:n-sum(v)]:v[i]+=1
 return v
for n,w in [(0,[]),(0,[0,0]),(5,[1,1,1]),(9007199254740993,[1,2,3]),(7,[0,2,0,2])]:assert apportion(units=n,weights=w)==ref(n,w)
for _ in range(100):
 w=[rng.randrange(10) for _ in range(rng.randrange(1,15))];n=rng.randrange(10000)
 if not sum(w):w[0]=1
 assert apportion(n,w)==ref(n,w)
for n,w in [(True,[1]),(False,[1]),(-1,[1]),(1.5,[1]),(1,[]),(1,[0,0]),(1,[-1]),(1,[True]),(1,[1.5]),(0,[False]),(0,[-1])]:
 try:apportion(n,w)
 except ValueError:pass
 else:raise AssertionError(('invalid accepted',n,w))
print('116 semantic cases passed')
'''
     with tempfile.TemporaryDirectory() as tmp:
      f=Path(tmp)/'check.py';f.write_text((p/'allocation.py').read_text()+'\n'+test);proc=subprocess.run([sys.executable,'-I','-S',str(f)],capture_output=True,text=True,timeout=20,cwd=tmp)
     checks['semantics']=proc.returncode==0;(p/'semantic-check.txt').write_text(proc.stdout+proc.stderr)
     events=[json.loads(l) for l in (p/'turn-01/events.jsonl').read_text().splitlines()]
     # Test's own completion evidence; do not confuse a later shell failure with test failure.
     checks['existing_suite_executed']=any(e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution' and 'unittest' in e['item'].get('command','') and 'Ran 4 tests' in e['item'].get('aggregated_output','') and '\nOK\n' in e['item'].get('aggregated_output','') for e in events)
   except Exception as e:checks['exception']=str(e)
   result[task][condition]={'status':'graded','passed':bool(checks) and all(v is True for v in checks.values()),'checks':checks,'usage':s['usage'],'resources':{k:v for k,v in s.items() if k not in ['usage','status']}}
  if all(result[task][c].get('status')=='graded' for c in ['off','on']):
   off,on=[result[task][c] for c in ['off','on']];result[task]['comparison']={'observed_parity':off['passed'] and on['passed'],'reduction_pct':{k:round(100*(1-on['usage'][k]/off['usage'][k]),3) for k in ['input_tokens','output_tokens']}}
 base.mkdir(parents=True,exist_ok=True);save(base/'grading.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--model',required=True,choices=['luna','sol','astra']);grade(a.parse_args().model)
