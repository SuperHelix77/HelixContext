"""Request-conditioned authorized output follow-up; existing control reused and labelled."""
import json,sys,time,tempfile
from pathlib import Path
from native_luna_ack_pair import REPO,AGENTS,sha,digest,enc,save,verify,dispatch,append,grade
from research_session import Session
from luna_event_id_adapter import resolve
from reason_obligation_check import check as check_reason
FIELDS=('minimum_distinct_approvers','approver_group','recovery_nonce','latency_threshold_ms','accounting_sequence')
def render(decision,raw,expected):
 if digest(raw)!=expected:raise ValueError('stale history')
 if set(decision)!={'authorized','policy','amendments','rejected','reason'}:raise ValueError('decision schema')
 if type(decision['authorized']) is not bool:raise ValueError('authorization must be semantic boolean')
 by={json.loads(l)['event']['turn']:json.loads(l)['event'] for l in raw.splitlines()}
 policy=decision['policy'];amendments=decision['amendments'];rejected=decision['rejected']
 if type(policy) is not int or policy not in by:raise ValueError('invalid policy')
 for ids in (amendments,rejected):
  if not isinstance(ids,list) or any(type(i) is not int or i not in by for i in ids) or len(set(ids))!=len(ids):raise ValueError('invalid references')
 if policy in amendments+rejected or set(amendments)&set(rejected):raise ValueError('contradictory roles')
 data=by[policy].get('data',{})
 if data.get('kind')!='authoritative policy' or not all(k in data for k in FIELDS):raise ValueError('unsupported policy record')
 out={'authorized':decision['authorized'],**{k:data[k] for k in FIELDS}}
 # Scope support is explicitly bounded; unfamiliar amendment means no publication.
 for i in sorted(amendments):
  a=by[i].get('data',{})
  if i<=policy or a.get('subject')!=data['subject'] or a.get('kind')!='authoritative amendment' or a.get('scope')!='Only approver_group changes; all other policy fields remain as originally recorded.' or 'approver_group' not in a:raise ValueError('unqualified amendment scope')
  out['approver_group']=a['approver_group']
 reason=decision['reason']
 if reason=='INSUFFICIENT_APPROVERS' and not out['authorized']:
  explanation=f"The requested single approver does not meet the policy minimum of {out['minimum_distinct_approvers']} distinct approvers. The applicable group is {out['approver_group']}; rejected records do not amend this requirement."
 elif reason=='WRONG_GROUP' and not out['authorized']:
  explanation=f"The requested approver group does not match the applicable policy group {out['approver_group']}."
 elif reason=='AUTHORIZED' and out['authorized']:
  explanation='The requested approval satisfies the applicable policy and selected amendments.'
 else:raise ValueError('unresolved or contradictory semantic decision')
 out.update(evidence_turns=[policy]+sorted(amendments)+rejected,explanation=explanation)
 return out

def preflight():
 events=json.loads((REPO/'benchmarks/frozen-high/protocol/long-horizon-v1.json').read_text())['events']
 raw=b''.join(enc({'event':e,'answer':'ACK '+e['event_id'],'owner':'caller'}) for e in events[:49]);h=digest(raw)
 d={'authorized':False,'policy':1,'amendments':[17],'rejected':[31],'reason':'INSUFFICIENT_APPROVERS'}
 grade(json.dumps(render(d,raw,h)))
 for obj,hh in [({**d,'policy':17,'amendments':[1]},h),({**d,'amendments':[31]},h),({**d,'rejected':[1]},h),({**d,'authorized':True},h),(d,'0'*64)]:
  try:render(obj,raw,hh)
  except ValueError:pass
  else:raise AssertionError('invalid renderer input accepted')
 altered=raw.replace(b'Only approver_group changes;',b'All requirements change;')
 try:render(d,altered,digest(altered))
 except ValueError:pass
 else:raise AssertionError('unknown scope accepted')
 wrong=render({**d,'authorized':True,'reason':'AUTHORIZED'},raw,h)
 try:grade(json.dumps(wrong))
 except AssertionError:pass
 else:raise AssertionError('semantic gate failed')
 print('V3 preflight PASS: roles, stale refs, unknown scope, contradictions, independent wrong-authorization rejection')

def prepare(root,prior):
 root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False);prior=Path(prior).resolve()
 m=json.loads((prior/'manifest.json').read_text());verify(m)
 assert json.loads((prior/'results.json').read_text())['state']=='DEVELOPMENT_PAIR_COMPLETE'
 (root/'fixture.json').write_bytes((prior/'fixture.json').read_bytes());cwd=root/'on';cwd.mkdir();sk=cwd/'.agents/skills/helixcontext/SKILL.md';sk.parent.mkdir(parents=True);sk.write_bytes((REPO/'skills/helixcontext/SKILL.md').read_bytes())
 paths=[Path(__file__),Path(__file__).with_name('luna_event_id_adapter.py'),Path(__file__).with_name('reason_obligation_check.py'),Path(__file__).with_name('native_luna_ack_pair.py'),AGENTS,root/'fixture.json',prior/'results.json',sk,REPO/'engine/output/research_session.py',REPO/'engine/output/app_server_native.py']
 save(root/'manifest.json',{'model':'gpt-5.6-luna','effort':'high','prior':str(prior),'retries':0,'max_native_turns':1,'classification':'Post-result development candidate; reused immediately preceding persistent Luna control. Not fresh paired causal ablation.','changes':['exact request-subject evidence projection with complete cold archive','exact ID adapter pre-attached','independent reason checker before publication'],'stop':'One attempt; preserve failed predecessor and all costs. No retry. Semantic grade required.','sha256':{str(p):sha(p) for p in paths}});print(sha(root/'manifest.json'))

