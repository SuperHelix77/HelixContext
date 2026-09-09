"""Fresh valid native-versus-prereview pair. Research only, no policy activation."""
import json,secrets,sys,time
from pathlib import Path
import audit,caller_patch_pair
from native_boundary_safety import sha,save,Gate,Store,REPO,HERE
sys.path.insert(0,str(REPO/'engine/output'));from research_session import Session


def prepare(root):
 start=time.perf_counter();root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False)
 files={'proposal.py':audit.GOOD,'queue_state.py':'class Queue: pass\n','CONTRACT.md':(HERE/'CONTRACT.md').read_text(),'check.py':caller_patch_pair.checker(),'check_independence.py':(HERE/'check_queue_independence_v1.py').read_text()}
 for arm in ('off','on'):
  cwd=root/arm;cwd.mkdir()
  for n,s in files.items():(cwd/n).write_text(s)
  skill=cwd/'.agents/skills/helixcontext/SKILL.md';skill.parent.mkdir(parents=True);skill.write_bytes((REPO/'skills/helixcontext/SKILL.md').read_bytes())
  common='''Review the proposed Queue module against the complete contract below. Caller consulted memory; no task facts recalled. Work only in this task directory; other runs/evaluators are out of scope. Preserve proposal.py, base queue_state.py, contract and checker files. Ordinary tools, exact files and additional semantic tests remain available. You own semantic interpretation, check adequacy and unresolved obligations. Batch commands whenever useful. Both declared checks are required: python3 check.py queue_state.py and python3 check_independence.py queue_state.py. Their finite coverage is not proof of universal correctness.\n'''
  operation='''$helixcontext is caller-registered. Perform semantic self-review before delegated application. Caller owns copying the exact proposal to an isolated snapshot and running both declared checks. ACCEPT with no unresolved obligations authorizes this exact mechanical operation and predicts both checks will exit zero under the unchanged bound state. No Engine discovery or integration is required. Do not claim checks have already run. If execution reports a changed state or unexpected result later, reconsider your earlier decision; return REJECT with explanation or REVISE with complete corrected source plus assessment and unresolved obligations. Additional semantic tests remain available before your decision.\n''' if arm=='on' else '''Using ordinary tools, stage the contract and both checkers in a private review directory and copy proposal.py there as queue_state.py. Run both declared checks there. Perform semantic review of the resulting state and actual results. Do not publish to the original base module.\n'''
  prompt=common+operation+'''Return JSON with decision (ACCEPT or REJECT), assessment (substantive reasoning, assumptions, verification or expected checks, and limits), and unresolved (array of strings). Empty unresolved means no identified open obligation, not universal proof. No separate report file is required.\nCOMPLETE CONTRACT:\n'''+files['CONTRACT.md']+'\nPROPOSED MODULE (exact):\n'+files['proposal.py']
  (root/(arm+'-prompt.txt')).write_text(prompt)
 g=Gate(Store(root/'store'));head=g.initialize('task',g.bundle({n:s.encode() for n,s in files.items() if n!='proposal.py'}));save(root/'head.json',head)
 paths=[Path(__file__),REPO/'engine/output/research_session.py',REPO/'engine/output/app_server_native.py']+[REPO/'engine/prototype'/n for n in ('review_gate.py','evidence.py','checked_steps.py')]+[root/'head.json']
 for arm in ('off','on'):paths+=list((root/arm).glob('*.py'))+[root/arm/'CONTRACT.md',root/arm/'.agents/skills/helixcontext/SKILL.md',root/(arm+'-prompt.txt')]
 order=['on','off'];secrets.SystemRandom().shuffle(order)
 save(root/'manifest.json',{'model':'gpt-6-astra','effort':'high','order':order,'max_initial_turns':2,'max_candidate_recovery_turns':1,'retries':0,'per_turn_input_review_limit':150000,'per_turn_output_review_limit':4000,'sha256':{str(p):sha(p) for p in paths},'prepare_seconds':time.perf_counter()-start,'classification':'Known valid supplied-proposal development pair, not autonomous repair or general parity','grading':'Substantive acceptance, exact staged artifacts, unchanged inputs, both checkers pass, count any recovery. Human semantic audit required.','stop':'Runtime/threshold/source/semantic failure stops remaining initial calls. A candidate check failure receives one same-thread recovery turn then stops; no silent retry.'})
 print(json.dumps({'order':order,'manifest_sha256':sha(root/'manifest.json')}))


def parse(text):
 text=text.strip()
 if text.startswith('```'):text='\n'.join(text.splitlines()[1:-1])
 return json.loads(text)


def run(root):
 root=Path(root);m=json.loads((root/'manifest.json').read_text());state=root/'results.json'
 if state.exists():raise ValueError('No retry')
 result={'state':'RUNNING','rows':{},'manifest_sha256':sha(root/'manifest.json')};save(state,result)
 for arm in m['order']:
  out=root/arm/'receipts/run'
  try:
   for p,h in m['sha256'].items():assert sha(p)==h,p
   skill=root/arm/'.agents/skills/helixcontext/SKILL.md' if arm=='on' else None
   with Session(m['model'],root/arm,out,skill) as session:
    answer,receipt=session.turn((root/(arm+'-prompt.txt')).read_text());row={'answer':answer,'turns':[receipt],'usage':dict(session.total)};result['rows'][arm]=row;save(state,result)
    assert receipt['usage_delta']['input_tokens']<=m['per_turn_input_review_limit'] and receipt['usage_delta']['output_tokens']<=m['per_turn_output_review_limit']
    response=parse(answer);assert response['decision']=='ACCEPT' and isinstance(response['assessment'],str) and response['assessment'] and response['unresolved']==[]
    for p,h in m['sha256'].items():assert sha(p)==h,p
    if arm=='on':
     g=Gate(Store(root/'store'));head=json.loads((root/'head.json').read_text());start=time.perf_counter()
     attempt=g.stage('candidate','task',head,{'queue_state.py':(root/arm/'proposal.py').read_bytes()},steps=[{'name':'contract','argv':[sys.executable,'-B','check.py','queue_state.py']},{'name':'independence','argv':[sys.executable,'-B','check_independence.py','queue_state.py']}],environment_id='bounded-native-review',env={},timeout=30)
     row.update(attempt=attempt,caller_seconds=time.perf_counter()-start)
     if attempt['status']!='AWAITING_REVIEW':
      recovery,recovery_receipt=session.turn(tool_output={'name':'helix_execution','output':json.dumps({'status':'UNEXPECTED_CHECK_OUTCOME','attempt':attempt,'exact_evidence_root':str(root/'store'),'obligation':'Reconsider the previous acceptance; no publication occurred'})})
      row.update(recovery_answer=recovery);row['turns'].append(recovery_receipt);row['usage']=dict(session.total)
      raise ValueError('Unexpected checker outcome; recovery preserved, pair stopped for independent adjudication')
    row['usage']=dict(session.total)
   row['status']=json.loads((out/'status.json').read_text());save(state,result)
  except Exception as e:
   result.update(state='STOPPED_PENDING_AUDIT',error=str(e),failed_arm=arm)
   if (out/'status.json').exists():result['partial_status']=json.loads((out/'status.json').read_text())
   save(state,result);return
 result['state']='AWAITING_INDEPENDENT_AUDIT';save(state,result)

if __name__=='__main__':globals()[sys.argv[1]](sys.argv[2])
