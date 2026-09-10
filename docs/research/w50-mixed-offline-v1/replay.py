"""Scripted ledger integration falsifier. No model calls or semantic scoring."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'engine/prototype'))
from evidence import Store
from workflow_memory import Memory, encode
from completion_ledger import CompletionLedger, EMPTY
from passive_workflow import PassiveWorkflow


def event(n, request=None):
    return {'turn':n, 'event_id':f'E{n:02d}', 'data':{'note':'exact cold evidence'},
            'request':request or f'Record this event for the ongoing workflow. Reply ACK E{n:02d}. No other action is requested at this turn.'}


def main(out):
    start = time.perf_counter(); results = {}
    with tempfile.TemporaryDirectory() as d:
        flow = PassiveWorkflow(CompletionLedger(Memory(Store(Path(d)/'passive'))),'test','a'*64)
        first = flow.accept(encode(event(1)),expected_head=EMPTY)
        sem = flow.accept(encode(event(2,'Clarify the contradictory requirement before proceeding.')),expected_head=first['head'])
        assert sem['state']=='semantic_required' and sem['head']==first['head']
        try: flow.accept(encode(event(3)),expected_head=first['head'])
        except ValueError as exc: gap = str(exc)
        else: raise AssertionError('Naive interleaving unexpectedly bypassed sequence gate')
        assert len(flow.exact_events(first['head']))==1
        results['old_passive_skip_falsifier']={'semantic_route':sem['state'],'next_ack_error':gap,'committed_records_after_failure':1}
        store = Store(Path(d)/'generic'); ledger = CompletionLedger(Memory(store)); head=EMPTY
        raws=[]; receipts=[]
        for n in [1,2,3]:
            raw = encode({'original_event':event(n,'Semantic checkpoint' if n==2 else None),
                          'answer_owner':'SCRIPTED_PLACEHOLDER_NOT_MODEL' if n==2 else 'engine',
                          'answer_base64':base64.b64encode(b'SCRIPTED, not a semantic answer' if n==2 else f'ACK E{n:02d}'.encode()).decode()})
            raws.append(raw); r=ledger.ingest('mixed-offline',f'E{n:02d}',raw,expected_head=head,sequence=n)
            receipts.append(r); head=r['head']
        replay=ledger.ingest('mixed-offline','E02',raws[1],expected_head=head,sequence=2)
        assert replay['replayed'] and replay['head']==head
        try: ledger.ingest('mixed-offline','E02',raws[1]+b' ',expected_head=head,sequence=2)
        except ValueError: pass
        else: raise AssertionError('Conflict accepted')
        reopened=CompletionLedger(Memory(Store(Path(d)/'generic')))
        restored=reopened.recover('mixed-offline',expected_head=head)
        assert [r['raw'] for r in restored]==raws
        assert [r['event'] for r in restored]==['E01','E02','E03']
        results['generic_mixed_data_replay']={'exact_restart':'PASS','same_replay':'PASS','conflict_rejected':'PASS',
            'completed_records':3,'head':head,'logical_store_io':dict(store.metrics),
            'scope':'Scripted payload storage only; no mixed semantic adapter, model authorship, downstream effect or consumer ACK qualified'}
    paths=[Path(__file__)]
    paths += [REPO/'engine/prototype'/n for n in ['evidence.py','workflow_memory.py','completion_ledger.py','passive_workflow.py','receipt_delivery.py']]
    results.update(native_model_calls=0,seconds=time.perf_counter()-start,
        classification='OFFLINE integration falsifier; not capability or token savings',
        bindings={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    Path(out).write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({'native_model_calls':0,'naive_passive_interleaving':'REJECTED_AS_EXPECTED','generic_data_replay':'PASS'}))


if __name__ == '__main__': main(sys.argv[1])
