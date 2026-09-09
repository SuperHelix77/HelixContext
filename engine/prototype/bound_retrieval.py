"""Conservative caller boundary for the experimental exact-request adapter.

The caller pins a complete task-state root outside mutable evidence storage.
This release handles only a single closed request with no inherited constraints.
It never decides that a natural-language constraint is irrelevant. A caller that
omits applicable context violates this interface; a hash cannot detect omission.
Returning an answer is read-only. Delivery/publication still needs caller CAS.
"""
import hashlib
import json
import re
import resolved_retrieval

VERSION = 'helix.bound-retrieval.v1'


def state_root(state):
    raw = json.dumps(state, sort_keys=True, ensure_ascii=False,
                     separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def dispatch(task, store, reference, *, expected_state_root, current_state, semantic):
    """Resolve only under a current, externally pinned, complete caller state.

    current_state is a trusted caller callback, never a function from evidence.
    Unknown request/schema or inherited constraints retain semantic execution.
    A stale state or corrupt authoritative source is held for exact recovery.
    """
    if not callable(current_state) or not callable(semantic):
        raise ValueError('Trusted caller state and semantic capabilities required')

    def hold(reason):
        return {'engine_active': True, 'state': 'HOLD_FOR_RECOVERY', 'reason': reason}

    def checked_state():
        state = current_state()
        if not isinstance(expected_state_root, str) or not re.fullmatch('[0-9a-f]{64}', expected_state_root):
            raise ValueError('Missing caller-pinned state root')
        if state_root(state) != expected_state_root:
            raise ValueError('Current authority state differs from caller-pinned root')
        if not isinstance(state, dict) or set(state) != {
            'schema', 'adapter_version', 'task_sha256', 'source_ref', 'active_constraints'
        }:
            raise ValueError('Incomplete task-state schema')
        if state['schema'] != VERSION or state['adapter_version'] != resolved_retrieval.VERSION:
            raise ValueError('Task-state or adapter version changed')
        if not isinstance(task, str) or state['task_sha256'] != hashlib.sha256(task.encode('utf-8')).hexdigest():
            raise ValueError('Task changed')
        if state['source_ref'] != reference:
            raise ValueError('Source binding changed')
        constraints = state['active_constraints']
        if not isinstance(constraints, list) or any(not isinstance(c, str) or not c.strip() for c in constraints):
            raise ValueError('Invalid inherited constraints')
        return state

    try:
        state = checked_state()
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError):
        return hold('Authority unavailable, invalid or stale')
    if state['active_constraints']:
        return {'engine_active': True, 'state': 'SEMANTIC_DISPATCHED',
                'reason': 'Inherited constraints need semantic interpretation',
                'result': semantic(task, reference)}

    # A semantic callback is never run by the low-level adapter until this
    # wrapper has rechecked the caller state following source retrieval.
    pending = object()
    try:
        result = resolved_retrieval.dispatch(task, store, reference, lambda *_: pending)
    except (ValueError, TypeError, RecursionError, OverflowError):
        result = {'engine_active': True, 'state': 'SEMANTIC_DISPATCHED',
                  'reason': 'Request or source exceeds the deterministic parser contract', 'result': pending}
    try:
        checked_state()
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError):
        return hold('Authority changed during retrieval; computed answer withheld')
    if result.get('result') is pending:
        result['result'] = semantic(task, reference)
    if result['state'] == 'RESOLVED':
        result.update(state_root=expected_state_root, gate_version=VERSION,
                      checked_predicates=['bound request', 'bound source', 'no inherited constraints', 'unchanged task state'],
                      unchecked_obligations=['Caller supplied all applicable authority', 'Delivery must compare-and-swap the same state root'])
    return result
