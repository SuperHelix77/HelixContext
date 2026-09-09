from pathlib import Path
import json,argparse
from run_benchmark import ROOT,WORKSPACE,load,save
from grade_benchmark import identical,parse_answer

def grade(alias):
 base=WORKSPACE/'outputs/helix-frontier/iteration3'/alias;result={}
 for family in ['L40']:
  result[family]={}
  for condition in ['off','on']:
   p=base/family/condition
   if not (p/'summary.json').exists():result[family][condition]={'status':'pending'};continue
   s=load(p/'summary.json');checks={}
   try:
    if family=='Q2':checks['exact_reasoning_answer']=identical(parse_answer(p/'turn-01/answer.txt'),load(ROOT/'evaluator/reasoning-gold.json'))
    else:
     delay=int(family[1:]);gold=load(ROOT/f'evaluator/latent-v1/delay-{delay}.json');spec=load(ROOT/f'protocol/latent-v1/delay-{delay}.json')
     checks['actual_sequential_turn_count']=s['turns']==delay+1
     integrity=load(p/'integrity.json')
     checks['caller_owned_state_preserved']=len(integrity)==delay+1 and all(x['caller_files_unchanged'] for x in integrity)
     checks['acknowledgements']=all((p/f'turn-{i:02d}/answer.txt').read_text().strip()==f'ACK L{i:02d}' for i in range(1,delay+1))
     checks['late_exact_answer']=identical(parse_answer(p/f'turn-{delay+1:02d}/answer.txt'),gold)
     history=[json.loads(l) for l in (p/'history.jsonl').read_text().splitlines()]
     checks['complete_history']=len(history)==2*(delay+1) and [h['event'] for h in history if h['role']=='user']==spec['events']
     if condition=='on':
      events=[json.loads(l) for l in (p/f'turn-{delay+1:02d}/events.jsonl').read_text().splitlines()]
      checks['actual_cold_retrieval']=any(e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution' and e['item'].get('exit_code')==0 and 'history.jsonl' in e['item'].get('command','') and gold['inventory_tag'] in e['item'].get('aggregated_output','') for e in events)
   except Exception as e:checks['grading_exception']=str(e)
   result[family][condition]={'status':'graded','checks':checks,'passed':bool(checks) and all(v is True for v in checks.values()),'usage':s['usage'],'resources':{k:v for k,v in s.items() if k not in ['usage','status']}}
  if all(result[family][c].get('status')=='graded' for c in ['off','on']):
   off,on=[result[family][c] for c in ['off','on']];result[family]['comparison']={'observed_parity':off['passed'] and on['passed'],'reduction_pct':{k:round(100*(1-on['usage'][k]/off['usage'][k]),3) for k in ['input_tokens','output_tokens']}}
 base.mkdir(parents=True,exist_ok=True);save(base/'latent-grading.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--model',required=True,choices=['luna','sol','astra']);grade(a.parse_args().model)
