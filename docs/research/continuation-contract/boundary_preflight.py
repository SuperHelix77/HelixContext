"""Offline falsifier for post-execution review; no model calls or model verdicts."""
import hashlib
import json
from pathlib import Path
import sys
import time
import audit

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[2]/'engine/prototype'))
from evidence import Store
from review_gate import Gate

NARROW='''from queue_state import Queue
q=Queue()
assert q.append_batch([1,2])==2
assert q.append_batch([3])==3
assert q.items==[1,2,3]
print('PASS declared smoke checks; alias and failure semantics unchecked')
'''


def run(root):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter();result={'classification':'OFFLINE_ONLY_NOT_NATIVE_PARITY','cases':{},'native_calls':0}
    good=audit.GOOD.encode();bad=good.replace(b'self.cursor=len(self.items)',b'self.cursor+=len(pending)')
    base=b'class Queue: pass\n'
    contract=(HERE/'CONTRACT.md').read_bytes()
    runtime={'executable':sys.executable,'sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),'version':sys.version,
             'scope':'Observed identity only, not enforced runtime dependency closure'}
    for name,proposal,stale in [('valid',good,False),('semantic_defect',bad,False),('stale_after_check',good,True)]:
        store=Store(root/name);gate=Gate(store)
        head=gate.initialize('queue',gate.bundle({'queue_state.py':base,'CONTRACT.md':contract,'check.py':NARROW.encode(),'runtime.json':json.dumps(runtime).encode()}))
        attempt=gate.stage('proposal','queue',head,{'queue_state.py':proposal},steps=[{'name':'smoke','argv':[sys.executable,'-B','check.py']}],environment_id='offline-python',env={},timeout=10)
        assert attempt['status']=='AWAITING_REVIEW'
        assert gate.head('queue')==head, 'A mechanical PASS must not publish'
        check_evidence=store.receipt(attempt['evidence'])
        # Independent semantic counterexample; NEVER presented as an Astra verdict.
        try:
            audit.exercise(proposal.decode(),('append','alias_add','empty'))
            semantic_ok=True
        except AssertionError:
            semantic_ok=False
        review=store.put(json.dumps({'reviewer':'offline-state-oracle','semantic_ok':semantic_ok,'sequence':['append','alias_add','empty'],'scope':'One explicit counterexample check, not complete semantic proof'}).encode())['sha256']
        if stale:
            changed=gate.files(head['root']);changed['CONTRACT.md']+=b'\nNew authority revision: prior approvals require refresh.\n'
            authoritative=gate.advance('queue',head,gate.bundle(changed))
        else:authoritative=head
        final=gate.review('proposal',approve=semantic_ok,reviewer='offline-oracle',evidence_ref=review)
        expected='CONFLICT' if stale else 'ACCEPTED' if semantic_ok else 'REJECTED'
        assert final['status']==expected
        if expected!='ACCEPTED':assert gate.head('queue')==authoritative
        else:assert gate.files(gate.head('queue')['root'])['queue_state.py']==proposal
        result['cases'][name]={'declared_checks_passed':check_evidence['validation']['process_success'],
            'no_publication_before_review':True,'offline_semantic_check_passed':semantic_ok,'terminal_status':final['status'],
            'candidate_root':attempt['candidate'],'check_evidence':attempt['evidence'],'review_evidence':review,
            'logical_store_counters':dict(store.metrics)}
    result.update(seconds=time.perf_counter()-start,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Exact Engine-owned artifact references only. No model behavior, deployed working tree, environment closure or full physical-cost claim.')
    (root/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return result

if __name__=='__main__':run(sys.argv[1])
