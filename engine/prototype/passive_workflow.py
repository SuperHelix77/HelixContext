"""Bound passive-record workflow; no semantic classification or model invocation.

Caller admits this exact record-and-ACK contract. Free-form or changed requests
return semantic_required with exact incoming evidence. This is not general task
admission. Engine stays active on either path.
"""
import base64
import hashlib
import json
from workflow_memory import encode, identity
from receipt_delivery import page

CONTRACT='helix.passive-record-ack.v1'


class PassiveWorkflow:
    def __init__(self, ledger, workflow, authority_root):
        identity(workflow,authority_root)
        if len(authority_root)!=64 or any(c not in '0123456789abcdef' for c in authority_root):
            raise ValueError('Caller-bound authority digest required')
        self.ledger=ledger
        self.scope=hashlib.sha256(encode([CONTRACT,workflow,authority_root])).hexdigest()

    def accept(self, raw, *, expected_head):
        if not isinstance(raw,bytes):raise ValueError('Exact event bytes required')
        source=self.ledger.memory.store.put(raw)['sha256']
        def pairs(items):
            d={}
            for key,value in items:
                if key in d:raise ValueError('Duplicate JSON key')
                d[key]=value
            return d
        try:event=json.loads(raw,object_pairs_hook=pairs)
        except (ValueError,UnicodeError):event=None
        supported=(isinstance(event,dict) and set(event)=={'turn','event_id','data','request'}
            and type(event['turn']) is int and event['turn']>0
            and event['event_id']==f"E{event['turn']:02d}"
            and event['request']==f"Record this event for the ongoing workflow. Reply ACK {event['event_id']}. No other action is requested at this turn.")
        if not supported:
            return {'engine_active':True,'state':'semantic_required','source':source,
                    'head':expected_head,'model_calls_added':0}
        answer='ACK '+event['event_id']
        payload=encode({'schema':CONTRACT,'source':source,'raw_base64':base64.b64encode(raw).decode(),
                        'answer':answer,'owner':'helix-engine'})
        receipt=self.ledger.ingest(self.scope,event['event_id'],payload,expected_head=expected_head,sequence=event['turn'])
        return {'engine_active':True,'state':'completion_recorded','answer':answer,
                **receipt,'source':source,'model_calls_added':0}

    def deliver(self, head, **cursor):
        return page(self.ledger,self.scope,head,**cursor)

    def exact_events(self, head):
        rows=self.ledger.recover(self.scope,expected_head=head)
        raw=[]
        for row in rows:
            packet=json.loads(row['raw'])
            value=base64.b64decode(packet['raw_base64'],validate=True)
            if hashlib.sha256(value).hexdigest()!=packet['source']:raise ValueError('Source mismatch')
            raw.append(value)
        return raw
