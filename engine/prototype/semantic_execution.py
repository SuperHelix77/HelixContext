"""Caller-owned mechanics with explicit semantic obligations, for every model.

No natural-language obligation classifier. Steps are caller-authorized callbacks,
not names/code supplied by a model. Engine remains the orchestrator on every path.
Existing research runners are frozen and do not automatically use this contract.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Step:
    name: str
    execute: object


def execute_decision(decision, *, expected_binding, current_binding, steps):
    """Run predetermined mechanics only after explicit semantic closure.

    current_binding checks the relevant inputs/authority, not outputs legitimately
    changed by a previous step. Atomic edits require their own CAS in execute().
    Return new evidence to the model on failure; never automatically replay steps.
    """
    if not isinstance(decision,dict) or set(decision)!={'artifact','assessment','semantic_obligations'}:
        raise ValueError('Explicit semantic decision schema required')
    if not isinstance(decision['artifact'],bytes):raise ValueError('Exact artifact bytes required')
    if not isinstance(decision['assessment'],str) or not decision['assessment'].strip():
        raise ValueError('Semantic assessment required')
    artifact=decision['artifact']
    obligations=decision['semantic_obligations']
    if not isinstance(obligations,list) or any(not isinstance(x,str) or not x.strip() for x in obligations):
        raise ValueError('Invalid semantic obligations')
    obligations=tuple(obligations)
    if not isinstance(expected_binding,str) or not expected_binding:
        raise ValueError('Explicit binding required')
    if not isinstance(steps,tuple) or any(not isinstance(s,Step) or not isinstance(s.name,str) or not s.name or not callable(s.execute) for s in steps):
        raise ValueError('Caller-defined immutable step list required')
    if len({s.name for s in steps})!=len(steps):raise ValueError('Duplicate step')
    receipts=[]
    def result(state,reason):
        return {'engine_active':True,'state':state,'reason':reason,'receipts':receipts,
                'semantic_obligations':list(obligations),'model_calls_added':0}
    if current_binding()!=expected_binding:return result('HOLD','stale authority/input binding')
    if obligations:return result('SEMANTIC_REENTRY','explicit unresolved semantics')
    for step in steps:
        if current_binding()!=expected_binding:return result('HOLD','binding changed before '+step.name)
        try:
            evidence=step.execute(artifact)
        except Exception as exc:
            receipts.append({'step':step.name,'status':'uncertain','error_type':type(exc).__name__})
            return result('RECONCILE','step raised; effects may have occurred; no retry')
        if not isinstance(evidence,dict) or type(evidence.get('passed')) is not bool:
            receipts.append({'step':step.name,'status':'uncertain'})
            return result('RECONCILE','invalid caller receipt; no retry')
        receipts.append({'step':step.name,'status':'passed' if evidence['passed'] else 'failed','evidence':evidence})
        if not evidence['passed']:return result('SEMANTIC_REENTRY','new failure evidence')
    return result('MECHANICS_COMPLETED','authorized steps completed; semantic adequacy remains the model assessment')
