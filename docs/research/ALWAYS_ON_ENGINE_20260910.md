# Always-on Engine; selective optimization, not selective Engine availability

User correction: do not disable Helix Engine for coding or other tasks, on any
model. This supersedes wording in earlier release notes describing unqualified
tasks as Engine-off. It does not authorize known-negative optimizations or removal
of semantic checks to meet token targets.

Engine remains the caller/control boundary. Its existing admission dispatcher can
select ordinary model execution without leaving that boundary. Receipts now state
`engine_active=true` and distinguish `ordinary_model_execution` from
`qualified_optimization`. The legacy `route=native` label remains compatible with
existing callers; it means ordinary model execution within Engine, not Engine shutdown.
These fields clarify actual dispatcher scope; they do not make all optional Memory,
Reducer or Plan features run on every task, and do not prove normal-app deployment.

## Concrete coding fix

New `engine/prototype/semantic_execution.py` separates explicit semantic obligations
from the caller's immutable mandatory step list. The model supplies artifact and
assessment, plus only unresolved semantic questions. The caller already owns tests,
oracle and exact publication; the model need not serialize or rediscover those steps.

The contract runs authorized callbacks against exact artifact bytes, checks current
binding before each step, stops on failed checks, and returns semantic re-entry when
new failure evidence appears. An exception after a possible side effect returns
reconciliation, not automatic retry. Each edit callback must enforce its own atomic
CAS: preflight alone cannot remove a race during execution. Caller receipts are
trusted executor results, never model-supplied claims of mechanical PASS.

The ambiguous old `unresolved` field is rejected, not guessed at. No natural-language
classifier decides which obligations to ignore. Existing frozen benchmark drivers
remain unchanged; a future assembled runner must explicitly adopt the new contract.

## Verification and limits

16 focused admission/execution tests passed, including the same execution contract
under Luna/Sol/Astra labels, semantic questions, failed checks, stale bindings and
uncertain effects. Parameterized labels test model-neutral plumbing, **not actual
model behavior or capability parity**. No new native inference was spent.

This addresses the observed caller-contract failure. It does not erase the coding
attempt's 5,361 output tokens or demonstrate that models stop repeating setup and
verification. Next paired qualification must use the always-on Engine in every
candidate cell, preserve tool/effort/semantic authority, and count ordinary-mode
tasks and all recurring overhead. An unsupported optimization must not falsely
claim a saving, even though Engine remains active.

75/75 release threshold and broader capability/workflow qualification remain open.
The eventual HUD must show **Engine active / policy / component activation / cost**
separately rather than a misleading Engine-off badge for ordinary execution.
