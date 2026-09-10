import json
from pathlib import Path

import pytest

from transition_transfer_v1 import (REPO,enc,selection,select_prompt,realize,grade,
    PassiveWorkflow,CompletionLedger,Memory,Store,EMPTY)


def test_existing_mechanisms_deliver_exact_workflow_and_semantic_answer(tmp_path):
    events=json.loads((REPO/'benchmarks/frozen-high/protocol/long-horizon-v1.json').read_text())['events']
    flow=PassiveWorkflow(CompletionLedger(Memory(Store(tmp_path))),'W50','a'*64)
    head=EMPTY;records=[]
    for event in events[:49]:
        r=flow.accept(enc(event),expected_head=head);head=r['head']
        records.append({'event':event,'answer':r['answer'],'owner':'caller'})
    assert [json.loads(x) for x in flow.exact_events(head)]==events[:49]
    assert len(flow.deliver(head)['deliveries'])==49
    assert flow.accept(enc(events[-1]),expected_head=head)['state']=='semantic_required'
    raw=b''.join(enc(r) for r in records)
    import hashlib
    request={'subject':'ORION-42','distinct_approvers':1,'approver_group':'violet'}
    valid=realize({'policy':'E01','amendments':['E17']},raw,hashlib.sha256(raw).hexdigest(),request)
    grade(json.dumps(valid['answer']))
    # Exact hashing and successful mechanics cannot certify a wrong selection.
    wrong=realize({'policy':'E01','amendments':[]},raw,hashlib.sha256(raw).hexdigest(),request)
    with pytest.raises(AssertionError):grade(json.dumps(wrong['answer']))
    packet=select_prompt(events[-1],raw)
    for record in records:
        if b'ORION-42' in enc(record):assert enc(record).decode().strip() in packet
    assert 'history.jsonl' in packet


@pytest.mark.parametrize('text',['{"policy":"E01","policy":"E31","amendments":[]}',
                                  'not a JSON selection'])
def test_selection_ambiguity_is_not_silently_repaired(text):
    with pytest.raises(ValueError):selection(text)
