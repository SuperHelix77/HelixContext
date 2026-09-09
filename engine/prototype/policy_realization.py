"""Realize model-selected policy references under an explicit bounded rule schema.

The model selects semantic authority and applicable amendments. Caller supplies a
bound structured request. Labels in raw data do not establish authority. Unknown
fields/scopes must return to semantics; never guess a rule or parse free-form intent.
"""
import hashlib
import json

FIELDS={'rollback_mode','minimum_distinct_approvers','recovery_nonce','latency_threshold_ms','accounting_sequence','approver_group'}


def realize(selection, raw, expected_hash, request):
    if not isinstance(raw,bytes) or hashlib.sha256(raw).hexdigest()!=expected_hash:
        raise ValueError('Stale exact history')
    if not isinstance(selection,dict) or set(selection)!={'policy','amendments'}:
        raise ValueError('Unresolved or invalid selection')
    if not isinstance(request,dict) or set(request)!={'subject','distinct_approvers','approver_group'}:
        raise ValueError('Unsupported structured request')
    count=request['distinct_approvers']
    if type(count) is not int or count<0 or any(not isinstance(request[k],str) or not request[k] for k in ['subject','approver_group']):
        raise ValueError('Invalid request facts')
    records=[json.loads(line)['event'] for line in raw.splitlines()]
    by={e['event_id']:e for e in records}
    if len(by)!=len(records) or len({e['turn'] for e in records})!=len(records):
        raise ValueError('Ambiguous exact identities')
    policy=selection['policy'];amendments=selection['amendments']
    if not isinstance(policy,str) or policy not in by or not isinstance(amendments,list):
        raise ValueError('Unbound selection')
    if any(not isinstance(x,str) or x not in by for x in amendments) or len(set(amendments))!=len(amendments) or policy in amendments:
        raise ValueError('Conflicting selection')
    base=by[policy]['data']
    if set(base)!=FIELDS|{'subject','kind'} or base['kind']!='authoritative policy' or base['subject']!=request['subject']:
        raise ValueError('Unknown base-policy schema or subject')
    if base['rollback_mode']!='manual-only':raise ValueError('Unsupported mode')
    minimum=base['minimum_distinct_approvers']
    if type(minimum) is not int or minimum<1:raise ValueError('Unsupported minimum')
    if any(not isinstance(base[k],str) for k in FIELDS-{'minimum_distinct_approvers'}):
        raise ValueError('Exact string fields required')
    facts={k:base[k] for k in FIELDS-{'rollback_mode'}}
    chosen=[by[x] for x in amendments]
    for e in sorted(chosen,key=lambda x:x['turn']):
        a=e['data']
        if e['turn']<=by[policy]['turn'] or set(a)!={'subject','kind','scope','approver_group'} or a['subject']!=request['subject'] or a['kind']!='authoritative amendment' or a['scope']!='Only approver_group changes; all other policy fields remain as originally recorded.' or not isinstance(a['approver_group'],str):
            raise ValueError('Unknown amendment; semantic re-entry required')
        facts['approver_group']=a['approver_group']
    if count<minimum:
        authorized=False;reason='INSUFFICIENT_APPROVERS'
        explanation=f"{count} approver(s) do not meet the selected policy minimum of {minimum}."
    elif request['approver_group']!=facts['approver_group']:
        authorized=False;reason='WRONG_GROUP';explanation='The requested approver group differs from the selected policy group.'
    else:
        authorized=True;reason='AUTHORIZED';explanation='The structured request meets the selected minimum and group requirements.'
    return {'answer':{'authorized':authorized,**facts,'evidence_turns':[by[policy]['turn']]+[e['turn'] for e in sorted(chosen,key=lambda x:x['turn'])],
                      'explanation':explanation},'reason':reason,
            'authority':'Model-selected references; mechanical realization does not validate semantic selection'}
