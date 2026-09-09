"""One live-thread contract-amendment recovery experiment; no savings denominator."""
import json,sys,time,subprocess
from pathlib import Path
import audit,caller_patch_pair
from native_boundary_safety import sha,save,REPO,HERE
sys.path.insert(0,str(REPO/'engine/output'));from research_session import Session
sys.path.insert(0,str(REPO/'engine/prototype'));from evidence import Store;from review_gate import Gate

AMEND='\n## Authoritative amendment v2\nAll earlier requirements remain. A batch may contain at most two values. A batch exceeding two values must raise ValueError without changing items, cursor or list identity. Exhausting a rejected iterable is not required. Successful empty, one-value and two-value batches retain all prior semantics.\n'
LIMIT_CHECK='''
ns={};exec(source,ns);q=ns['Queue']();alias=q.items
alias.extend([9]);before=(alias[:],q.cursor)
try:q.append_batch(iter([1,2,3]))
except ValueError:pass
else:raise AssertionError('Oversized batch accepted')
assert q.items is alias and (q.items,q.cursor)==before
assert q.append_batch([1,2])==3
assert q.append_batch([])==3
print('PASS amended batch limit and failure atomicity')
'''

def prepare(root):
 root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False);cwd=root/'on';cwd.mkdir()
 original=(HERE/'CONTRACT.md').read_text();v1=caller_patch_pair.checker();marker="payload=[] if operation=='empty' else [0,2,7]";assert v1.count(marker)==1
 v2=v1.replace(marker,"payload=[] if operation=='empty' else [0,2]")+LIMIT_CHECK
 for n,s in {'CONTRACT.md':original,'proposal.py':audit.GOOD,'check.py':v1,'check_independence.py':(HERE/'check_queue_independence_v1.py').read_text()}.items():(cwd/n).write_text(s)
 (root/'contract-v2.md').write_text(original+AMEND);(root/'checker-v2.py').write_text(v2)
 skill=cwd/'.agents/skills/helixcontext/SKILL.md';skill.parent.mkdir(parents=True);skill.write_bytes((REPO/'skills/helixcontext/SKILL.md').read_bytes())
 g=Gate(Store(root/'store'));head=g.initialize('task',g.bundle({'queue_state.py':audit.GOOD.encode(),'CONTRACT.md':original.encode(),'check.py':v1.encode(),'check_independence.py':(cwd/'check_independence.py').read_bytes()}));save(root/'head.json',head)
 prompt='''Review the proposed module against the complete public contract below, including semantic self-review and unresolved obligations. $helixcontext is already registered by the caller. Caller consulted memory; no facts recalled. Work only here; other experiments and evaluators are out of scope. Caller owns exact application and mechanical checks; do not edit the proposal or task files. Ordinary tools and additional semantic tests remain available. No Engine discovery/integration is needed.
Return a JSON object with decision (ACCEPT or REJECT), assessment (your substantive semantic reasoning, assumptions, expected checks and limitations), and unresolved (array of strings). An empty unresolved array means no identified outstanding semantic obligation, not proof of universal correctness. Do not claim execution has already happened.
If the caller later supplies authoritative changed contract/source state as tool output, reconsider the earlier judgment, resolve the changed obligation, and return decision REVISE, source (complete corrected Python module as a string), assessment, and unresolved. Do not edit task files: caller will copy your exact proposed bytes and run checks. Historical conclusions do not override amended current authority.
COMPLETE CONTRACT:\n'''+original+'\nPROPOSAL (exact):\n'+audit.GOOD
 (root/'prompt.txt').write_text(prompt)
 paths=[Path(__file__),Path(REPO/'engine/output/research_session.py'),Path(REPO/'engine/output/app_server_native.py')]+[REPO/'engine/prototype'/n for n in ('review_gate.py','evidence.py','checked_steps.py')]+list(cwd.glob('*.py'))+[cwd/'CONTRACT.md',skill,root/'contract-v2.md',root/'checker-v2.py',root/'prompt.txt',root/'head.json']
 save(root/'manifest.json',{'model':'gpt-6-astra','effort':'high','max_turns':2,'retries':0,'per_turn_review_input_limit':150000,'per_turn_review_output_limit':4000,'sha256':{str(p):sha(p) for p in paths},'allowed_mutations':'Caller replaces cwd CONTRACT.md and check.py with the frozen v2 files between turns only. Proposal and all other files remain bound.','grading':'Initial substantive acceptance; old-root staging refused without a process; same-thread revised source passes v2 and independence checks; exact raw accounting. Schema failures are transport/dispatch failures, not proof of intelligence loss.','classification':'One deliberately injected development recovery, no paired savings or general parity'})
 print(root)

