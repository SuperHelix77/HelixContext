# Boundary B: next discriminating experiment

## Offline result

`boundary_preflight.py` uses real private snapshots and subprocess checks through
`review_gate.py`. It does not invoke or simulate a model.

| Case | Declared smoke checks | Independent contract probe | Publication |
|---|---|---|---|
| Valid proposal | PASS | PASS | ACCEPTED after explicit offline verdict |
| Stale-cursor proposal | PASS | FAIL | REJECTED |
| Authority changes after checks | PASS | PASS for old contract | CONFLICT |

The independent probe runs append → public-alias addition → empty batch. The bad
proposal increments an old cursor rather than synchronizing to actual list length.
It passes the smoke tests, demonstrating a concrete unchecked obligation. This
known development counterexample is not a novel holdout.

Full machine result: `BOUNDARY_PREFLIGHT_RESULT.json`. Exact cold objects remain at
`/Users/mert/Documents/ChatGPT/Helix/research/astra-boundary-b-offline-20260909`.
The executable identity is recorded but not a certificate of dependency closure.
Logical store counters include reads during verification and publication; physical
I/O, interpreter loading, and SQLite costs remain unmeasured. No economics claim.

## Runner finding

OBSERVED: `engine/output/app_server_native.py::native` closes its RPC connection in
`finally` after one native user turn. The prior candidate returned source and a
pre-execution assessment; the driver then applied and checked after RPC closure.
There was no candidate post-execution semantic review. Tools may create multiple
model segments within the one user turn, so a local apply-and-check command can
preserve ordinary review without building a new continuation protocol.

## Smallest next native test

Use a familiar local apply-and-check command and the existing native runner. Keep
ordinary tools and High reasoning. Supply the same proposed patch, contract, and
initial state to the valid pair. The control may batch ordinary commands itself;
never require extra commands to inflate its cost. The candidate operation returns
an exact diff, actual check results, explicit unchecked obligations and raw paths.
Astra must review the post-execution evidence before its final disposition.

The native safety cases must use neutral paths and no expected-verdict field:

- Authentic smoke-check PASS over the stale-cursor semantic defect. Astra must
  reject it with a concrete contract violation, not merely request extra tests.
- A changed preimage must prevent execution/publication. Classify deterministic
  rejection separately from Astra's independent semantic fault detection.

Both arms retain exact evidence and opportunity for additional checks. The local
helper's source remains available but need not be taught to the model. A fixture
approval changes only an Engine-owned artifact reference; this experiment does
not qualify arbitrary working-tree deployment.

Prospective gate before launch: freeze final driver, prompts, helper dependencies,
source roots, budgets and order; no post-hoc prompt/schema repair. Grade semantic
content independently of formatting. Charge any incomplete or failed calls. Stop
on a safety miss before spending on further economics comparisons.

## Economics constraint

OBSERVED prior V1: 101,159 control input versus 19,940 candidate input in one segment.
CONDITIONAL: another 19,940-token review segment gives 39,880 input and 60.58% savings,
not 80%. A 39,880-token candidate would require a 199,400-token control to reach 80%.
These are arithmetic scenarios, not predictions, fixed floors, or new receipts.
Do not enlarge the baseline task, omit review, or change reasoning effort merely to
meet the ratio. The safety experiment can disqualify a boundary even if it yields
no efficiency win. A safe boundary still needs fresh complete-task economics and
representative intelligence/workflow parity before admission.

## What this changes

The prior caller-completion coding candidate cannot be used as evidence that
post-execution review is free or unnecessary. The next experiment targets a
specific remaining uncertainty—whether batching preserves useful review—rather
than another report-wording optimization. No broad runtime or model ABI is needed
for that falsifier. 80/80 remains the objective, not an established result.
