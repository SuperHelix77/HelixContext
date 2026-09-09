import argparse,json,time
from run_benchmark import ROOT,WORKSPACE,MODELS,common,native,save,load,sha
from run_followups import summarize

def run(alias,condition):
 start=time.time();cpu=time.process_time();cwd=ROOT/'iteration3-runs'/alias/'probe'/condition;out=WORKSPACE/'outputs/helix-frontier/iteration3'/alias/'probe'/condition;cwd.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
 prefix=common('off')
 if condition=='on':prefix=prefix.split('Use your normal behavior.')[0]+'Use this experimental Helix Context skill:\n'+(ROOT/'iteration3/SKILL.md').read_text()+'\n'
 history=[];ledger=[];archive_bytes=0;checks=[]
 for event in load(ROOT/'iteration3/probe.json')['events']:
  t=event['turn'];history.append({'role':'user','event':event});archive=''.join(json.dumps(h)+'\n' for h in history);(cwd/'history.jsonl').write_text(archive);archive_bytes+=len(archive.encode());(cwd/'ledger.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in ledger));before={n:sha((cwd/n).read_bytes()) for n in ['history.jsonl','ledger.jsonl']}
  ownership={'logical_task_id':f'probe3-{alias}-{condition}','state_owner':'caller','current_event_persisted':True,'operation':'acknowledge_already_persisted_event','history_file':'history.jsonl','ledger_file':'ledger.jsonl'}
  context='\nState ownership:\n'+json.dumps(ownership)+'\n'
  context+=('Complete history:\n'+archive) if condition=='off' else ('Current event:\n'+json.dumps(event))
  answer,status=native(MODELS[alias],cwd,prefix+context,out/f'turn-{t:02d}')
  checks.append({'turn':t,'exact_ack':answer.strip()==f'ACK P{t:02d}','caller_files_unchanged':all((cwd/n).exists() and sha((cwd/n).read_bytes())==h for n,h in before.items())})
  history.append({'role':'assistant','turn':t,'answer':answer});ledger.append({'turn':t,'event_ref':event['event_id'],'response_ref':f'history assistant {t}'})
  print(alias,condition,t,'/5 complete',flush=True)
 summarize(out,alias,condition,5,start,cpu,archive_bytes);save(out/'checks.json',checks)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--model',required=True,choices=MODELS);args=a.parse_args()
 for f,h in load(ROOT/'iteration3/manifest.json')['files'].items():assert sha((ROOT/f).read_bytes())==h,('probe drift',f)
 for condition in (['on','off'] if args.model=='sol' else ['off','on']):run(args.model,condition)
