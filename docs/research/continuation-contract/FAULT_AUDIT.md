# Caller patch failure audit: publication and recovery remain unqualified

**OBSERVED — injected offline faults, zero native calls.** This audit executes the
actual frozen V1 caller-stage AST unchanged, starting at its protected-file check.
It uses the real checker. No mock model usage, fabricated native receipt, production
Engine change, or amendment of the earlier pair is involved. Driver/stage/audit
hashes and all outcomes are recorded in `FAULT_AUDIT_RESULT.json`.

| Condition | Caller stage result | Source/state outcome |
|---|---|---|
| No fault | PASS | Exact proposed repair present; contract still bound |
| Source stale before validation | Rejects | Intervening edit preserved |
| Contract changes while checker returns | **PASS: gap** | Current contract no longer matches bound authority |
| Source changes after validation, before replace | **PASS: gap** | Intervening edit overwritten |
| Proposed repair fails semantic checker | Stops | Failed proposed source remains in task workspace |
| Checker unavailable after replacement | Stops | Proposed source remains without verification |

The first stale-source gate works. The narrow binding window and post-check
publication closure do not cover the injected races. Failing checks do not produce
a success marker, which is correct, but the stage has already replaced the file.
It neither rolls back nor continues semantic recovery. Therefore it cannot justify
a complete no-workflow-loss claim on failure paths.

These faults were not observed in the successful native pairs. Their input/output
measurements and finite check passes stand. Do not retroactively call those native
runs failures, and do not generalize their successful single-writer trajectory to
concurrent user edits, interruptions or automatic recovery. The original benchmark
budget deliberately allowed no recovery calls; that is a research stop policy,
not a deployable replacement for the user's complete workflow.

## Consequence for the next architecture step

Do not launch another native call merely to see whether the model notices these
mechanical races. The deterministic caller must first make them impossible within
its declared ownership boundary or reject unsupported execution modes.

The smallest coherent publication design is:

1. Bind an immutable input/authority/checker/environment state root.
2. Stage Astra's exact proposed bytes in an isolated attempt workspace.
3. Run required checks there; retain exact failed artifacts/logs without changing
   the committed workflow state.
4. Publish a successful immutable artifact/receipt only if the authoritative state
   still equals the bound base, using a transactional compare-and-swap over the
   Engine-owned state reference. A changed base returns a conflict delta.
5. On failure, return the actual unresolved semantic/test delta for normal recovery;
   charge that call. Never rerun side effects silently or invent a semantic repair.

A mutable user-workspace file is not an atomic compare-and-swap reference.
Rechecking its hash immediately before `os.replace` merely shortens a race window;
it does not close it. Advisory locks only work if all writers honor them. A future
implementation must either own an isolated versioned workspace/reference or state
and enforce its writer-coordination assumption. It must not claim protection from
arbitrary uncooperative writers by adding another hash check.

Existing evidence-store and named-plan machinery may supply immutable attempts and
transactional receipt publication internally. They must not become another
model-facing generic API or cold-plan lesson. This audit does not implement or
qualify that integration, and no production route is activated.

Before native transfer: falsify stale base, changed authority, failed checker,
interrupted staging, duplicate publication and exactly-once recovery disposition at
the caller boundary. Account for storage, hashes, checker and recovery work. Then
measure a fresh paired complete task. The 80/80 target is unchanged; discarding
necessary recovery to meet it would violate the primary objective.
