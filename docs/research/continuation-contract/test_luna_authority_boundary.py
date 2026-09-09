"""Offline falsifiers for the exact safety-fixture authority boundary."""
import copy,hashlib,json
import pytest
from luna_semantic_safety_pair_v2 import AUTHORITY
from luna_semantic_safety_pair import REPO, ordinary
from policy_realization import realize


def test_request_attribute_cannot_silently_enter_mechanical_schema():
    events=json.loads((REPO/'benchmarks/frozen-high/protocol/long-horizon-v1.json').read_text())['events']
    events=[events[i] for i in (0,16,30)]
    raw=b'\n'.join(json.dumps({'event':e}).encode() for e in events)
    digest=hashlib.sha256(raw).hexdigest()
    selection={'policy':'E01','amendments':['E17']}
    request={'subject':'ORION-42','distinct_approvers':2,'approver_group':'violet'}
    assert realize(selection,raw,digest,request)['answer']['authorized'] is True
    with pytest.raises(ValueError,match='Unsupported structured request'):
        realize(selection,raw,digest,{**request,'maintenance_ticket_present':False})
    changed=copy.deepcopy(events)
    changed[0]['data']['maintenance_ticket_required']=True
    newraw=b'\n'.join(json.dumps({'event':e}).encode() for e in changed)
    with pytest.raises(ValueError,match='Stale exact history'):
        realize(selection,newraw,digest,request)
    with pytest.raises(ValueError,match='Unknown base-policy schema'):
        realize(selection,newraw,hashlib.sha256(newraw).hexdigest(),request)
    # Clarified ordinary path retains extra facts and rules verbatim.
    prompt=ordinary({**request,'maintenance_ticket_present':False},changed)
    assert AUTHORITY in prompt
    assert '"maintenance_ticket_present": false' in prompt
    assert '"maintenance_ticket_required": true' in prompt
