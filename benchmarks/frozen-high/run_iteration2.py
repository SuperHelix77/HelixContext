from pathlib import Path
import argparse,json,sys,subprocess,time,shutil
from run_benchmark import ROOT,WORKSPACE,MODELS,common,native,load,save,sha,setup_files
from run_followups import summarize

def run(alias,task,condition):
 start=time.time();cpu=time.process_time();d=ROOT/'iteration2';spec=load(d/f'{task}.json')
 cwd=ROOT/'iteration2-runs'/alias/task/condition;out=WORKSPACE/'outputs/helix-frontier/iteration2'/alias/task/condition;cwd.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
 prefix=common('off')
 if condition=='on':prefix=prefix.split('Use your normal behavior.')[0]+'Use this experimental Helix Context skill:\n'+(d/'SKILL.md').read_text()+'\n'
 prompt=prefix+spec['task']
 if task=='Q3':
  raw=json.dumps(spec['records'],indent=2);setup_files(cwd,{'records.json':raw})
  if condition=='off':evidence=raw
  else:
   sys.path.insert(0,str(WORKSPACE/'work/astra-80'));from preflight import representations
   import tiktoken
   enc=tiktoken.get_encoding('o200k_base');_,note,body=min(representations(raw,True),key=lambda r:len(enc.encode(r[1]+r[2])));evidence='records.json remains the original ordinary JSON array. The representation below is only a compact prompt view; tools should read the original file directly, without reimplementing this representation decoder.\n'+note+'\n'+body
  prompt+='\nComplete records evidence:\n'+evidence
 else:
  setup_files(cwd,spec['files'])
  if condition=='on':
   probe=subprocess.run(['git','rev-parse','--show-toplevel'],cwd=cwd,capture_output=True,text=True)
   prompt+='\nVerified workspace capabilities: '+json.dumps({'git_repository':probe.returncode==0})+'\nCaller-read complete source snapshots; preserve unrelated files and reretrieve if state changes:\n'
   for name,text in spec['files'].items():prompt+=f'\n{name} SHA256 {sha(text.encode())}\n{text}'
 native(MODELS[alias],cwd,prompt,out/'turn-01')
 if task=='A2':
  for name in spec['files']:
   if (cwd/name).exists():shutil.copy2(cwd/name,out/name)
 summarize(out,alias,condition,1,start,cpu,0)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--model',choices=MODELS,required=True);args=a.parse_args()
 for f,h in load(ROOT/'iteration2/manifest.json')['files'].items():assert sha((ROOT/f).read_bytes())==h,('iteration2 drift',f)
 for task in ['Q3','A2']:
  for condition in (['on','off'] if args.model=='sol' else ['off','on']):run(args.model,task,condition)
