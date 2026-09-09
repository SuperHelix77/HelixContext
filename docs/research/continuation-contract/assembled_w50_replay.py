"""Replay recorded V7 semantics through current passive lifecycle; zero inference."""
import hashlib,json,tempfile,time
from pathlib import Path
from passive_workflow import PassiveWorkflow
from completion_ledger import CompletionLedger,EMPTY
from evidence import Store
from workflow_memory import Memory
from native_luna_ack_output_v5 import render,grade,check_reason
from luna_event_id_adapter import resolve


def run():
    base=Path('/Users/mert/Documents/ChatGPT/Helix/research/native-luna-base-v7-20260909')
    p=base/'on/receipts/run';status=json.loads((p/'status.json').read_text())
    assert hashlib.sha256((p/'native-events.jsonl').read_bytes()).hexdigest()==status['native_events_sha256']
    fixture=Path('benchmarks/frozen-high/protocol/long-horizon-v1.json')
    events=json.loads(fixture.read_text())['events'];authority=hashlib.sha256(fixture.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory() as tmp:
        store=Store(tmp);flow=PassiveWorkflow(CompletionLedger(Memory(store)),'W50',authority)
        head=EMPTY;start=time.perf_counter()
        for e in events[:49]:head=flow.accept(json.dumps(e,ensure_ascii=False).encode(),expected_head=head)['head']
        restored=flow.exact_events(head)
        raw=b''.join((json.dumps({'event':json.loads(b),'answer':'ACK '+json.loads(b)['event_id'],'owner':'caller'},separators=(',',':'))+'\n').encode() for b in restored)
        d=json.loads((p/'turn-1-answer.txt').read_text());d={**d,'authorized':d['reason']=='AUTHORIZED'}
        out=render(resolve(d,raw),raw,hashlib.sha256(raw).hexdigest());grade(json.dumps(out))
        assert check_reason({'distinct_approvers':1,'approver_group':'violet'},out,d['reason'])=='PASS'
        assert out==json.loads((base/'rendered.json').read_text())
        assert len(flow.deliver(head)['deliveries'])==49
        return {'classification':'Offline assembled lifecycle with recorded V7 decision; not fresh native pair',
            'exact_final_matches_v7':True,'ack_records':49,'new_native_calls':0,
            'recorded_native_source_sha256':status['native_events_sha256'],'seconds':time.perf_counter()-start,
            'object_io':store.metrics,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path('engine/prototype/passive_workflow.py'),Path('engine/prototype/completion_ledger.py')]},
            'limits':['No new model behavior evidence','Receipt offering not Codex UI delivery',
                      'Quadratic validation and exact-source duplication charged','Qualified passive contract only']}


if __name__=='__main__':
    result=run();Path(__file__).with_name('ASSEMBLED_W50_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
