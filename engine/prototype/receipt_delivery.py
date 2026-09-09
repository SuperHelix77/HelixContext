"""Read-only Engine receipt feed for CLI/HUD and future harness adapters.

Pinned snapshot and cursor give deterministic replay. Consumers must deduplicate
delivery_id; the feed does not claim that network delivery or UI rendering occurred.
It never fabricates model messages or executes stored payloads.
"""
import argparse
import base64
import hashlib
import json
from completion_ledger import CompletionLedger
from evidence import Store
from workflow_memory import Memory, encode


def page(ledger, scope, head, *, offset=0, limit=50):
    if type(offset) is not int or offset < 0 or type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError('Invalid delivery cursor')
    records=ledger.recover(scope,expected_head=head)
    if offset > len(records):raise ValueError('Cursor outside pinned snapshot')
    deliveries=[]
    for ordinal,record in enumerate(records[offset:offset+limit],offset):
        # Payload remains exact evidence. No inferred PASS or model authorship.
        deliveries.append({'delivery_id':hashlib.sha256(encode([scope,record['receipt']])).hexdigest(),
            'sequence':ordinal,'owner':'helix-engine','kind':'completion-record',
            'event_id':record['event'],'receipt':record['receipt'],
            'payload_base64':base64.b64encode(record['raw']).decode('ascii'),
            'payload_sha256':hashlib.sha256(record['raw']).hexdigest(),
            'semantic_correctness':'not established by delivery'})
    next_offset=offset+len(deliveries)
    return {'schema':'helix.delivery.v1','scope':scope,'snapshot':head,
            'deliveries':deliveries,'next_offset':next_offset,'has_more':next_offset<len(records),
            'delivery_status':'offered; consumer acknowledgement not established'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store',required=True);parser.add_argument('--scope',required=True)
    parser.add_argument('--head',required=True);parser.add_argument('--offset',type=int,default=0)
    parser.add_argument('--limit',type=int,default=50);args=parser.parse_args()
    # CLI uses existing store but constructs Memory, which may initialize schema.
    ledger=CompletionLedger(Memory(Store(args.store)))
    print(json.dumps(page(ledger,args.scope,args.head,offset=args.offset,limit=args.limit)))


if __name__=='__main__':main()
