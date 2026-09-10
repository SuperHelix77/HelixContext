"""Ordered passive/model completions; caller-only, no inference or effect executor.

Existing passive and native benchmarks are unchanged. Caller pins authority/head
outside the mutable index, serializes a workflow, and retains in-flight native
handles across crashes. This adapter commits completed interactions only. Native
capture is trusted caller input, not a cryptographic hosted-service attestation.
Task-state snapshots remain evidence; no stored prose is executed as authority.
"""
import base64
import hashlib
import json
import re

from completion_ledger import EMPTY
from workflow_memory import encode, identity

VERSION = 'helix.mixed-completion.v1'


def digest(raw): return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    result = {}
    for k, v in pairs:
        if k in result: raise ValueError('Duplicate JSON key')
        result[k] = v
    return result


def event(raw):
    if not isinstance(raw, bytes): raise ValueError('Exact event bytes required')
    e = json.loads(raw, object_pairs_hook=unique)
    if (not isinstance(e, dict) or set(e) != {'turn','event_id','data','request'}
            or type(e['turn']) is not int or e['turn'] < 1
            or e['event_id'] != f"E{e['turn']:02d}" or not isinstance(e['request'], str)):
        raise ValueError('Invalid caller event identity')
    return e


def passive(e):
    return e['request'] == (f"Record this event for the ongoing workflow. Reply ACK {e['event_id']}. "
                            'No other action is requested at this turn.')


def next_action(*, unresolved_semantics, pending_mechanics, model_final_pending):
    """Route already established obligations, never classify natural-language text.

    These are current-checkpoint obligations, not every historical open question.
    Inputs come from the trusted caller/model result, never an untrusted event's
    suggested route. A no-action record can preserve background questions as data.
    """
    if (not isinstance(unresolved_semantics, list) or not isinstance(pending_mechanics, list)
            or any(not isinstance(x, str) or not x.strip() for x in unresolved_semantics + pending_mechanics)
            or type(model_final_pending) is not bool):
        raise ValueError('Explicit scoped obligations required')
    if unresolved_semantics: return 'MODEL_SEMANTIC_DECISION'
    if pending_mechanics: return 'ENGINE_MECHANICS'
    if model_final_pending: return 'MODEL_FINAL_RESPONSE'
    return 'DELIVER_COMPLETED_RESPONSE'