def parse(text):
 text=text.strip()
 if text.startswith('```'):text='\n'.join(text.splitlines()[1:-1])
 return json.loads(text)

def run(root):
 root=Path(root);cwd=root/'on';m=json.loads((root/'manifest.json').read_text())
 for p,h in m['sha256'].items():assert sha(p)==h,p
 if (root/'results.json').exists():raise ValueError('No retry')
 result={'state':'STARTED','manifest_sha256':sha(root/'manifest.json'),'turns':[]};save(root/'results.json',result)
 g=Gate(Store(root/'store'));head=json.loads((root/'head.json').read_text())
 try:
  with Session(m['model'],cwd,cwd/'receipts/run',cwd/'.agents/skills/helixcontext/SKILL.md') as s:
   answer,row=s.turn((root/'prompt.txt').read_text());result['turns'].append({'receipt':row,'answer':answer});save(root/'results.json',result)
   response=parse(answer);assert response['decision']=='ACCEPT' and isinstance(response['assessment'],str) and response['assessment'] and response['unresolved']==[]
   assert row['usage_delta']['input_tokens']<=m['per_turn_review_input_limit'] and row['usage_delta']['output_tokens']<=m['per_turn_review_output_limit']
   for p,h in m['sha256'].items():assert sha(p)==h,p
   files=g.files(head['root']);files['CONTRACT.md']=(root/'contract-v2.md').read_bytes();files['check.py']=(root/'checker-v2.py').read_bytes()
   current=g.advance('task',head,g.bundle(files));(cwd/'CONTRACT.md').write_bytes(files['CONTRACT.md']);(cwd/'check.py').write_bytes(files['check.py'])
   try:g.stage('stale','task',head,{'queue_state.py':files['queue_state.py']},steps=[{'name':'check','argv':[sys.executable,'-B','check.py','queue_state.py']}],environment_id='fixture')
   except ValueError as e:assert str(e)=='Stale base'
   else:raise AssertionError('Stale operation executed')
   try:g.attempt('stale')
   except ValueError:pass
   else:raise AssertionError('Stale attempt reserved')
   result['stale_execution_refused']=True;result['new_head']=current
   delta={'status':'AUTHORITY_CHANGED_BEFORE_EXECUTION','executed':False,'previous_head':head,'current_head':current,'amendment':AMEND,'current_contract':str(cwd/'CONTRACT.md'),'current_checker':str(cwd/'check.py'),'proposal_unchanged':True,'obligation':'Reconsider the prior proposal against the amended contract; return the revised module per the initial task.'}
   answer,row=s.turn(tool_output={'name':'helix_execution','output':json.dumps(delta)});result['turns'].append({'receipt':row,'answer':answer});save(root/'results.json',result)
   response=parse(answer);assert response['decision']=='REVISE' and isinstance(response['assessment'],str) and response['assessment'] and response['unresolved']==[]
   assert row['usage_delta']['input_tokens']<=m['per_turn_review_input_limit'] and row['usage_delta']['output_tokens']<=m['per_turn_review_output_limit']
   assert isinstance(response['source'],str)
   for p,h in m['sha256'].items():
    expected=sha(root/'contract-v2.md') if p==str(cwd/'CONTRACT.md') else sha(root/'checker-v2.py') if p==str(cwd/'check.py') else h
    assert sha(p)==expected,p
   attempt=g.stage('revised','task',current,{'queue_state.py':response['source'].encode()},steps=[{'name':'contract-v2','argv':[sys.executable,'-B','check.py','queue_state.py']},{'name':'independence','argv':[sys.executable,'-B','check_independence.py','queue_state.py']}],environment_id='fixture',env={},timeout=30)
   result.update(state='AWAITING_INDEPENDENT_AUDIT',attempt=attempt,usage=s.total,thread_id=s.thread)
   assert attempt['status']=='AWAITING_REVIEW','Revised module failed checks'
 except Exception as e:result.update(state='STOPPED',error=type(e).__name__+': '+str(e))
 save(root/'results.json',result)

if __name__=='__main__':globals()[sys.argv[1]](sys.argv[2])
