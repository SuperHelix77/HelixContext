# Explicit obligations can be mechanized; semantic adequacy remains open

**OFFLINE RESULT,2026-09-10:** a bounded differential/metamorphic adapter detects
the actual default-limit defect from Astra's previous review plus five constructed
faults, without invoking a model. It runs612 declared comparisons per variant in
about one second. This is functional evidence for moving specified comparisons out
of model-generated test code. It is **not** an80/80 result or a model release.

## What was built

The adapter compares the prior `Memory.search` implementation with a candidate in
disposable stores. It checks the exact legacy return values/errors, explicit AND
compatibility, literal-word OR as a union of prior single-word results, argument
validation, unchanged event/index tables and corruption beyond the result limit.
The task already states these obligations. The adapter does not infer them from a
PASS receipt or decide that all semantic obligations have been enumerated.

Differential testing uses comparable implementations to expose disagreements;
legitimate differences and test-generator assumptions still need adjudication.
[McKeeman,1998,pp.101–102](https://www.cs.tufts.edu/comp/150FP/archive/bill-mckeeman/DifferentailTesting.pdf)
Metamorphic testing supplies specification-derived relations between executions;
it does not convert finite testing into a complete oracle.
[Liu et al.,2014,§§I–II](https://vuir.vu.edu.au/33046/8/TSEmt.pdf)

No new model-facing language, prompt/kernel, generic semantic cache, production
router or automatic deployment was added. This remains a research adapter for
one explicitly qualified task/reference pair. It neither writes model finals nor
requests less reasoning or fewer semantic probes.

## Offline outcomes

| Source variant | Violated comparisons, of612 | Outcome |
|---|---:|---|
| Previously accepted implementation |0|No difference in enumerated cases|
| Actual default-limit10→9 defect |20|Detected|
| Reversed result ordering |112|Detected|
| Wrong default match mode |54|Detected|
| Missing integrity validation |18|Detected|
| Wrong default limit only for OR mode |24|Detected|
| Mode validation after empty-query return |24|Detected|
| Query-specific defect outside the corpus |0|**Missed, deliberately retained coverage hole**|

The valid/default-limit sources are byte-identical to the two previous Astra
review artifacts. The first counterexample compares the same ordinary call,
`search('p','alpha beta')`: baseline returns10 records and candidate9. The generator
uses the baseline's default to choose nearby corpus sizes; it is not supplied the
candidate's answer or Astra's generated witness.

All eight cases are exposed development calibration, not holdouts. The uncovered
query mutation returns an incorrect empty answer for `unlisted_token`; a separate
witness confirms it is wrong. Its trigger was not added to the corpus afterward.
**This demonstrates why `NO_DIFFERENCE_IN_ENUMERATED_CASES` must never become
`SEMANTICALLY_CORRECT`.** Astra must retain source access, investigation authority
and its ordinary complete final answer.

## Hostile admission finding and repair

The initial four engineering tests passed, but an additional falsifier exposed an
authority bug: the adapter could freshly hash a changed task and still apply the
old compiled compatibility relations. For example, a new request to change the
default to9 invalidates the old obligation to preserve10.

The new test failed before the repair. The adapter now requires the exact
previously adjudicated task, reference-source and evidence implementation hashes,
as well as current runtime/candidate bindings. A new task/reference requires new
relation qualification; a fresh hash cannot grant that authority to itself.

**Six boundary tests pass.** They cover stale/missing/wrong bindings before
execution, unsupported observations, typed distinction between `true` and1,
changed task/reference qualification, and source drift preventing a successful
receipt. The public verifier reproduces the old admission from preserved source
bytes and confirms the new rejection. It also verifies all4,896 archived
comparison outcomes and31 artifact bindings.

The old source and first calibration remain in `artifacts/initial-executor` and
`INITIAL_RESULT.json`. A publication-verifier path assertion initially failed on
the macOS `/var` versus `/private/var` alias; canonicalizing the assertion fixed
that verifier issue without changing any comparison result.

This is not hostile-host custody or untrusted-code sandboxing. Trusted local
research modules run in disposable stores; end guards detect observed drift and
do not prove that a concurrent change-and-revert never occurred.

## Costs and native admission

Final eight-variant calibration: **7.683s**, median **0.981s** per variant. Initial
calibration:7.468s, retained separately. The valid case reads2,954,298 logical
object bytes through22,596 reads, writes39,590 object bytes and hashes2,994,748
bytes. Full physical SQLite/filesystem I/O remains unmeasured. Tests, source
qualification, publication and this research are additional costs.

Exact final outcomes occupy5,932,931 bytes; the lossless public gzip archives occupy
101,070 bytes. That is storage representation, not a measured reduction in model
input. No model was given either representation during this turn.

There were **zero additional native benchmark calls**, but research was not free.
The active-goal counter moved from8,440,549 to8,565,050 at an intermediate reading,
a coarse124,501-token interval. That counter is not a per-model input/output split,
invoice, completed-turn total or substitute for native paired receipts. Setup and
research amortization must be measured before any net-economic claim.

The new adapter could plausibly remove some generated comparison code. It cannot
honestly claim the entire mixed Astra segment as removable. Even granting that
optimistic deletion for the previously observed defect case, while leaving other
segments unchanged, gives only **45.98% input /35.42% output** two-case median
savings. The valid case contains no equivalent new comparison segment to delete.
See[COST_GATE.json](COST_GATE.json). This is arithmetic over old verified streams,
not a measured intervention, causal estimate or impossibility theorem.

**Decision:** retain this tested execution building block, but do not launch an
unchanged native review pair merely because coverage improved. A next native
experiment needs a mechanism addressing the remaining output as well; no new
configuration or Astra profile is admitted here.

## Latest native benchmark remains unchanged

The separate [Astra High W50 V2 pair](../w50-native-final-v2/RESULT.md) remains
98.32% total-input /72.71% uncached-input /49.62% output saving, with both complete
model-written finals passing its finite checks. It is1/7 release cells, not a
seven-cell median. No results from these offline comparisons enter that cohort.
The80/80 capability/workflow-preserving objective remains open.

Reproduce engineering checks with:

```sh
python3 -m pytest -q docs/research/differential-obligations-v1/test_boundaries.py
python3 docs/research/differential-obligations-v1/verify.py
```

For a new offline calibration output directory, run `calibrate.py <new-directory>`.
It does not invoke a model. Results:[machine receipt](RESULT.json),
[public verification](PUBLIC_VERIFICATION.json),[design and limits](DESIGN.md).
