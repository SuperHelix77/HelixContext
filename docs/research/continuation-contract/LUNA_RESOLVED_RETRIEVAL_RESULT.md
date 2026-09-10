# Luna closed retrieval: fresh paired execution, 2026-09-10

**OBSERVED:** The active Engine completed two recognized, mechanically closed
requests without a model invocation. Both complete answers exactly match native
Luna High and independent task oracles. This avoids 100% of the task's model
input/output on these requests. Engine and setup costs are nonzero.

**CONDITIONAL:** This qualifies two existing parameterized request grammars on
fresh data. General reasoning, coding and automatic Codex-app integration remain
unqualified. Corrected coding still has median **86.29% input / 64.04% output**
savings and fails 75/75.

## Results

| Task | Native input | Native output | Uncached input | Native segments / tools | Engine model calls | Input / output model tokens avoided | Exact checks |
|---|---:|---:|---:|---:|---:|---:|---|
| Selection, 320 records | 404,874 | 2,411 | 69,002 | 12 / 11 | 0 | 100% / 100% | PASS |
| Exact cold-note recovery | 120,216 | 1,297 | 20,120 | 5 / 4 | 0 | 100% / 100% | PASS |

Controls used `gpt-5.6-luna`, High, default client base and ordinary tools.
Candidate `native_usage` is **null**: no receipt exists for a nonexistent
invocation. Zero model tokens are separately established by the Engine audit
and absence of semantic callbacks. The two-case median is 100/100 only within
this closed-request cohort; it is not pooled with coding or W50.

## Provenance and scope

Runner, auditor, tests and [preregistration](LUNA_RESOLVED_RETRIEVAL_PREREG.md)
were committed as `0961b4e` before either control. No parser, kernel or model
policy changed for this pair. Identical source bytes reside in separate tracked
Git roots. Actual memory preflight and project registration preceded config
freeze with zero model turns; other runs' relevant information was not attached.

The complete requests already specify the selection predicates, projection,
ordering, count and job flag, or the exact inventory tag and recovery fields.
The existing full-match parser admits only these closed forms. SQL selection
and an independently indexed note relation are the task oracles.

Fresh seed `910051` generated 320 records and 40 events/120 notes, including
leading-zero strings, decomposed Unicode, non-Latin text and trailing whitespace.
Data notes confer no instruction authority. Recovery reads original archived
bytes through a reopened store. This is a **40-event snapshot**, not forty live
turns; request families were known to the executor.

Manifest SHA-256: `6e7699b760a0829ed601c989558d00d507079b2dfd8084cebf96a7929101f51b`.
Audit SHA-256: `aeb8761990d7e6b45c241db21cbbe6e2141d43326f6172f2197f77e0faaa050b`.
Default client-base SHA-256: `a91357a1cd2727a0be06d461248d6e3a7274746e38108f548a3adf2cc2430415`.

[Machine-readable results](LUNA_RESOLVED_RETRIEVAL_RESULT.json) bind native
receipts, raw rollouts, source, answers and task state. Public
[exact artifacts and offline verifier](resolved-retrieval-artifacts/README.md)
reproduce complete answers without inference. Environment-bearing raw rollouts
remain local; published counters are extracted receipts, not independently
authenticated provider attestations.

## Observable residual

**OBSERVED:** Selection used ten sequential source-page reads before one `jq`
filter/projection. Cold recovery used four tool calls: discovery, broad search,
source inspection and exact byte/base64 checks. This describes visible commands,
not hidden reasoning.

**INFERRED:** Closed requests specified the whole procedure before inference.
Caller execution removed these calls while preserving exact answers. For
unrecognized requests needing semantic choice, choosing a query before paging
all records is a plausible lever; these pairs do not test that hypothesis.

## Cost accounting

Two native controls, no candidate inference and no retries cost **525,090 input /
3,708 output**, including **435,968 cached / 89,122 uncached input**. Reported
reasoning, 1,076 tokens, is already in output. Earlier failed research attempts
remain separately charged.

| Measured work | Selection | Cold recovery |
|---|---:|---:|
| Native task elapsed | 67.7473 s | 37.1822 s |
| Candidate dispatch only | 0.000751 s | 0.000654 s |
| Candidate memory preflight | 0.141706 s | 0.145576 s |
| Candidate project registration | 0.151384 s | 0.140040 s |
| Archive/state creation | 0.000646 s | 0.000767 s |
| Exact object archived / hashed | 83,967 B | 25,794 B |
| Object read / hashed on reopened-store recovery | 83,967 B | 25,794 B |
| Complete answer | 2,996 B | 208 B |
| Raw memory response retained locally | 27,817 B | 49,944 B |

All-pair preparation took **1.915229 s**, including both workspaces, memory,
registration and archival. Dispatch excludes preparation, repeated manifest /
config verification, final checks/publication and HUD ingestion. Candidate
subtotals are lower bounds, not end-to-end latency. Object counters are logical
traffic, not physical SSD reads; this is not sparse-read efficiency. Storage,
unallocated bookkeeping, parent/R&D inference and included-plan quota are not
fully metered. No whole-project net-cost, quota or break-even claim follows.

## Failure boundary and next work

The caller pins complete task state outside mutable evidence: request hash,
source hash/length, schema/adapter versions and inherited constraints. State is
checked before and after retrieval. Stale/corrupt authority holds for recovery;
unknown wording or inherited constraints retain ordinary semantics inside the
active Engine. Existing offline tests cover these failures; neither positive
fresh pair needed fallback inference.

The caller must supply every applicable constraint; hashes cannot detect omitted
authority. Repeated publication checks do not isolate a hostile concurrent
writer. Delivery still needs compare-and-swap against the bound state root.
Normal Codex-app lifecycle integration remains open.

**HYPOTHESIS, not implementation:** For unrecognized query-shaped requests, Luna
could choose only unresolved query semantics while the existing executor owns
extraction, formatting and verification. First falsify unsafe reduction of
inherited constraints, ambiguous intent, unsupported operators and stale source.
Never add inference to requests already resolved without it.

The HUD keeps verified Engine/native comparisons separate from semantic model
cohorts and withholds savings on mismatched receipts, source, answer, authority,
model/effort or checks. The coding failure remains visible.
