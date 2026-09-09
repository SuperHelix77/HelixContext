# Sol integrated V1: no freeze

**14.56% native input / 40.59% native output savings.** Both exact artifacts and
source-preservation checks passed. Neither 75/75 nor 80/80 was reached. Terminal
state: `RESIDUAL_DIAGNOSIS_ONLY`. Two calls; no experimental rerun or prompt tuning.

| Metric | Control | Integrated Sol High | Saved |
|---|---:|---:|---:|
| Native input, including cached | 136,608 | 116,717 | 14.56% |
| Native output, including reported reasoning | 2,673 | 1,588 | 40.59% |
| Cached input, a subset | 109,184 | 103,296 | — |
| Uncached input | 27,424 | 13,421 | 51.06% |
| Reported reasoning output, a subset | 966 | 751 | 22.26% |
| Command calls | 5 | 5 | 0% |
| Recorded terminal bytes | 38,679 | 5,261 | 86.40% |
| Generated command bytes | 2,058 | 659 | 67.98% |
| Caller preparation seconds | 0.291 | 0.258 | Not a token metric |
| Native elapsed seconds | 145.874 | 73.904 | Confounded by control retry |
| Exact output bytes | 6,102 | 6,102 | Both pass |

The pair consumed **253,325 input / 4,261 output tokens** in reported native
receipts. Parent research and potentially disconnected server sampling remain
additional/unmeasured. Cached input is included, never added twice. No monetary
savings claim follows without prices and complete billing receipts.

## What was integrated

The previous exact-copy fixture was reused with four small policy-history
records, including a superseded policy and a rejected alternative. No filler
history or log padding was added. Both arms received identical source records,
history and raw logs, and the caller executed the same real 36-test archive
schema preflight. These tests validate structure, not semantic release selection.

The control could use ordinary efficient search and scripts. It was not forced
to dump all records; it chose to read the complete payload. The candidate received
request-conditioned exact policy records, complete selection metadata, the skill,
and reduced preflight evidence. Memory survived runtime recreation and restored
exact skill and source references. Original IDs drove caller-owned exact copying
and byte verification. All three mechanisms were enabled; cold plans were off.
Independent immutable switches and component hashes remain available.

This is a fresh composite **development task**, not a holdout, isolated mechanism
ablation, or proof that prior percentages compound. Only schema-test output ran
through the command reducer; arbitrary model commands were still native. The
integration therefore does not claim universal tool-stream interception.

## Residual diagnosis

The candidate still performed five commands: installed-skill reread, file
rediscovery, policy search, three-record payload sample, and a semantic jq
selector. No Engine implementation read appears in its command trace. It avoided
artifact-assembly code, but did not avoid the model/tool conversation around
supplied evidence. The installed-skill read may reflect platform skill-loading
requirements; its cost cannot simply be removed by forbidding required checks.

The representation reduction was real: recorded terminal bytes fell 86.4%,
while native input fell only 14.6%. This directly falsifies treating local output
reduction as an equivalent whole-run token saving. The candidate's initial
supplied prompt was also larger: 8,540 versus 4,686 bytes. Exact metadata, skill
and projection have an admission cost even before any rereading.

Reported reasoning alone was 751 output tokens, exceeding this control's
75%-saving total-output allowance of 668.25. **Conditional arithmetic only:** if
that reasoning count stayed fixed, deleting every other output token would
still miss 75%. It is not an irreducible reasoning lower bound and does not justify
lowering High or removing semantic verification. Preventing redundant work is
the unresolved requirement.

The candidate narrated a Helix registration `PermissionError`. Stderr records
one sandbox filesystem denial with unknown path, but the recorded command trace
contains no registration call. A global Helix hook configuration exists, while
the runner specifies `--ignore-user-config`; configuration presence does not
prove hook execution. The particular database failure remains unestablished.
It would be incorrect to label this proven hallucination or proven hook failure.

The control's stderr records one transport sampling retry. Complete accounting
for disconnected server work is unavailable, so latency is not a clean paired
model comparison. Both raw stderr hashes are retained. These environmental
confounds would preclude broad qualification even if the numeric gate passed.

## Hidden-cost accounting

Candidate reducer: 3,489 raw bytes → 1,651 projected transport bytes, versus
3,741 bytes for its native JSON transport; approximately 1.03 ms reduction and
verification time. This is presentation accounting, not model-visible token
billing. Its 12,948 logical evidence-read bytes expose repeated verification
traffic rather than hiding it.

Candidate cold store ended at 110,844 file bytes. After restart, logical object
reads were 104,646 bytes, writes 57,337 bytes, hashed bytes 162,708; before-restart
indexing costs are separately retained. The JSON report includes both runtime
instances. Do not add nested cumulative operation receipts again. The memory
index conservatively rereads its scope; physical I/O, SQLite traffic and money
remain unknown. Routine HUD rendering uses no inference.

## Disposition

Do not freeze Sol or announce 75/75. Do not multiply its earlier wins. Preserve
this integrated implementation and failed qualification. Any subsequent native
attempt needs an explicit residual-cost intervention and control of the
registration/skill-admission boundary; adding more compression layers is not
supported by this result. No additional native attempt was made here.

**201 engineering tests passed**, including raw/binary recovery, no rerun after
reducer failure, invalid-policy rejection before side effects, scoped persistent
memory, exact skill restoration and latent-fact retrieval after 50 stored events.
Live HUD SSE, filters, Engine timeline, switches, receipt links, pause/resume and
mobile overflow checks passed. These are infrastructure results, not model
intelligence or 50-turn agentic parity certification.

[Machine-readable adjudication](SOL_INTEGRATED_RESULT.json) retains source,
manifest, component, trace and stderr hashes. Raw traces and local environment
receipts remain in `research/sol-integrated-v1-20260909` outside the public repo.
