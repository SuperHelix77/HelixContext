"""Local no-inference prompt reconstruction; publish metrics, keep raw text local."""
import concurrent.futures,hashlib,json,subprocess,sys
from pathlib import Path
import tiktoken
CLI='/Applications/ChatGPT.app/Contents/Resources/codex'
ENC=tiktoken.get_encoding('o200k_base')
def metric(s):return {'utf8_bytes':len(s.encode()),'o200k_proxy_tokens':len(ENC.encode(s)),'sha256':hashlib.sha256(s.encode()).hexdigest()}
def run(root,out):
 root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False)
 cat=subprocess.run([CLI,'debug','models'],capture_output=True,text=True,check=True);(root/'catalog.json').write_text(cat.stdout);catalog=json.loads(cat.stdout)['models']
 chosen={m['slug']:m for m in catalog if m['slug'] in ('gpt-5.6-sol','gpt-5.6-luna')};assert len(chosen)==2
 result={'classification':'OBSERVED local renderer/catalog metrics, not native billed-token anatomy','native_calls':0,'models':{},'diagnostics':{},'raw_local_root':str(root)}
 for name,m in chosen.items():
  base=m['base_instructions'];template=m['model_messages'].get('instructions_template','')
  result['models'][name]={'base_instructions':metric(base),'template':metric(template),'base_equals_template':base==template,'metadata':{k:m.get(k) for k in ('tool_mode','shell_type','include_skills_usage_instructions','include_plugin_usage_instructions','include_apps_usage_instructions','default_verbosity','use_responses_lite','node_repl_disabled','experimental_supported_tools')}}
 sol=Path('/Users/mert/Documents/ChatGPT/Helix/research/sol-integrated-v3-20260909');agents=Path('/Users/mert/.codex/AGENTS.md').read_text();skill=Path('/tmp/helix-named-plans-20260909/skills/helixcontext/SKILL.md').read_text()
 tasks={a:(sol/f'{a}-prompt.txt').read_text() for a in ('off','on')}
 result['standalone_controllable']={'global_agents':metric(agents),'helix_skill':metric(skill),'task_off':metric(tasks['off']),'task_on':metric(tasks['on'])}
 def diag(pair):
  model,arm=pair;cwd=sol/'tasks'/arm;assert cwd.is_dir()
  cmd=[CLI,'debug','prompt-input','-c','model='+json.dumps(model),'-c','model_reasoning_effort="high"','-c','skills.max_context_tokens=512','-c','approval_policy="never"','-c','sandbox_mode="workspace-write"',tasks[arm]]
  p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,check=True);name=model+'-'+arm;(root/(name+'.json')).write_text(p.stdout);(root/(name+'.stderr')).write_text(p.stderr);x=json.loads(p.stdout);blocks=[]
  for i,msg in enumerate(x):
   for j,c in enumerate(msg.get('content',[])):
    if c.get('type')=='input_text':
     text=c['text'];blocks.append({'message':i,'part':j,'role':msg['role'],**metric(text),'global_agents_occurrences':text.count(agents),'helix_skill_exact_occurrences':text.count(skill),'task_exact_occurrences':text.count(tasks[arm]),'catalog_base_exact_occurrences':text.count(chosen[model]['base_instructions'])})
  return name,{'cwd':str(cwd),'fresh_reconstruction_no_thread_history':True,'blocks':blocks,'sum_text_proxy_tokens':sum(b['o200k_proxy_tokens'] for b in blocks),'sum_text_bytes':sum(b['utf8_bytes'] for b in blocks),'raw_json_sha256':metric(p.stdout)['sha256']}
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for name,data in pool.map(diag,[(m,a) for m in chosen for a in ('off','on')]):result['diagnostics'][name]=data
 a=chosen['gpt-5.6-sol']['base_instructions'];b=chosen['gpt-5.6-luna']['base_instructions'];result['models_share_exact_base']=a==b
 result['limits']=['Debug input list is not the complete native transmitted request.','Catalog base/template measurements are not proof of their exact serialization or addition to input-list totals.','Explicit app-server skill input cannot be reproduced by this command; standalone skill bytes are not observed attachment cost.','Tool/schema definitions and platform remainder absent from this output remain UNKNOWN.','Same frozen Sol task and task directories used for both model diagnostics, to isolate renderer differences; no fresh execution or Luna transfer claim.','No platform/system instructions modified; raw instruction text stays local.','Proxy tokenizer is o200k_base, not authoritative native token counting.']
 Path(out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'models':result['models'],'models_share_exact_base':result['models_share_exact_base'],'diagnostics':{k:{z:v[z] for z in ('sum_text_proxy_tokens','sum_text_bytes')} for k,v in result['diagnostics'].items()},'standalone':result['standalone_controllable']},indent=2))
if __name__=='__main__':run(*sys.argv[1:])
