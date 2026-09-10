# Astra XHigh: semantic review preserved, modest economic gain

**OBSERVED:** caller-prepared execution evidence removed repeated test execution
without suppressing the new semantic probe in these two review cases. Both arms
accepted the valid change and rejected a default-limit regression missed by all
supplied tests and both historical Astra probe programs. Ordinary model-written
final answers and XHigh effort were preserved.

| Paired review | Input ordinary → prepared | Input saved | Output ordinary → prepared | Output saved | Short API-equivalent saved |
|---|---:|---:|---:|---:|---:|
| Valid implementation | 133,760 → 75,848 | 43.30% | 1,679 → 1,089 | 35.14% | 18.03% |
| Default-limit defect | 168,328 → 120,480 | 28.43% | 1,619 → 1,526 | 5.74% | −0.67% |
| **Two-case median** | | **35.86%** | | **20.44%** | **8.68%** |

Median uncached input saving was **−15.39%**: uncached input increased. Long-context
API-equivalent median saving was 8.11%. These are dated Standard API scenarios,
not measured Codex quota, a bill, or complete effective cost. The exact official
[pricing source](https://developers.openai.com/api/docs/pricing.md) was fetched at
2026-09-10 07:46:03 UTC and retained with its hash. Live HUD pricing refreshes and
expires independently. No 65/65 release claim is supported by this diagnostic.

## What was preserved and removed

Both arms used the same installed original Astra base, tools, Helix skill and
global configuration. Engine stayed active: ordinary execution was compared with
caller-prepared regression evidence and an exact diff. This is not pristine native
Codex, and these review cases are not additions to the seven-task release cohort.

The prepared valid arm used 3 segments/5 shell commands versus 5/10 ordinarily.
The defective arm used 4/6 versus 6/11. Neither prepared arm reran the supplied
regressions. Both still inspected source and coverage. On the defective case both
models created and executed a new 12-record probe demonstrating that unchanged
two-argument calls returned 9 results instead of 10. Test PASS did not override
semantic judgment. The prepared probe's nonzero exit was an intentional failing
compatibility assertion; ordinary `diff` exits also indicate differences, not
infrastructure failure.

All four final answers were checked against source and actual execution evidence.
Inputs remained unchanged. Native counters, per-segment increments, model/effort,
raw stream hashes, configuration and final authorship were reconciled. The two new
probe programs were cross-replayed on both sources with the expected outcomes.
These are bounded semantic/workflow checks, not universal intelligence parity.

## Costs and decision

All four streams consumed 498,416 input and 5,913 output tokens, including 2,146
reported reasoning tokens. Combined preparation took 2.08 seconds; each prepared
arm's three caller-run checks took about 0.60 seconds. Native session time was
74.86→45.19 seconds for the valid case and 76.95→59.10 for the defect, excluding
preparation. Memory, storage, raw capture and adjudication also cost resources;
complete physical I/O and included quota are unmeasured.

**The policy misses its preregistered 20% median weighted-cost admission gate.**
No new Astra kernel or model profile is deployed or frozen. The current coordinator
retains already-supported exact evidence/test reuse and used the existing Engine
to capture this audit, preserving raw stdout/stderr and unchanged-input checks.
Its own end-to-end savings remain unmeasured; its reasoning and review authority
were not changed.

The residual is now clearer. In the prepared valid arm, the final semantic-review
segment alone used 793 output tokens, including 516 reported reasoning tokens.
Even retaining only that observed segment leaves 52.77% output savings against its
control, under unchanged costs. That is conditional trace arithmetic, not an
irreducible lower bound. More source preloading alone does not justify another
native attempt to claim 65/65. Preserve the semantic work and reject blind reruns.

Evidence: [native accounting](RESULT.json), [explicit semantic review](SEMANTIC_REVIEW.json),
[public verification](PUBLIC_VERIFICATION.json), [frozen protocol](PREREG.md).
