# Isolated attempt and semantic review gate — offline audit

Status: **OBSERVED engineering checks only; native experiment not launched.**

## Why this exists

Arena's preferred boundary preserves a semantic review after execution. The earlier
caller fault audit also exposed publication races and failed proposals left in the
working file. A review turn cannot undo a lost edit. This research-only gate makes
one narrower publication boundary testable before another model call: immutable
candidate files plus an atomic update of an Engine-owned version reference.

It is not activated by any production policy, skill, HUD, or benchmark driver.
Existing frozen Sol code and the native caller-patch receipts are unchanged.

## Implemented boundary

1. Caller binds a task root and monotonically increasing revision. Exact files are
   content-addressed; the prototype supports flat filenames only.
2. A unique attempt is durably STARTED before checks. Candidate files are frozen
   and copied into a private attempt directory. Checks retain exact raw evidence.
3. Failed checks or modified snapshot files cannot produce AWAITING_REVIEW.
   A successful process result never advances the task head by itself.
4. The trusted caller supplies an explicit semantic verdict and retained evidence.
   The gate verifies the attempt evidence matches the task, revision and candidate.
5. Approval updates the head and attempt status in one SQLite transaction, only if
   both the original root and revision still match. A competing update or ABA
   transition causes CONFLICT. Rejection leaves the head unchanged.
6. Interrupted STARTED attempts cannot be executed again under the same identity.
   They require explicit reconciliation; automatic recovery is not implemented.

The review API records a trusted caller assertion. It does not authenticate a
model, implement semantic review, or establish that a review was adequate.

## Verification

Command:

```sh
python3 -m pytest engine/prototype/test_review_gate.py engine/prototype/test_checked_steps.py -q
```

**OBSERVED: 21 passed.** Real local subprocesses exercise success, failure, snapshot
mutation, interruption after a side effect, and concurrent approvals. Gate tests
also cover semantic rejection, stale preflight, ABA, corrupt cold data, mismatched
intact evidence, wrong task scope, unsafe path identities, restart, and no replay.
These are deterministic engineering tests, not model tasks or capability parity.

## Explicit limits

- Atomicity covers the Engine-owned SQLite head, not arbitrary mutable filesystem
  deployment. No caller working files are changed by this gate.
- Processes are not sandboxed. External side effects, uncooperative writers, and
  mutation outside the captured snapshot are not rolled back or fully detected.
- Environment labels and recorded argv are not complete dependency closure.
  Executables, external imports, environment changes and undeclared dependencies
  remain unqualified. Hostile storage writers and power-loss durability are not
  certified by these tests.
- Stored candidates are authoritative exact bytes; post-check snapshot comparison
  is not proof that a hostile checker never transiently changed an input.
- STARTED records preserve uncertainty, but there is no automatic reconciliation.
- Store counters before receipt publication and snapshot bytes written are exposed;
  final receipt, SQLite, physical I/O and full recovery costs are not fully charged.
  No complete-cost claim follows from these counters.

## Next native boundary experiment: entry gates

Before native calls, bind the fixture's full declared check inputs in the isolated
snapshot, retain the ordinary Astra post-execution review in both arms, and test
rejection of a mechanically passing semantic defect offline. Deployment back into
an arbitrary working tree is outside this prototype and must not be presented as
solved. Any benchmark using only Engine-owned artifact publication must disclose
that scope rather than substituting it for the full coding-workflow objective.

The matched native comparison must charge initial setup, execution, semantic
review, evidence expansion, reporting and failures; retain reasoning and tools;
and measure input, cached/uncached input, and output independently. Safety arms do
not enter the savings denominator. Stop on stale acceptance, unauthorized work,
missed semantic defect, denied review/evidence or duplicated effects.

Latest coding results remain V1 **80.29% input / 65.90% output** and V2 **80.18% /
46.91%**, bounded development fixtures without candidate post-execution review.
Neither establishes the requested 80/80 with intelligence and workflow parity.