class MixedWorkflow:
    def __init__(self, ledger, workflow, authority_root, initial_state):
        identity(workflow, authority_root)
        if not re.fullmatch('[0-9a-f]{64}', authority_root): raise ValueError('Pinned authority required')
        self.ledger = ledger
        self.store = ledger.memory.store
        self.initial_state = self._ref(initial_state)
        self.scope = digest(encode([VERSION, workflow, authority_root, self.initial_state]))

    def _read_ref(self, ref):
        if (not isinstance(ref, dict) or set(ref) != {'sha256','bytes'}
                or type(ref['bytes']) is not int or ref['bytes'] < 0):
            raise ValueError('Exact source reference required')
        raw = self.store.get(ref['sha256'])
        if len(raw) != ref['bytes']: raise ValueError('Source length mismatch')
        return raw

    def _ref(self, ref):
        self._read_ref(ref)
        return dict(ref)

    def _guard(self, binding, current_binding):
        if not isinstance(binding, str) or not re.fullmatch('[0-9a-f]{64}', binding):
            raise ValueError('Explicit caller binding required')
        if not callable(current_binding) or current_binding() != binding:
            raise ValueError('Stale or unavailable caller binding')

    def _append(self, raw, answer, owner, native, after_state, *, expected_head, binding, current_binding):
        self._guard(binding, current_binding)
        e = event(raw)
        # The payload chain alone does not verify referenced state/native objects.
        # Validate those references before extending the authenticated transcript.
        packets = self.recover(expected_head)
        if native is not None and any(
                p['event_id'] != e['event_id'] and p.get('native') is not None
                and (p['native']['thread_id'],p['native']['turn_id']) == (native['thread_id'],native['turn_id'])
                for p in packets):
            raise ValueError('Native turn already belongs to another checkpoint')
        # On a late duplicate, preserve the original pre-state and payload while
        # CompletionLedger keeps the latest committed head as the returned head.
        prior = next((x for x in packets if x['event_id'] == e['event_id']), None)
        before = prior['before_state'] if prior else packets[-1]['after_state'] if packets else self.initial_state
        self._ref(before)
        after = self._ref(after_state) if after_state is not None else before
        if owner == 'engine' and after != before: raise ValueError('Passive event cannot rewrite task state')
        packet = {'schema':VERSION, 'event_id':e['event_id'], 'ordinal':e['turn'],
                  'event_base64':base64.b64encode(raw).decode(), 'event_sha256':digest(raw),
                  'before_state':before, 'after_state':after, 'completion_binding':binding,
                  'answer_owner':owner, 'answer_base64':base64.b64encode(answer).decode(),
                  'answer_sha256':digest(answer), 'native':native}
        payload = encode(packet)
        self._guard(binding, current_binding)
        # SQLite commits ordinal/id/head atomically. Caller serialization and
        # effect-level CAS are separate; this is not a concurrent-host guarantee.
        receipt = self.ledger.ingest(self.scope,e['event_id'],payload,
                                     expected_head=expected_head,sequence=e['turn'])
        # A crash retry may carry the original parent, even EMPTY. The ledger
        # returns the live head; the caller must not restore a stale prefix state.
        current_state = self.recover(receipt['head'])[-1]['after_state'] if receipt['replayed'] else after
        return {**receipt, 'engine_active':True, 'answer':answer, 'answer_owner':owner,
                'checkpoint_after_state':after, 'current_state':current_state,
                'status':'CHECKPOINT_RECORDED', 'model_calls_added':0}

    def record_ack(self, raw, *, expected_head, binding, current_binding):
        e = event(raw)
        if not passive(e): raise ValueError('Unresolved request requires the model')
        return self._append(raw, ('ACK '+e['event_id']).encode(), 'engine', None, None,
                            expected_head=expected_head,binding=binding,current_binding=current_binding)

    def record_model(self, raw, response_ref, *, thread_id, turn_id, after_state,
                     expected_head, binding, current_binding):
        """Extract original final directly from a bound, completed native stream.

        No replacement-answer parameter or output normalization. Supplied stream
        may be a captured prefix up to completion; it is archived immutably.
        It must originate from the caller's real native adapter in live use.
        """
        self._guard(binding,current_binding)
        identity(thread_id,turn_id)
        raw_stream = self._read_ref(response_ref)
        reference = dict(response_ref)
        finals = []; completed = False
        for line in raw_stream.splitlines():
            x = json.loads(line, object_pairs_hook=unique); p = x.get('params', {})
            if p.get('threadId') != thread_id: continue
            if p.get('turnId',p.get('turn',{}).get('id')) != turn_id: continue
            if x.get('method') == 'item/completed':
                item = p['item']
                if finals and item.get('type') != 'reasoning':
                    raise ValueError('New visible evidence after final response')
                if item.get('type') == 'agentMessage' and item.get('phase') == 'final_answer':
                    if completed: raise ValueError('Final appeared after completion')
                    finals.append(item)
            if x.get('method') == 'turn/completed':
                if completed or not finals or p['turn'].get('status') != 'completed':
                    raise ValueError('Invalid or failed native completion')
                completed = True
        if not completed or len(finals) != 1 or not isinstance(finals[0].get('text'),str) or not finals[0]['text']:
            raise ValueError('One complete native final required')
        answer = finals[0]['text'].encode('utf-8')
        native = {'source':reference,'thread_id':thread_id,'turn_id':turn_id,
                  'item_id':finals[0]['id'],'authority':'trusted native capture; semantic correctness not established'}
        return self._append(raw,answer,'model',native,after_state,expected_head=expected_head,
                            binding=binding,current_binding=current_binding)

    def recover(self, head):
        """Exact ordered transcript and state after restart; no actions executed."""
        result=[]; previous=self.initial_state
        for ordinal, row in enumerate(self.ledger.recover(self.scope,expected_head=head),1):
            p = json.loads(row['raw']); raw = base64.b64decode(p['event_base64'],validate=True)
            answer = base64.b64decode(p['answer_base64'],validate=True); e=event(raw)
            if (p['schema'] != VERSION or p['ordinal'] != ordinal or e['turn'] != ordinal
                    or e['event_id'] != row['event'] or p['event_id'] != row['event']
                    or p['before_state'] != previous or digest(raw) != p['event_sha256']
                    or digest(answer) != p['answer_sha256']):
                raise ValueError('Mixed transcript/state mismatch')
            self._ref(p['after_state'])
            if p['answer_owner']=='engine':
                if not passive(e) or answer != ('ACK '+e['event_id']).encode() or p['native'] is not None or p['after_state'] != previous:
                    raise ValueError('Invalid passive completion')
            elif p['answer_owner']=='model':
                self._ref(p['native']['source'])
            else: raise ValueError('Unknown answer owner')
            result.append({**p,'event_bytes':raw,'answer_bytes':answer,'receipt':row['receipt']})
            previous=p['after_state']
        return result
