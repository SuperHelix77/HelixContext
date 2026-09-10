# Complete semantic handoff: offline correction

**OBSERVED, source inspection:** `bound_retrieval.py` correctly detects inherited
constraints but calls `semantic(task, reference)`. The callback contract does not
carry those constraints or the checked state root. Callers could capture them
out of band; their delivery was not guaranteed by this interface. Its inherited-
constraint path also returned without checking state after semantic execution.
This is an interface gap, not an observed native model failure.

**IMPLEMENTED / OFFLINE:** New
[`context_bound_retrieval.py`](../../../engine/prototype/context_bound_retrieval.py)
wraps the frozen gate. Existing benchmark sources and manifests stay unchanged.

```text
dispatch(task, store, reference,
         expected_state_root, current_state, semantic)

semantic({schema, task, state_root, task_state})
```

The semantic callback receives a detached exact state snapshot containing source
reference, request hash, adapter/schema versions and all inherited constraints.
The callback must attach the task and constraints once to the ordinary model
turn, retaining tools, effort and exact evidence access. Engine internals need
not enter the model prompt. The caller remains responsible for supplying all
applicable authority; this wrapper cannot detect a constraint omitted upstream.

| Condition | Action |
|---|---|
| Recognized, closed, current request | Existing deterministic execution, no model call |
| Unknown request or inherited constraints | One semantic callback with complete bound context |
| State changes immediately before handoff | Hold; no model call |
| State changes or becomes unreadable during inference | Hold publication; retain uncommitted result with its original root |
| Semantic callback fails | Propagate failure; never retry or claim success |

Completed-but-stale work must be persisted by the caller before any recovery
inference. The wrapper returns it as `uncommitted_result`, never as a publishable
`answer` or `result`. It does not decide whether a new requirement is irrelevant,
execute ledger instructions, or provide atomic external publication. A caller
still needs final compare-and-swap/delivery discipline.

**VERIFIED:** 29 focused tests pass: eight new handoff tests plus 21 existing
bound/exact retrieval tests. They cover exact multiline constraint delivery,
source-note authority separation, snapshot detachment, changes before/during
handoff, unavailable state, missing authority, callback failure without retry,
and both complete fresh paired artifacts continuing to resolve without inference.
Test callbacks are deterministic stubs, not Luna/Sol/Astra. No native capability,
economic or normal Codex-app integration claim is added.

This is a common contract for all models, with Engine active on every route.
It is not automatically wired into frozen native benchmark drivers or the Codex
desktop app. The exact context packet adds serialization/input overhead when
semantic execution is required; that cost is unmeasured natively. No inference
was spent on this correction.

**NEXT:** An integration must consume the complete context packet, persist held
work without a second inference, and supply publication CAS. Only then test a
query-intent interface. Do not infer a coding output fix from retrieval tests.
