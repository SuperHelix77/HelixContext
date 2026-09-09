"""One native semantic review of caller-prepared evidence; no retries/promotion."""
import json,sys,time
from pathlib import Path
from prepared_review import prepare as evidence_prepare,validate
from native_boundary_safety import sha,save,REPO
sys.path.insert(0,str(REPO/'engine/output'))
from research_session import Session

PROMPT='''Review the exact proposed module against the complete contract below. Caller consulted memory; no task facts recalled. Work only in this task directory; other runs and evaluators are out of scope. Preserve the bound input files. $helixcontext is caller-registered.
Caller already staged these exact bytes and executed the three existing checkers. Their recorded PASS establishes finite test outcomes only, not semantic correctness or adequate coverage. You own semantic interpretation and acceptance. Exact checker sources, snapshots and raw outputs remain available; ordinary tools and additional semantic tests are unrestricted. No Engine integration is required. No working-tree publication is authorized.
Return JSON with decision (ACCEPT or REJECT), assessment (substantive justification, evidence and limitations), and unresolved (array). No separate report file is required.
'''

def prepare(root,fixture):
 root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False);cwd=root/'on';cwd.mkdir();fixture=Path(fixture)
 for n in ('proposal.py','CONTRACT.md','check.py','check_independence.py','supplemental.py'):(cwd/n).write_bytes((fixture/n).read_bytes())
 skill=cwd/'.agents/skills/helixcontext/SKILL.md';skill.parent.mkdir(parents=True);skill.write_bytes((REPO/'skills/helixcontext/SKILL.md').read_bytes())
 t=time.perf_counter();h=evidence_prepare(cwd,cwd/'.prepared');r=validate(cwd/'.prepared',h);seconds=time.perf_counter()-t
 packet={'receipt':'.prepared/receipt.json','sha256':h,'status':r['status'],'checks':[{'name':c['name'],'status':c['status'],'exit':c['exit_code'],'evidence':str(Path(c['cwd']).relative_to(cwd))} for c in r['checks']],'unchecked':r['unchecked']}
 prompt=PROMPT+'\nCOMPLETED EVIDENCE:\n'+json.dumps(packet)+'\nCOMPLETE CONTRACT:\n'+(cwd/'CONTRACT.md').read_text()+'\nEXACT PROPOSED MODULE:\n'+(cwd/'proposal.py').read_text()
 (root/'prompt.txt').write_text(prompt)
 paths=[Path(__file__),Path(__file__).with_name('prepared_review.py'),REPO/'engine/output/research_session.py',REPO/'engine/output/app_server_native.py',root/'prompt.txt',skill]+[cwd/n for n in r['input_roots']]
 save(root/'manifest.json',{'model':'gpt-6-astra','effort':'high','max_native_turns':1,'retries':0,'receipt_hash':h,'sha256':{str(p):sha(p) for p in paths},'prepare_and_validate_seconds':seconds,'classification':'Prospective semantic safety gate; no savings or parity claim','stop':'One turn only, audit semantic answer and all costs; no retries or promotion.'})
 print(sha(root/'manifest.json'))

def run(root):
 root=Path(root);state=root/'result.json'
 if state.exists():raise ValueError('No retry')
 m=json.loads((root/'manifest.json').read_text());save(state,{'state':'STARTED','manifest_sha256':sha(root/'manifest.json')})
 try:
  for p,h in m['sha256'].items():assert sha(p)==h,p
  validate(root/'on/.prepared',m['receipt_hash'])
  with Session(m['model'],root/'on',root/'on/receipts/run',root/'on/.agents/skills/helixcontext/SKILL.md') as session:
   answer,receipt=session.turn((root/'prompt.txt').read_text())
   result={'state':'AWAITING_INDEPENDENT_AUDIT','answer':answer,'usage':session.total,'turn':receipt,'manifest_sha256':sha(root/'manifest.json')}
  for p,h in m['sha256'].items():assert sha(p)==h,p
  validate(root/'on/.prepared',m['receipt_hash']);save(state,result)
 except BaseException as e:
  save(state,{'state':'STOPPED_PENDING_AUDIT','error':str(e),'raw_evidence':str(root/'on/receipts/run')});raise

if __name__=='__main__':globals()[sys.argv[1]](*sys.argv[2:])
