"""Complete semantic handoff around the frozen bound-retrieval primitive.

All models receive the same explicit caller context when semantics are needed.
This does not interpret constraints, lower effort, or authorize external effects.
Existing benchmark drivers remain frozen; integrations must opt into this API.
"""
import hashlib
import json

import bound_retrieval

VERSION = 'helix.context-bound-retrieval.v1'
CONTEXT_VERSION = 'helix.semantic-context.v1'


class ChangedAuthority(ValueError):
    pass


def dispatch(task, store, reference, *, expected_state_root, current_state, semantic):
    """semantic(context) gets exact task, constraints, source and state binding.

    Check again after inference before making its result available. If authority
    changed, retain completed model work for caller reconciliation; never retry it
    automatically. This is a read-only boundary, not atomic external publication.
    The caller must persist returned uncommitted work before restarting a model.
    """
    if not callable(semantic) or not callable(current_state):
        raise ValueError('Trusted caller callbacks required')
    calls = 0
    completed = []

    def snapshot():
        try:
            # Detach mutable references. The same exact snapshot is checked and
            # delivered; a caller changing state later cannot rewrite this packet.
            state = json.loads(json.dumps(current_state(), ensure_ascii=False,
                                           sort_keys=True, allow_nan=False))
            if bound_retrieval.state_root(state) != expected_state_root:
                raise ChangedAuthority('Authority differs from caller-pinned root')
            return state
        except (OSError, ValueError, TypeError, RecursionError) as error:
            raise ChangedAuthority('Authority unavailable, invalid or stale') from error

    def invoke(task_text, source_reference):
        nonlocal calls
        state = snapshot()
        # The inner gate already validates the full authority schema. Keep an
        # independent request/source check at this last pre-inference boundary.
        if (state['task_sha256'] != hashlib.sha256(task_text.encode()).hexdigest()
                or state['source_ref'] != source_reference):
            raise ChangedAuthority('Semantic context binding mismatch')
        context = {'schema': CONTEXT_VERSION, 'task': task_text,
                   'state_root': expected_state_root, 'task_state': state}
        calls += 1
        result = semantic(context)
        completed.append(result)
        snapshot()
        return result

    try:
        result = bound_retrieval.dispatch(task, store, reference,
            expected_state_root=expected_state_root, current_state=current_state, semantic=invoke)
        if result['state'] in ('RESOLVED', 'SEMANTIC_DISPATCHED'):
            snapshot()
    except ChangedAuthority:
        result = {'engine_active': True, 'state': 'HOLD_FOR_RECOVERY',
                  'reason': 'Authority changed at semantic handoff; no publication or automatic retry'}
        if completed:
            result['uncommitted_result'] = completed[-1]
            result['uncommitted_state_root'] = expected_state_root
    result.update(handoff_version=VERSION, semantic_calls=calls)
    return result
