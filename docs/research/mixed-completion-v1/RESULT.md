# Mixed W50 completion: offline integration candidate

**OBSERVED engineering result:** the new caller-only `mixed_workflow.py` records
46passive ACKs and four scripted semantic checkpoints in one ordered ledger,
without changing the original event numbers or answer bytes. It does not invoke
a model, infer semantics, execute stored prose, or alter the frozen native pilots.

34 focused tests pass. They cover exact50event restart, stale bindings, conflicting
duplicates, index rollback, failed publication, old-reference corruption, invalid
native completion, wrong native identity, reuse of one native turn for another
checkpoint, and the distinction between mechanics and a required model final.

Two previously audited **actual Astra native streams** were separately ingested
and recovered. Their original final bytes/hashes remained unchanged. This checks
compatibility with real native event formatting; it is neither a new model run
nor independent semantic/capability replication.

## What changed

The historical passive adapter correctly rejected an ACK following an unrecorded
semantic event as a sequence gap. The new adapter uses a common completed-event
ordinal for both owners. Passive records preserve the current task-state reference.
Model records carry exact final text extracted from a caller-bound native stream,
the thread/turn/item identity and state references. There is no replacement-answer
argument. State snapshots are evidence, not machine-certified semantic conclusions.

Late duplicate delivery now separates `checkpoint_after_state` from `current_state`:
replaying E01 after E50 returns E50's current state and head, rather than rolling
the caller back. One native turn cannot be relabeled as a different checkpoint.
Native failure, duplicate/incomplete final, or new visible evidence after the final
prevents committing that response as a completed native checkpoint.

`next_action` routes explicit, current-checkpoint obligations supplied by the
trusted caller/model result. It does not parse arbitrary prose to decide that
reasoning is unnecessary:

    unresolved semantics        -> model semantic decision
    pending authorized mechanics -> Engine mechanics
    model final still required   -> model final response
    otherwise                    -> deliver completed response

Historical open questions can remain in the exact task-state snapshot while a
separately authorized no-action event is merely recorded. Recording data does not
answer those questions or change authority. This distinction prevents repeatedly
waking a model just because a question is awaiting later clarification.

## Hostile finding and correction

The initial adapter validated ledger payloads but did not revalidate references
from older records before appending. Two deliberately hostile tests corrupted an
older task-state object or native capture, then submitted another ACK. Both tests
**failed as expected for the defective implementation**: the ACK was accepted.

The corrected append path validates the mixed transcript's state/native references
before extending it. Both attacks now reject without advancing the committed head.
The first calibration remains retained as superseded evidence; it is not used to
advertise the corrected implementation's cost.

## Measured overhead, not model economics

| Corrected offline calibration | Result |
|---|---:|
| New model calls | 0 |
| Scripted ordered events / semantic placeholders | 50 / 4 |
| Complete calibration wall time | 0.2462s |
| Append-phase logical object reads, including initialization | 3,113,166B |
| Append object read operations | 6,359 |
| Append object writes | 61,949B |
| Restart logical object reads | 65,303B |
| Restart object read operations | 155 |

These cumulative append counters include44bytes of initial-state validation before
the per-event measurements. The public verifier accounts for that setup read.
The previous incomplete check read3,006,583B in the append phase; reference closure
adds106,583B on this fixture. Timing is a single local observation, not a latency
distribution. Calibration uses constant caller-binding callbacks except in hostile
tests. Live dependency-check cost is additional. Python/SQLite/metadata and physical
I/O, energy, and full research costs are not measured by the Store counters.

The underlying ledger still verifies the prefix; append work over a long stream
is quadratic, and this adapter adds reference validation. It is small at50events,
not a demonstrated production-scale solution. No unchecked mtime cache or weaker
integrity guarantee was substituted to hide the cost.

## Economic and native-admission verdict

**No new token savings or capability parity is claimed.** The most recent native
economic result remains the separate [cold pair](../cold-native-final-v1/RESULT.md):
78.29% input/61.75% output. This adapter resolves an observed lifecycle obstacle
to the harder W50 experiment; it does not itself make unresolved reasoning cheap.

Before a live mixed pair:

1. Freeze the four genuine semantic tasks and independent behavioral graders.
   Retain all ordinary tools, effort, clarification and model-written finals.
2. Bind each original event, pre-state and native request **before** dispatch;
   persist its existing native handle. This completion adapter alone does not
   establish that a capture answered the right task. On uncertain delivery,
   inspect/recover that same request; never automatically buy a new inference.
3. Keep external-effect idempotency, consumer acknowledgement and cross-process
   serialization explicit. SQLite completion atomicity does not provide exactly
   once side effects, complete caller authority, or a hostile-host guarantee.
4. Budget actual internal segments, normal final output, live binding costs and
   all50control events. Four checkpoints do not imply four model segments.

**Status: offline integration candidate; not admitted for a new native benchmark
yet.** There is no new installed hook, kernel, model policy, release median or
normal Codex-app pre-inference integration. The Engine stays available on model
routes; no model/task family was disabled. Capability and80/80 remain open.
