import argparse
from run_benchmark import ROOT,WORKSPACE,load,save
from grade_benchmark import identical,parse_answer

def grade(alias):
 base=WORKSPACE/'outputs/helix-frontier/iteration3'/alias/'Q4';res={}
 for c in ['off','on']:
  p=base/c
  if not (p/'summary.json').exists():res[c]={'status':'pending'};continue
  s=load(p/'summary.json');checks={'source_preserved':load(p/'integrity.json')['source_unchanged']}
  try:checks['exact_answer']=identical(parse_answer(p/'turn-01/answer.txt'),load(ROOT/'evaluator/reasoning4-gold.json'))
  except Exception as e:checks['error']=str(e)
  res[c]={'status':'graded','checks':checks,'passed':all(x is True for x in checks.values()),'usage':s['usage']}
 if all(res[c]['status']=='graded' for c in ['off','on']):res['comparison']={'observed_parity':res['off']['passed'] and res['on']['passed'],'reduction_pct':{k:round(100*(1-res['on']['usage'][k]/res['off']['usage'][k]),3) for k in ['input_tokens','output_tokens']}}
 save(base/'grading.json',res);print(res)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--model',required=True);grade(a.parse_args().model)