def run(root):
 root=Path(root);m=json.loads((root/'manifest.json').read_text());verify(m);assert not (root/'results.json').exists(),'No retry';save(root/'results.json',{'state':'RUNNING'})
 cwd=root/'on';path=cwd/'history.jsonl';events=json.loads((root/'fixture.json').read_text())['events'];metrics={'logical_read_bytes':0,'logical_written_bytes':0};t=time.perf_counter()
 try:
  for e in events[:49]:
   metrics['logical_written_bytes']+=append(cwd/'received.jsonl',e)
   metrics['logical_read_bytes']+=path.stat().st_size if path.exists() else 0
   assert dispatch(e,path)=='ACK '+e['event_id']
  raw=path.read_bytes();h=digest(raw);metrics['logical_read_bytes']+=len(raw);metrics['logical_written_bytes']+=len(raw)
  assert [json.loads(l)['event'] for l in raw.splitlines()]==events[:49]
  metrics['logical_written_bytes']+=append(cwd/'received.jsonl',events[-1]);metrics['prep_seconds']=time.perf_counter()-t
  projection_start=time.perf_counter()
  selected=[line for line in raw.splitlines(keepends=True) if b'ORION-42' in line]
  packet=b''.join(selected);metrics['projection_seconds']=time.perf_counter()-projection_start;metrics['projected_bytes']=len(packet);metrics['archive_bytes']=len(raw);metrics['projection_read_bytes']=len(raw)
  assert len(selected)==3
  with Session(m['model'],cwd,cwd/'receipts/run',skill=cwd/'.agents/skills/helixcontext/SKILL.md') as s:
   assert s.registration['thread_id']==s.thread and s.registration['skill_sha256']==sha(cwd/'.agents/skills/helixcontext/SKILL.md')
   prompt='''Caller preflight is complete for this exact turn: relevant memory was consulted (no facts recalled), every event and ACK was durably recorded and recovered exactly, and Helix Context is already activated and registered for the actual native thread. Caller owns subsequent memory storage and skill/ledger bookkeeping. Do not repeat those completed caller-owned operations. This task-specific ownership instruction applies over generic bookkeeping defaults. Ordinary tools, independent semantic checks and requests for missing evidence remain available; use them whenever the decision requires them.
You own policy interpretation and authorization. Return only this semantic decision JSON:
{"authorized":boolean,"policy":base_policy_event_ID,"amendments":[applicable_amendment_event_IDs],"rejected":[relevant_non_authoritative_event_IDs],"reason":"INSUFFICIENT_APPROVERS|WRONG_GROUP|AUTHORIZED"}.
Choose one reason. Caller copies policy fields exactly, applies only each selected amendment's supported scope in event chronology, and renders the explanation from your reason and exact values. No ordering of policy versus amendment is required: the fields identify their roles. A selected unsupported scope, invalid reference, or contradictory decision stops publication and returns for semantic reconsideration. If these choices cannot express the answer, report the unresolved requirement instead. Exact evidence follows; no setup or bookkeeping remains for you.
'''+ '\nActual caller registration:\n'+json.dumps(s.registration)+'\nOriginal semantic request:\n'+json.dumps(events[-1])+'\nCaller selected every exact record containing the request subject ORION-42. Full49-record history remains in history.jsonl, SHA256='+h+'. These are raw records, not interpreted conclusions. Retrieve any additional evidence if needed. Selected records:\n'+packet.decode()
   answer,turn=s.turn(prompt);u=dict(s.total)
  verify(m);current=path.read_bytes();metrics['logical_read_bytes']+=len(current);assert current==raw
  decision=json.loads(answer);rt=time.perf_counter();normalized=resolve(decision,current);final=render(normalized,current,h);metrics['render_seconds']=time.perf_counter()-rt
  assert check_reason({'distinct_approvers':1,'approver_group':'violet'},final,decision['reason'])=='PASS','reason obligation failed'
  grade(json.dumps(final))
  metrics['logical_written_bytes']+=append(path,{'event':events[-1],'answer':json.dumps(final),'owner':'caller-rendered-model-decision'})
  save(root/'decision.json',decision);save(root/'rendered.json',final)
  result={'state':'AWAITING_INDEPENDENT_AUDIT','manifest_sha256':sha(root/'manifest.json'),'rows':{'on':{'usage':u,'answer':json.dumps(final),'semantic_decision':decision,'caller':metrics}},'comparison':'Reused prior native control; adaptive development follow-up, not new independent pair'}
  save(root/'results.json',result);grade(json.dumps(final));print(json.dumps({'usage':u,'caller':metrics,'answer':final}),flush=True)
 except BaseException as e:save(root/'failure.json',{'state':'STOPPED_PENDING_AUDIT','error':repr(e)});raise
if __name__=='__main__':globals()[sys.argv[1]](*sys.argv[2:])
