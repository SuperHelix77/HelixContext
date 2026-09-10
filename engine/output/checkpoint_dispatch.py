"""Durable request binding before turn/start; no automatic inference retry.

Caller-only research adapter. An exclusive fsynced marker is written before the
transport callback. Missing acknowledgement means outcome unknown, never resend.
Caller retains the ticket reference outside this directory. This is not rollback
protection against a hostile host deleting the whole journal and its external pin.
Native streams must come from the registered transport, not arbitrary evidence.
"""
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import re

VERSION='helix.checkpoint-dispatch.v1'


def encode(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    d={}
    for k,v in pairs:
        if k in d:raise ValueError('Duplicate event key')
        d[k]=v
    return d


def durable_mkdir(path):
    path=Path(path)
    if not path.parent.exists():durable_mkdir(path.parent)
    try:path.mkdir()
    except FileExistsError:
        if not path.is_dir():raise
        return
    fd=os.open(str(path.parent),os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


def durable_new(path,raw):
    """Never replace an attempted dispatch, including a partial failed write."""
    with Path(path).open('xb') as f:
        f.write(raw);f.flush();os.fsync(f.fileno())
    fd=os.open(str(Path(path).parent),os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


class Journal:
    def __init__(self,root):
        self.root=Path(root).resolve();durable_mkdir(self.root)

    def prepare(self,*,workflow,event_id,event_bytes,pre_head,pre_state,expected_request,expected_rpc_id,binding):
        if not isinstance(event_bytes,bytes) or not event_bytes:raise ValueError('Exact event required')
        event=json.loads(event_bytes,object_pairs_hook=unique)
        if not isinstance(event,dict) or event.get('event_id')!=event_id:raise ValueError('Prepared event identity mismatch')
        if any(not isinstance(x,str) or not x for x in [workflow,event_id]):raise ValueError('Identity required')
        if any(not isinstance(x,str) or not re.fullmatch('[0-9a-f]{64}',x) for x in [pre_head,binding]):
            raise ValueError('Caller-pinned roots required')
        if (not isinstance(expected_request,dict) or not expected_request.get('threadId')
                or not expected_request.get('model') or expected_request.get('effort') not in ['high','xhigh']
                or not isinstance(expected_request.get('input'),list) or not expected_request['input']):
            raise ValueError('Exact native request and effort required')
        if type(expected_rpc_id) is not int or expected_rpc_id<1:raise ValueError('Exact next RPC identity required')
        payload={'schema':VERSION,'workflow':workflow,'event_id':event_id,
            'event_base64':base64.b64encode(event_bytes).decode(),'event_sha256':digest(event_bytes),
            'pre_head':pre_head,'pre_state':pre_state,'request':expected_request,
            'rpc_id':expected_rpc_id,'binding':binding}
        raw=encode(payload);key=digest(encode([VERSION,workflow,event_id]));folder=self.root/key
        durable_mkdir(folder);path=folder/'ticket.json'
        try:durable_new(path,raw)
        except FileExistsError:
            if path.read_bytes()!=raw:raise ValueError('Conflicting or interrupted checkpoint preparation')
        # Verify the durable bytes, not only the caller's mutable Python object.
        if path.read_bytes()!=raw:raise ValueError('Ticket readback mismatch')
        return {'key':key,'sha256':digest(raw)}

    def ticket(self,reference):
        if not isinstance(reference,dict) or set(reference)!={'key','sha256'}:raise ValueError('Pinned ticket reference required')
        if any(not isinstance(x,str) or not re.fullmatch('[0-9a-f]{64}',x) for x in reference.values()):raise ValueError('Invalid ticket reference')
        folder=self.root/reference['key'];raw=(folder/'ticket.json').read_bytes()
        if digest(raw)!=reference['sha256']:raise ValueError('Ticket binding mismatch')
        value=json.loads(raw)
        if value['schema']!=VERSION or digest(base64.b64decode(value['event_base64'],validate=True))!=value['event_sha256']:
            raise ValueError('Event binding mismatch')
        return folder,value

    def send_once(self,reference,wire,transport,*,current_binding):
        folder,ticket=self.ticket(reference)
        if (not callable(transport) or not callable(current_binding)
                or current_binding()!=ticket['binding']):raise ValueError('Stale dispatch binding')
        # Copy before checking to avoid caller mutation after validation.
        wire=copy.deepcopy(wire)
        if (set(wire)!={'id','method','params'} or type(wire['id']) is not int or wire['id']!=ticket['rpc_id']
                or wire['method']!='turn/start' or encode(wire['params'])!=encode(ticket['request'])):
            raise ValueError('Outgoing native request differs from prepared checkpoint')
        marker={'ticket_sha256':reference['sha256'],'wire':wire,
                'state':'DISPATCH_OUTCOME_UNKNOWN','automatic_resend_allowed':False}
        # Any existing marker blocks another send, even when no reply exists.
        durable_new(folder/'dispatch.json',encode(marker))
        if current_binding()!=ticket['binding']:
            raise ValueError('Binding changed before transport; marker retained, no automatic retry')
        return transport(wire)

    def bind_capture(self,reference,raw_native):
        """Find the reply to this exact request in its trusted native wire stream.

        Does not assert task correctness or authorize another send. A completed
        final is checked separately by MixedWorkflow.record_model.
        """
        folder,ticket=self.ticket(reference)
        marker=json.loads((folder/'dispatch.json').read_bytes(),object_pairs_hook=unique)
        expected_wire={'id':ticket['rpc_id'],'method':'turn/start','params':ticket['request']}
        if marker['ticket_sha256']!=reference['sha256'] or encode(marker['wire'])!=encode(expected_wire):
            raise ValueError('Dispatch marker changed')
        rid=marker['wire']['id']
        path=folder/'capture.json'
        if path.exists():
            old=json.loads(path.read_bytes(),object_pairs_hook=unique)
            if old['ticket']!=reference or digest(raw_native[:old['native_bytes']])!=old['native_sha256']:
                raise ValueError('Conflicting checkpoint capture; preserve original')
            raw_native=raw_native[:old['native_bytes']]
        responses=[]
        events=[]
        for line in raw_native.splitlines():
            x=json.loads(line,object_pairs_hook=unique);events.append(x)
            if type(x.get('id')) is int and x.get('id')==rid and 'method' not in x:responses.append(x)
        if len(responses)!=1 or 'error' in responses[0]:raise ValueError('Native acceptance unresolved or rejected; do not resend')
        turn=responses[0].get('result',{}).get('turn',{}).get('id')
        if not isinstance(turn,str) or not turn:raise ValueError('No accepted native turn identity')
        done=[x for x in events if x.get('method')=='turn/completed'
              and x.get('params',{}).get('threadId')==ticket['request']['threadId']
              and x['params'].get('turn',{}).get('id')==turn]
        if len(done)!=1 or done[0]['params']['turn'].get('status')!='completed':
            raise ValueError('Native task not completed; retain same handle, do not resend')
        record={'ticket':reference,'native_sha256':digest(raw_native),
                'native_bytes':len(raw_native),
                'thread_id':ticket['request']['threadId'],'turn_id':turn,
                'event_sha256':ticket['event_sha256'],'pre_head':ticket['pre_head'],'pre_state':ticket['pre_state']}
        raw=encode(record)
        try:durable_new(path,raw)
        except FileExistsError:
            if path.read_bytes()!=raw:raise ValueError('Conflicting checkpoint capture; preserve original')
        return record


class BoundSend:
    """Instance-local RPC.send interception; no request or prompt rewriting."""
    def __init__(self,rpc,journal,reference,current_binding):
        self.rpc=rpc;self.journal=journal;self.reference=reference;self.current_binding=current_binding
        self.original=None

    def __enter__(self):
        self.original=self.rpc.send
        def send(wire):
            if wire.get('method')=='turn/start':
                return self.journal.send_once(self.reference,wire,self.original,current_binding=self.current_binding)
            return self.original(wire)
        self.rpc.send=send
        return self

    def __exit__(self,*exc):self.rpc.send=self.original


def commit_capture(flow,journal,reference,raw_native,*,after_state,current_binding):
    """Bind a native completion to the original event without regenerating a final."""
    binding=journal.bind_capture(reference,raw_native)
    raw_native=raw_native[:binding['native_bytes']]
    _,ticket=journal.ticket(reference)
    if ticket['workflow']!=flow.scope:raise ValueError('Checkpoint belongs to another workflow scope')
    rows=flow.recover(ticket['pre_head'])
    current_state=rows[-1]['after_state'] if rows else flow.initial_state
    if current_state!=ticket['pre_state']:raise ValueError('Prepared task state differs from checkpoint history')
    raw=base64.b64decode(ticket['event_base64'],validate=True)
    decoded=json.loads(raw)
    if decoded.get('event_id')!=ticket['event_id']:raise ValueError('Event identity differs from prepared slot')
    ref=flow.store.put(raw_native)
    return flow.record_model(raw,ref,thread_id=binding['thread_id'],turn_id=binding['turn_id'],
        after_state=after_state,expected_head=ticket['pre_head'],binding=ticket['binding'],current_binding=current_binding)
