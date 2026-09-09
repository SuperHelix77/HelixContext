# Initial semantic review: measured cost and next admission constraint

OBSERVED. Read-only audit of the fresh prereview pair, no new native calls.
Reproduce with `python3 docs/research/continuation-contract/prereview_cost_audit.py /path/to/native-prereview-pair-v1-20260909 /tmp/audit.json`.
The script verifies frozen event hashes and reconciles segment input/output/cache
counts with final receipts. Machine evidence: `PREREVIEW_COST_AUDIT.json`.

| Candidate segment | Observable activity | Input | Output |
|---|---|---:|---:|
| 1 | Announcement and file discovery | 19,524 | 95 |
| 2 | Request skill/source/contract/checker read | 19,782 | 161 |
| 3 | Generate and execute supplemental semantic probes | 22,354 | 909 |
| 4 | Return semantic assessment | 23,395 | 287 |

Activity labels describe visible messages and commands, not hidden cognition.
The complete proposal and contract were already in the initial text and appeared
again in the bulk-read output. The skill was attached and later read as a file;
its exact platform serialization is unavailable, so its duplicate token charge
cannot be isolated. Checker source was newly loaded, not a confirmed duplicate.
Do not call all initial 19,524 tokens Helix bootstrap: runtime context is included.

## What this changes

CONDITIONAL arithmetic: deleting segments 1 and 2 while retaining segments 3 and 4
unchanged leaves 45,749 input and 1,196 output, only 63.83% / 25.53% below native.
Safe deletion and unchanged downstream behavior have NOT been measured.
This sensitivity nevertheless rejects the claim that navigation removal alone,
under that stated intervention, reaches 80/80.

The matched budgets are 25,295.4 input and 321.2 output. Two segments each costing
as much as the observed first segment would already consume 39,048 input.
That is a boundary-specific constraint, not a universal lower bound. An engine
which merely batches file discovery is insufficient for this target.

OBSERVED: the probe-generating segment used 909 output tokens, including reported
reasoning. The trace does not isolate native token cost of code versus reasoning.
Its total exceeds the entire candidate output budget by 587.8 tokens. Even the
287-token final assessment leaves only 34.2 tokens for all preceding output if it
were unchanged. Do not remove useful assessment or probes to manufacture savings.

## Highest-value candidate to assess next

HYPOTHESIS: caller-prepared exact evidence plus reusable, inspectable semantic
probe execution can reduce inspection and test-construction without removing
Astra's right to challenge test adequacy or create new tests.

Caller owns evidence preparation, identity binding and execution registration
before the first inference. Helix Context supplies the existing small behavior
contract; it must not trigger another tutorial or source discovery phase. Engine
owns deterministic evaluation of specified probes, raw receipts and exact staging.
Astra sees task requirements, exact proposed source and relevant check evidence,
then decides whether those checks are sufficient and what additional semantic
probe or correction is needed. There is no supplied reference answer.

Reusable probes must retain their executable source, version, domain limitations
and exact observations. Their coverage is not a semantic certificate. Novel tests
remain ordinary unrestricted tools. Changed code, contract, checker, environment,
or state invalidates the corresponding old result. Failure or ambiguity returns
exact evidence and an unresolved obligation, never inferred success.

This is a candidate architecture, not permission to build a generic test DSL or
force Astra into a closed selection menu. Such a menu could conceal the very
counterexamples that make Astra useful and incur the old alias/codebook tax.

## Cheapest falsifier before another paired run

First use existing probe traces to separate reusable operations from novel
semantic choices. Freeze a coverage map against the original public contract and
record cases the reusable inventory cannot express. Include cross-instance state,
stale cursor, exception identity, self-aliasing and observational iterables.
Charge preparation, source exposure, selection, fallback and result review.

Then, only if the inventory demonstrably replaces substantial visible code without
answer leakage, run a prospective safety gate with a valid proposal, a known
semantic defect and a freshly designed defect outside the inventory. Astra must
retain unrestricted tools and discover/resolve the uncovered obligation. A frozen
finite inventory cannot establish general parity. A future paired economic run
must use fresh matched controls and keep all extra calls, cache and failed paths.

Stop if the new interface requires helper inspection or generated glue; if reduced
cost depends on suppressing novel tests; if a defect is accepted due to mechanical
PASS; or if necessary semantic re-entry exceeds the budget. No production closure
or new benchmark was activated by this audit. Full model/task and long-horizon
qualification remains open.
