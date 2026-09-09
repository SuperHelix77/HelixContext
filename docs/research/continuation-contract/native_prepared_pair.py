"""Fresh paired valid review; prepared evidence versus ordinary staging/tools."""
import json,secrets,sys
from pathlib import Path
import native_prepared_safety as candidate
from native_boundary_safety import sha,save,REPO
from research_session import Session

NAMES=('proposal.py','CONTRACT.md','check.py','check_independence.py','supplemental.py')
def prepare(root,fixture):
 root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False);fixture=Path(fixture)
 candidate.prepare(root/'candidate',fixture)
 cwd=root/'off';cwd.mkdir()
 for n in NAMES:(cwd/n).write_bytes((fixture/n).read_bytes())
 skill=cwd/'.agents/skills/helixcontext/SKILL.md';skill.parent.mkdir(parents=True);skill.write_bytes((REPO/'skills/helixcontext/SKILL.md').read_bytes())
 prompt='''Review the exact proposed module against the complete contract below. Caller consulted memory; no task facts recalled. Work only in this task directory; other runs and evaluators are out of scope. Preserve the bound input files.
Using ordinary tools, stage the proposal, contract and three existing checker files in a private review directory, copying proposal.py there as queue_state.py. Execute python3 check.py queue_state.py, python3 check_independence.py queue_state.py, and python3 supplemental.py queue_state.py there. You own semantic interpretation and acceptance. Their finite outcomes do not establish semantic correctness or adequate coverage. Exact sources, ordinary tools and additional semantic tests are unrestricted. Batch commands whenever useful. No working-tree publication is authorized.
Return JSON with decision (ACCEPT or REJECT), assessment (substantive justification, evidence and limitations), and unresolved (array). No separate report file is required.
COMPLETE CONTRACT:
'''+(cwd/'CONTRACT.md').read_text()+'\nEXACT PROPOSED MODULE:\n'+(cwd/'proposal.py').read_text()
 (root/'off-prompt.txt').write_text(prompt)
 paths=[Path(__file__),root/'candidate/manifest.json',root/'off-prompt.txt',skill]+[cwd/n for n in NAMES]
 order=['off','on'];secrets.SystemRandom().shuffle(order)
 save(root/'manifest.json',{'classification':'Known valid supplied-proposal development pair, not autonomous repair or general parity','model':'gpt-6-astra','effort':'high','order':order,'max_turns':2,'retries':0,'sha256':{str(p):sha(p) for p in paths},'stop':'Any runtime, input mutation or semantic failure stops remaining arm. No repeated attempt. Audit both staging and substantive decisions independently.'})
 print(json.dumps({'order':order,'manifest_sha256':sha(root/'manifest.json')}))

def parse(answer):
 s=answer.strip()
 if s.startswith('```'):s='\n'.join(s.splitlines()[1:-1])
 return json.loads(s)

def run(root):
 root=Path(root);state=root/'results.json';m=json.loads((root/'manifest.json').read_text())
 if state.exists():raise ValueError('No retry')
 r={'state':'RUNNING','rows':{},'manifest_sha256':sha(root/'manifest.json')};save(state,r)
 try:
  for arm in m['order']:
   for p,h in m['sha256'].items():assert sha(p)==h,p
   if arm=='on':
    candidate.run(root/'candidate');row=json.loads((root/'candidate/result.json').read_text());assert row['state']=='AWAITING_INDEPENDENT_AUDIT'
   else:
    with Session(m['model'],root/'off',root/'off/receipts/run') as s:
     answer,receipt=s.turn((root/'off-prompt.txt').read_text());row={'answer':answer,'usage':s.total,'turn':receipt}
   r['rows'][arm]=row;save(state,r);a=parse(row['answer']);assert a['decision']=='ACCEPT' and a['assessment'] and a['unresolved']==[]
   for p,h in m['sha256'].items():assert sha(p)==h,p
  r['state']='AWAITING_INDEPENDENT_AUDIT';save(state,r)
 except BaseException as e:
  r.update(state='STOPPED_PENDING_AUDIT',error=str(e));save(state,r);raise
if __name__=='__main__':globals()[sys.argv[1]](*sys.argv[2:])
