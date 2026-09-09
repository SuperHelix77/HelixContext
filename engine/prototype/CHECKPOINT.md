# Experimental checkpoint — 2026-09-09

Status: development code and receipts, not production admission. No global hook or
installed skill was changed by this checkpoint. The shared public main branch is
not automatically advanced by publishing this isolated feature branch.

## Implemented and checked

- Named immutable plans, declared dependency snapshots, individual step statuses,
  transactional accepted-success pointer and exact declared-source archival.
- Explicit input-snapshot release after the caller finishes all consumers;
  partial cleanup failures are separately reported. No automatic cleanup.
- Compact plan CLI, exact full receipts, break-even arithmetic with unknown costs.
- Project-scoped lexical memory, exact retrieval, timeline and shared-provenance
  replay. No inference is used for routine indexing/search.
- Native usage/resume validation helpers; legacy archived runners are unchanged.

Clean-copy verification: **128 passed**. The copied prototype ran from an
independent temporary working directory; installed Python/pytest were shared.
`CLEAN_COPY_VERIFICATION.json` pins tested Python sources. Tests verify the
documented bounded behaviors, not general semantic sufficiency.

## Measurements and failures

| Evidence | Outcome | Scope |
|---|---|---|
| Named-plan offline execution | Positive latency overhead on both tested input sizes | Exact script/output, no model |
| Explicit snapshot release | Large-input retained storage 7.40 MB → 1.11 MB | Before/after development result; no token saving |
| Metadata invalidation | ctime-only change rejected unchanged source bytes | Unresolved workflow rejection |
| Memory payload | Exact lookup 98.54% smaller; exhaustive recovery overhead reduced to 0.35% | Predeclared query, synthetic payload count |
| Existing native query-V2 receipts | No model meets both 80% thresholds | Six development traces reverified |
| Fresh memory native control | Correct answer; 194,759 input / 1,659 output; stopped before candidate | No pair or saving estimate |
| Separate frozen-candidate follow-up | Input -39.73%, output +15.01% versus retained control | Exploratory historical comparison; joint target failed |

Detailed reports: [plans](NAMED_PLAN_OVERHEAD.md), [release](NAMED_PLAN_RELEASE.md),
[memory](MEMORY_PAYLOAD_RESULTS.md), [native receipt checks](NATIVE_BENCHMARK_GATE.md),
[budget stop](MEMORY_NATIVE_CONTROL_STOP.md).

The later [separately declared follow-up](MEMORY_NATIVE_FOLLOWUP.md) preserves the
original budget stop and reports its changed budget and negative output result.

## Open gates

The approved full TOCTOU condition remains unestablished for noncooperating host
writers. Snapshot lifecycle assumes exclusive caller ownership. Complete creation,
failure, SQLite, physical I/O and publication accounting is unfinished. Search
misses do not establish absence, and index completeness/rebuild is not certified.
Native memory bootstrap, skill restoration, model-discovered latent relevance and
combined input/output savings require further evidence. HUD and integrated skill
activation remain planned; neither is implicitly delivered by the prototype.

The next native experiment must use integrated identity/usage guards and a budget
that accounts for multi-tool turns; the stopped experiment is closed and cannot
be silently resumed with a higher threshold. Neither reduced verification nor a
weaker baseline is an acceptable route to the target.
