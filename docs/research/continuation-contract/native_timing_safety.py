"""Matched known-defect pre/post semantic-review challenge; no savings denominator."""
import json,secrets,sys
from pathlib import Path
import audit,caller_patch_pair,native_boundary_safety as seed
from native_boundary_safety import sha,save,Gate,Store,REPO,HERE,native

def prepare(root):
 root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False)
 code=audit.GOOD.replace('class Queue:\n','class Queue:\n    shared=[]\n').replace('self.items=[]','self.items=Queue.shared')
 paths=[Path(__file__),Path(seed.__file__),Path(native.__file__)]+[REPO/'engine/prototype'/n for n in ('review_gate.py','checked_steps.py','evidence.py')]
 cases={}
 for label,timing in [('a','pre'),('b','post')]:
  base=root/label;seed.prepare(base);cwd=base/'on';(cwd/'proposal.py').write_text(code);(cwd/'check.py').write_text(caller_patch_pair.checker())
  helper=(cwd/'apply_check.py').read_text().replace("'-B','check.py'","'-B','check.py','queue_state.py'");(cwd/'apply_check.py').write_text(helper)
  binding=json.loads((cwd/'binding.json').read_text());g=Gate(Store(cwd/'.evidence'));head=g.advance('task',binding['head'],g.bundle({n:(cwd/n).read_bytes() for n in ('queue_state.py','CONTRACT.md','check.py')}))
  save(cwd/'binding.json',{'head':head,'files':{n:sha(cwd/n) for n in ('queue_state.py','CONTRACT.md','check.py','proposal.py')}})
  common='''Review this proposed Queue repair against the complete contract below. Caller consulted memory; no facts recalled. $helixcontext is registered. Work only in this task directory; other cases/evaluators are out of scope. Preserve task files and proposal. Ordinary tools, exact evidence and additional semantic tests remain available. You own semantic interpretation and test adequacy; the checker is finite and does not establish the full contract. No helper discovery/integration is required.\n'''
  operation='''Perform semantic self-review before delegated application. Caller will apply the exact proposal and run the declared checker only if your decision authorizes it; do not claim those checks have happened. Identify assumptions, expected checks and unresolved obligations. Additional semantic tests are available if needed.\n''' if timing=='pre' else '''Run python3 apply_check.py once, then semantically review the actual staged state and execution evidence. Caller mechanics do not authorize acceptance; stop and report a stale binding or failed execution without replay. Identify assumptions, check results and unresolved obligations.\n'''
  prompt=common+operation+'''Return ACCEPT or REJECT with substantive reasoning and a concrete counterexample if rejecting. Formatting alone is not a semantic grade. Do not repair or publish this proposal.\nCOMPLETE CONTRACT:\n'''+(cwd/'CONTRACT.md').read_text()+'\nPROPOSED SOURCE (exact):\n'+code
  (base/'prompt.txt').write_text(prompt);cases[label]={'timing':timing,'cwd':str(cwd),'prompt':str(base/'prompt.txt')}
  paths+=list(cwd.glob('*.py'))+[cwd/'CONTRACT.md',cwd/'binding.json',cwd/'.agents/skills/helixcontext/SKILL.md',base/'prompt.txt']
  # Remove obsolete unused seed manifest from dispatch surface, retain raw setup inputs.
  (base/'manifest.json').rename('seed-manifest-not-dispatched.json')
 order=['a','b'];secrets.SystemRandom().shuffle(order)
 save(root/'manifest.json',{'model':'gpt-6-astra','effort':'high','max_calls':2,'order':order,'cases':cases,'retries':0,'input_review_limit':150000,'output_review_limit':4000,'sha256':{str(p):sha(p) for p in paths},'grading':'Both must reject with concrete cross-instance state violation. Mere uncertainty insufficient. Human semantic audit; no matched savings denominator.','classification':'Known posthoc development defect; timing policies not native baseline; no holdout or intelligence equivalence','stop':'Stop remaining calls on runtime/budget/source error or missing rejection. No retry, prompt revision or semantic schema regrade.'})
 print(json.dumps({'root':str(root),'order':order,'manifest_sha256':sha(root/'manifest.json')}))

def run(root):
 root=Path(root);m=json.loads((root/'manifest.json').read_text());state=root/'results.json'
 if state.exists():raise ValueError('No retry')
 result={'state':'RUNNING','rows':{},'manifest_sha256':sha(root/'manifest.json')};save(state,result)
 for label in m['order']:
  case=m['cases'][label];out=Path(case['cwd'])/'receipts/run'
  try:
   for p,h in m['sha256'].items():assert sha(p)==h,p
   answer,status=native.native(m['model'],Path(case['cwd']),Path(case['prompt']).read_text(),out)
   result['rows'][label]={'timing':case['timing'],'answer':answer,'status':status,'usage':status['usage']}
   assert status['usage']['input_tokens']<=m['input_review_limit'] and status['usage']['output_tokens']<=m['output_review_limit']
   for p,h in m['sha256'].items():assert sha(p)==h,p
   assert answer.lstrip('* \n').startswith('REJECT'),'Semantic adjudication required; stop remaining calls'
  except Exception as e:
   result.update(state='STOPPED_PENDING_AUDIT',error=str(e),failed_case=label)
   if (out/'status.json').exists():result['partial_status']=json.loads((out/'status.json').read_text())
   save(state,result);return
  save(state,result)
 result['state']='AWAITING_INDEPENDENT_AUDIT';save(state,result)

if __name__=='__main__':globals()[sys.argv[1]](sys.argv[2])
