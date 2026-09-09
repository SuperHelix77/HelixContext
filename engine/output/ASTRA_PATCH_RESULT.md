# Astra High: independent transactional repair regresses input

**Do not admit source-plus-preflight as a default policy for small novel coding
repairs.** This development pair saved 6.35% native output but used 29.66% more
native input. Both arms passed the finite behavioral checks. No Astra freeze.

| Metric | Native control | Skill + caller preflight | Savings |
|---|---:|---:|---:|
| Native input including cached | 98,251 | 127,397 | -29.66% |
| Native output including reasoning | 1,464 | 1,371 | 6.35% |
| Cached input subset | 76,160 | 115,072 | — |
| Uncached input | 22,091 | 12,325 | 44.21% |
| Reported reasoning subset | 41 | 61 | — |
| Command calls | 4 | 4 | 0% |
| Recorded terminal bytes | 5,747 | 6,874 | -19.61% |
| Native elapsed seconds | 93.95 | 64.96 | 30.86% |
| Original + independent contract checks | PASS | PASS | — |

Combined native usage: 225,648 input / 2,835 output. Cached input is included,
not added again. Lower uncached traffic and elapsed time do not erase the failure
of the separate native-input target or establish a monetary saving. Caller
preflight is separately metered in the receipt; initial fixture setup, grading,
parent research, complete server billing and physical I/O remain unmeasured.

## What this tested

A new coding task, distinct from source selection/copy: repair a queue whose
cursor and items partially mutate before validation/iteration failures. Public
contract requires exact int validation, identity preservation, one-pass iterable
consumption, rollback on invalid values/iterator exceptions, and subsequent
successful calls. Both arms retain High, normal tools and required post-edit
execution. Candidate receives native Helix skill attachment plus exact source,
contract and a caller-executed initial failing test receipt. Small inputs bypass
Memory/Reducers/Plans; Engine does not generate the patch or semantic answer.
This tests a small-task admission policy, not the full integrated selector stack.

Control reproduced the failure, repaired the code and added five tests. Candidate
also repaired the code, but reread source and the attached skill despite the
supplied exact view, then read source/tests again. Both issued four commands.
Thus early source inclusion did not remove the observed inspection workflow;
it added duplicated context. This is an observed trajectory, not a claim about
private cognition or an irreducible reasoning bound. One pair cannot estimate a
stable effect distribution.

## Evaluator correction, not model failure

The prompt explicitly allowed adding tests. The original byte-identical-test-file
gate incorrectly rejected control's additions, despite successful behavioral
checks. Original stopped results are retained unchanged and hash-bound. A separate
correction checks preservation of original test ASTs, independently runs the exact
untouched original suite in a temporary directory, runs the frozen external
contract checks and runs the agent's complete suite. Candidate prompt, sources,
High and limits remained frozen; control was not rerun. One remaining candidate
call followed the recorded correction. This is **evaluator-corrected development
evidence**, not untouched preregistration or a holdout. The original runner is
retained as historical reproduction; its invalid whole-file gate is superseded
by `patch_gate_followup.py` and must not be used for new qualification unchanged.

Raw native event hashes and final cumulative counters were independently checked
against both status receipts. Neither raw stream recorded an error notification.
All 229 engineering tests passed, including the additive-test gate and a HUD fix
that tolerates unfamiliar report row formats without inventing a PASS.

## Decision

Sol's bounded 88.10/88.98 freeze remains unchanged. Astra's previous selection
transfer was 67.35/65.78; this coding pair is -29.66/6.35. Do not multiply or average
these into a product claim. Keep the small-coding policy unqualified and prefer
native execution for this currently unsupported class. No global routing setting
was changed by this report. Future work must demonstrate a different execution
boundary or independent workflow benefit before another native tuning run.

The three-model representative matrix, native long-horizon/future-relevance
trajectory, failure recovery parity and 80/80 objective remain open. These finite
checks do not establish universal intelligence or agentic no-loss.

[Machine-readable evidence and source receipt references](ASTRA_PATCH_RESULT.json).
