import argparse,json,time
from run_benchmark import ROOT,WORKSPACE,MODELS,native,load,save,sha,setup_files
from run_validation3 import prefix
from run_followups import summarize

def run(alias,condition):
 start=time.time();cpu=time.process_time();cwd=ROOT/'reasoning4-runs'/alias/condition;out=WORKSPACE/'outputs/helix-frontier/iteration3'/alias/'Q4'/condition;cwd.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
 spec=load(ROOT/'iteration3/Q4.json');raw=json.dumps(spec['records'],indent=2);setup_files(cwd,{'records.json':raw});before=sha((cwd/'records.json').read_bytes())
 metadata={'path':'records.json','format':'original JSON array','bytes':len(raw.encode()),'sha256':before,'fields':list(spec['records'][0]),'role':'complete original source; read/query as needed'}
 native(MODELS[alias],cwd,prefix(condition=='on')+spec['task']+'\nSource metadata:\n'+json.dumps(metadata),out/'turn-01')
 save(out/'integrity.json',{'source_unchanged':sha((cwd/'records.json').read_bytes())==before});summarize(out,alias,condition,1,start,cpu,0)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--model',required=True,choices=MODELS);args=a.parse_args()
 for f,h in load(ROOT/'iteration3/reasoning4-manifest.json')['files'].items():assert sha((ROOT/f).read_bytes())==h,('Q4 drift',f)
 for condition in (['on','off'] if args.model=='sol' else ['off','on']):run(args.model,condition)
