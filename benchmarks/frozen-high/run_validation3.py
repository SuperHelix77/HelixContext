"""V3 validation: progressive skill loading, explicit ownership, original-file references.
Q includes an efficient file-reference normal control. A/W reuse frozen same-task
normal control receipts; this is disclosed, not presented as concurrent repetition.
"""
import argparse,json,time,sys,shutil,subprocess
from run_benchmark import ROOT,WORKSPACE,MODELS,common,native,load,save,sha,setup_files
from run_followups import summarize

def prefix(on):
 control=common('off')
 return control.split('Use your normal behavior.')[0]+'Use this experimental Helix Context skill:\n'+(ROOT/'iteration3/SKILL.md').read_text()+'\n' if on else control

def run(alias,task,condition):
 start=time.time();cpu=time.process_time();archive_bytes=0;cwd=ROOT/'validation3-runs'/alias/task/condition;out=WORKSPACE/'outputs/helix-frontier/iteration3'/alias/task/condition;cwd.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
 if task=='Q':
  spec=load(ROOT/'protocol/reasoning-v2.json');raw=json.dumps(spec['records'],indent=2);setup_files(cwd,{'records.json':raw});before=sha((cwd/'records.json').read_bytes())
  metadata={'path':'records.json','format':'original JSON array','bytes':len(raw.encode()),'sha256':before,'fields':list(spec['records'][0]),'role':'complete original source; read/query as needed'}
  native(MODELS[alias],cwd,prefix(condition=='on')+spec['task']+'\nSource metadata (the file is not a compact prompt encoding):\n'+json.dumps(metadata),out/'turn-01')
  save(out/'integrity.json',{'source_unchanged':sha((cwd/'records.json').read_bytes())==before});calls=1
 elif task=='A':
  spec=load(ROOT/'protocol/agentic-v1.json');setup_files(cwd,spec['files']);probe=subprocess.run(['git','rev-parse','--show-toplevel'],cwd=cwd,capture_output=True,text=True)
  prompt=prefix(True)+spec['task']+'\nVerified workspace capabilities: '+json.dumps({'git_repository':probe.returncode==0})+'\nComplete caller-read snapshots:\n'
  for name,text in spec['files'].items():prompt+=f'\n{name} SHA256 {sha(text.encode())}\n{text}'
  native(MODELS[alias],cwd,prompt,out/'turn-01')
  for name in spec['files']:
   if (cwd/name).exists():shutil.copy2(cwd/name,out/name)
  calls=1
 else:
  spec=load(ROOT/'protocol/long-horizon-v1.json');history=[];ledger=[];integrity=[]
  for event in spec['events']:
   t=event['turn'];history.append({'role':'user','event':event});archive=''.join(json.dumps(h,ensure_ascii=False)+'\n' for h in history);(cwd/'history.jsonl').write_text(archive);archive_bytes+=len(archive.encode());(cwd/'ledger.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in ledger));before={n:sha((cwd/n).read_bytes()) for n in ['history.jsonl','ledger.jsonl']}
   state={'logical_task_id':f'W-{alias}-v3','state_owner':'caller','current_event_persisted':True,'history_file':'history.jsonl','ledger_file':'ledger.jsonl','current_turn':t}
   if t<50:state.update(operation='acknowledge_already_persisted_event',requested_acknowledgement=f'ACK E{t:02d}')
   else:state['operation']='answer_current_request_using_recoverable_history'
   prompt=prefix(t==50)+'\nThe caller owns and maintains history.jsonl and ledger.jsonl. Current event persistence is complete. Do not duplicate that work. For a simple acknowledgement, reproduce the requested acknowledgement exactly; no new ledger entry is needed. For a substantive decision, retrieve missing historical evidence before answering.\nState:\n'+json.dumps(state)+'\nCurrent event:\n'+json.dumps(event)
   answer,status=native(MODELS[alias],cwd,prompt,out/f'turn-{t:02d}')
   integrity.append({'turn':t,'caller_files_unchanged':all((cwd/n).exists() and sha((cwd/n).read_bytes())==h for n,h in before.items())})
   history.append({'role':'assistant','turn':t,'answer':answer});ledger.append({'turn':t,'event_ref':event['event_id'],'response_ref':f'history assistant turn {t}'})
   print(alias,'W v3',t,'/50 complete',flush=True)
  (out/'history.jsonl').write_text(''.join(json.dumps(h,ensure_ascii=False)+'\n' for h in history));save(out/'integrity.json',integrity);calls=50
 summarize(out,alias,condition,calls,start,cpu,archive_bytes)
 save(out/'comparison-contract.json',{'task':task,'control':'new ordinary file-reference control' if task=='Q' else 'reused frozen primary off receipt, same model/High/task/source data','condition':'V3 skill plus caller context policy; passive ACK turns use progressive disclosure without loading the skill body','model':MODELS[alias],'effort':'high','no_model_calls_eliminated':True})
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--model',required=True,choices=MODELS);args=a.parse_args()
 for f,h in load(ROOT/'iteration3/validation-manifest.json')['files'].items():assert sha((ROOT/f).read_bytes())==h,('validation drift',f)
 for task in ['Q','A','W']:
  for condition in (['off','on'] if task=='Q' else ['on']):run(args.model,task,condition)
