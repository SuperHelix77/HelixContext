"""Audit the explanation gap in the frozen W50 grader; no native calls."""
import json,sys
from pathlib import Path
from native_luna_ack_pair import REPO,enc,digest,grade,sha
from native_luna_ack_output_v3 import render

def run(out):
 events=json.loads((REPO/'benchmarks/frozen-high/protocol/long-horizon-v1.json').read_text())['events']
 raw=b''.join(enc({'event':e,'answer':'ACK '+e['event_id'],'owner':'caller'}) for e in events[:49])
 rows=[]
 for reason in ('INSUFFICIENT_APPROVERS','WRONG_GROUP'):
  decision={'authorized':False,'policy':1,'amendments':[17],'rejected':[31],'reason':reason}
  answer=render(decision,raw,digest(raw))
  try:grade(json.dumps(answer));old_pass=True
  except AssertionError:old_pass=False
  # Independent explicit request facts: E50 says exactly one violet approver.
  # This checks the stated rejection reason, not a complete authorization theorem.
  entailed=(1<answer['minimum_distinct_approvers'] if reason=='INSUFFICIENT_APPROVERS' else 'violet'!=answer['approver_group'])
  rows.append({'reason':reason,'answer':answer,'frozen_grade_pass':old_pass,'reason_entailed_by_request_and_resolved_policy':entailed})
 assert rows[0]['frozen_grade_pass'] and rows[0]['reason_entailed_by_request_and_resolved_policy']
 assert rows[1]['frozen_grade_pass'] and not rows[1]['reason_entailed_by_request_and_resolved_policy']
 result={'classification':'OBSERVED deterministic grader false-positive; no new native evidence','native_calls':0,'source_hashes':{str(p):sha(p) for p in (Path(__file__),Path(__file__).with_name('native_luna_ack_output_v3.py'),Path(__file__).with_name('native_luna_ack_pair.py'))},'cases':rows,'finding':'Frozen grade checks final factual fields and nonempty explanation, not explanation entailment. WRONG_GROUP receives PASS despite requested and resolved group both violet.','impact':'Actual V3 recovery used INSUFFICIENT_APPROVERS and survives this additional check. No evidence of loss in its actual reason; broader reason-code interface qualification weakened.','next_gate':'Before another native trial, prospectively bind structured request facts and independently verify reason entailment. Treat unsupported obligations as unresolved. Never silently repair a model reason.','limits':['Synthetic falsifier of checker sufficiency, not observed model error.','No full semantic correctness theorem; source authority/completeness and extra obligations remain model responsibilities.','Frozen results, graders and native traces unchanged.']}
 Path(out).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'old_grade_accepts_wrong_reason':True,'actual_v3_reason_survives':True,'native_calls':0}))
if __name__=='__main__':run(*sys.argv[1:])
