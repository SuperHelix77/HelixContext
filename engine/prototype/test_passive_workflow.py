import json
from pathlib import Path
import pytest
from evidence import Store
from workflow_memory import Memory
from completion_ledger import CompletionLedger,EMPTY
from passive_workflow import PassiveWorkflow


def setup(tmp_path,authority='a'*64):
    return PassiveWorkflow(CompletionLedger(Memory(Store(tmp_path))),'workflow',authority)


def test_real_w50_exact_replay_and_final_semantic_route(tmp_path):
    p=Path(__file__).resolve().parents[2]/'benchmarks/frozen-high/protocol/long-horizon-v1.json'
    events=json.loads(p.read_text())['events'];flow=setup(tmp_path);head=EMPTY;raws=[]
    for e in events[:49]:
        raw=json.dumps(e,ensure_ascii=False,indent=1).encode();raws.append(raw)
        r=flow.accept(raw,expected_head=head);head=r['head']
        assert r['answer']=='ACK '+e['event_id'] and r['model_calls_added']==0
    flow=setup(tmp_path)
    assert flow.exact_events(head)==raws
    delivered=flow.deliver(head)
    assert len(delivered['deliveries'])==49
    final=flow.accept(json.dumps(events[-1]).encode(),expected_head=head)
    assert final['state']=='semantic_required' and final['head']==head
    replay=flow.accept(raws[0],expected_head=head)
    assert replay['replayed'] and replay['head']==head
    with pytest.raises(ValueError):setup(tmp_path,'b'*64).exact_events(head)


def test_cancel_gap_duplicate_key_and_conflict(tmp_path):
    flow=setup(tmp_path)
    e={'turn':1,'event_id':'E01','data':{},'request':'Record this event for the ongoing workflow. Reply ACK E01. No other action is requested at this turn.'}
    r=flow.accept(json.dumps(e).encode(),expected_head=EMPTY)
    changed={**e,'request':'Cancel and delete the previous event'}
    assert flow.accept(json.dumps(changed).encode(),expected_head=r['head'])['state']=='semantic_required'
    assert flow.accept(b'{"request":"x","request":"y"}',expected_head=r['head'])['state']=='semantic_required'
    with pytest.raises(ValueError):flow.accept(json.dumps({**e,'data':{'changed':True}}).encode(),expected_head=r['head'])
    gap={**e,'turn':3,'event_id':'E03','request':'Record this event for the ongoing workflow. Reply ACK E03. No other action is requested at this turn.'}
    with pytest.raises(ValueError):flow.accept(json.dumps(gap).encode(),expected_head=r['head'])
    assert len(flow.exact_events(r['head']))==1
