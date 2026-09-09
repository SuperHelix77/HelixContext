"""Bound first-turn registration facts; no global registry or semantic authority.

Research adapter. Use only after ResearchSession's caller-side activation succeeds.
It changes the prompt and therefore requires a new benchmark release.
"""
import hashlib


def attach(session, task):
    if not isinstance(task, str) or not task:
        raise ValueError('Nonempty task required')
    if session.turns or session.skill is None:
        return task
    record = session.registration
    if not isinstance(record, dict) or not session.thread or record.get('thread_id') != session.thread:
        raise ValueError('Registration is not bound to this native thread')
    digest = hashlib.sha256(session.skill.read_bytes()).hexdigest()
    if record.get('skill_sha256') != digest:
        raise ValueError('Attached skill changed after registration')
    # Do not interpolate historical content or claim a global/post-compaction state.
    prefix = ('Caller preflight: the attached Helix Context skill has been activated '
              'and verified in this task-local registry for this native thread. '
              'Caller owns registration and its persistence; do not repeat activation '
              'or search for the runtime. This establishes current task-local '
              'registration only, not global or future compaction recovery. '
              'Ordinary tools, semantic review and escalation remain available.\n')
    return prefix + task
