import base64
import pytest
from completion_ledger import CompletionLedger,EMPTY
from workflow_memory import Memory
from evidence import Store
from receipt_delivery import page


def test_pinned_pages_restart_and_consumer_deduplication(tmp_path):
    ledger=CompletionLedger(Memory(Store(tmp_path)));head=EMPTY;raws=[]
    for n in range(49):
        raw=('ACK E%02d'%(n+1)).encode()+b'\r\n';raws.append(raw)
        head=ledger.ingest('workflow','e'+str(n),raw,expected_head=head)['head']
    first=page(ledger,'workflow',head,limit=20)
    # New completion cannot change the pinned historical page or its identifiers.
    ledger.ingest('workflow','later',b'new',expected_head=head)
    fresh=CompletionLedger(Memory(Store(tmp_path)))
    assert page(fresh,'workflow',head,limit=20)==first
    consumer={}
    for packet in [first,first,page(fresh,'workflow',head,offset=20,limit=20),page(fresh,'workflow',head,offset=40,limit=20)]:
        for item in packet['deliveries']:
            old=consumer.setdefault(item['delivery_id'],item)
            assert old==item
    assert [base64.b64decode(x['payload_base64']) for x in consumer.values()]==raws
    assert all(x['owner']=='helix-engine' for x in consumer.values())
    assert first['delivery_status'].startswith('offered')


def test_wrong_scope_corruption_and_cursor_fail(tmp_path):
    ledger=CompletionLedger(Memory(Store(tmp_path)))
    root=ledger.ingest('P','e',b'raw',expected_head=EMPTY)['head']
    for kwargs in [{'offset':2},{'offset':True},{'limit':0}]:
        with pytest.raises(ValueError):page(ledger,'P',root,**kwargs)
    with pytest.raises(ValueError):page(ledger,'Q',root)
    (tmp_path/'objects'/root).write_bytes(b'{}')
    with pytest.raises(ValueError):page(ledger,'P',root)
