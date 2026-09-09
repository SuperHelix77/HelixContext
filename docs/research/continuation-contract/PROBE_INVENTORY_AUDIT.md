# Reusable semantic probes: coverage audit before implementation

OBSERVED: offline replay of the exact Astra supplemental Python heredoc from the
fresh prereview candidate, alongside its two declared checkers. No model calls.
This is posthoc development mutation testing, not independent replication or a
fresh native safety gate. It does not regrade any original correct proposal.

| Proposal variant | Declared | Independence | Astra supplemental |
|---|---|---|---|
| Original correct proposal | PASS | PASS | PASS |
| Shared instance storage | PASS | FAIL | FAIL |
| Self-alias input ignored | PASS | PASS | FAIL |
| Integers above signed 64-bit rejected | PASS | PASS | FAIL |
| Legacy sequence input rejected | PASS | PASS | FAIL |
| Input length hint invoked | PASS | PASS | FAIL |
| Value 4093 silently omitted | PASS | PASS | PASS |

FAIL means the suite detects the injected defect, not that the agent failed.
The length-hint variant calls an optional method whose user-defined exception
prevents an otherwise supported finite iterable from completing. The legacy
sequence variant rejects Python's supported __getitem__ iteration fallback.

The final variant violates the contract directly: `append_batch([4093])` returns
0 and leaves an empty list, instead of returning 1 with `[4093]`. The independent
witness is executed and asserted by the audit. This hand-designed escape is not
an empirical estimate of defect prevalence or a claim Astra would miss the branch.
It is now development evidence, never a future unseen holdout.

## Reuse map

| Existing work | Reusable machinery | Semantic responsibility retained |
|---|---|---|
| Stateful success/failure sequences | Execute frozen declared checker | Judge contract and checker adequacy |
| Cross-instance independence | Execute independence checker | Identify other hidden/shared state |
| Alias and stale-state probes | Execute exact supplemental suite | Identify new aliasing interactions |
| Iteration entry/midway exceptions | Execute existing probe objects | Judge domain and new exception paths |
| Huge ints, invalid types, sequence fallback | Execute existing concrete cases | Inspect value/type-dependent behavior beyond samples |
| Source inspection | Exact caller-provided bytes and identity | Decide whether implementation satisfies the contract |
| Protected-file checks and receipts | Caller-owned hashing and snapshots | Resolve unexpected state or semantic obligations |

INFERRED: the 909-output probe-generating segment contains useful semantic tests,
not disposable scaffolding. Reusing its exact executable suite could avoid future
regeneration. No measured native savings follow from offline reuse alone. The
segment includes reported reasoning and other output; do not assign all909 tokens
to replaceable code. Preparation, execution, result delivery and renewed adequacy
review must all be charged.

## Architecture decision

CONDITIONAL: reuse existing executable tests internally, with exact source and
results available. Do not build a generic probe DSL or closed selection menu now.
A finite test inventory cannot be a semantic acceptance authority. PASS means
these exact tests passed on these exact bytes, not requirements satisfied.

A caller may prepare a bound execution receipt before Astra's first turn, exposing
exact proposed source, contract and limitations. Astra retains tools, may inspect
checker source, and may generate new probes. Unexpected results invalidate any
prior predicted outcome. Changed contract/source/checker/environment/state requires
refresh of affected receipts. No automatic semantic closure was implemented here.

The next native safety experiment, if admitted, must test whether ready evidence
actually prevents regeneration without inducing acceptance of semantically wrong
but test-passing code. It must include a genuinely fresh uncovered defect after
freezing the candidate, and allow unrestricted supplemental tests. The current
4093 variant can only be a development sanity check. A safe receipt alone is not
sufficient to claim 80/80; follow with fresh paired economics and full workflow
qualification. Stop if source concealment or tool restrictions are needed.

## Reproduction and limits

`python3 docs/research/continuation-contract/probe_inventory_audit.py /path/to/native-prereview-pair-v1-20260909 /tmp/result.json`

The script checks the original event hash, extracts the unchanged Python heredoc,
records suite/source hashes, runs each variant/suite in a separate temporary
process, checks that the reference passes and independently asserts the uncovered
witness. Raw stdout/stderr and elapsed times are retained in
`PROBE_INVENTORY_RESULT.json`. No production modules, frozen checkers, original
receipts or native task inputs changed. Offline process times are not dollar or
native-token savings. The 80/80 and full no-loss objectives remain unestablished.
