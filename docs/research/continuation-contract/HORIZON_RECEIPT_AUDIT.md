# Historical native horizon coverage and call-placement sensitivity

OBSERVED: reconciled546original native receipts and534exact passive replies against
the published V3 summary. Every selected raw event SHA256 matches both its original
status and published commitment; input/output/cache/reasoning totals agree. This
rechecks provenance and ACK behavior, not a new independent final-answer grading.

An earlier release DID run W50 and L40 for Luna/Sol/Astra High, both arms. W50 has
49passive ACK requests followed by one policy/historical decision. L40 has40ACK
requests followed by one late-selected exact historical-label retrieval. Each event
used a fresh native CLI invocation with caller-reconstructed context. These are
native horizon episodes, but not persistent-session compaction or50dependent
semantic decisions. A/W controls were reused in the older V3 report; L40 controls
were fresh. Current implementation/global-instruction changes are not qualified by
these old passes.

| Model/episode | Observed input saved | Observed output saved | Conditional final-only input saved | Conditional final-only output saved |
|---|---:|---:|---:|---:|
| Luna W50 |20.60%|51.24%|93.52%|81.40%|
| Luna L40 |27.79%|23.15%|90.65%|70.34%|
| Sol W50 |15.20%|-26.06%|93.83%|10.28%|
| Sol L40 |26.60%|-6.86%|93.83%|22.68%|
| Astra W50 |9.73%|-5.79%|92.25%|36.45%|
| Astra L40 |24.27%|-3.22%|93.62%|41.80%|

CONDITIONAL columns retain the old candidate final invocation and delete its
passive calls, relative to old full native totals. They do not measure a new policy.
Safe elimination, unchanged final behavior/cost and full caller persistence/recovery
cost are unproven. This also changes the original no-call-elimination comparison
contract. Never present those columns as achieved80/80 or automatic production
admission. Do not select an old high-cost control instead of a fresh efficient one.

## What survives

- Older finite native evidence covers early authority/amendment recovery and late
  relevance, with actual candidate cold-file retrieval recorded by the old grader.
- Deterministic epoch recovery after50stored records is separate engineering
  evidence; it cannot replace these model tests.
- Newer same-thread amendment recovery and semantic safety tests cover bounded
  current paths, not the whole historical suite or long native compaction.
- Call elimination attacks repeated input, while output savings depend strongly
  on model behavior. Luna W50 is the only one of these six optimistic sensitivities
  clearing80on both axes; its L40 case does not.

## Qualification gaps, not an empty history

| Requirement | Available evidence | Remaining gap |
|---|---|---|
| Three models / multiple task families | Older Q4/A/W50/L40 finite V3 evaluation | Fresh paired current release and representative scope |
| Latent future relevance | Older L40native episodes | Current engine, new cases, exact cold tool-state recovery |
| Persistent native continuation | Newer bounded two-turn amendment recovery | Long dependent trajectories and lifecycle failures |
| Compaction skill restoration | Deterministic registry/restore tests | Native post-compaction behavior |
| Recovery economics | Exact epoch recovery probes | Full dominant-path costs, no cross-fixture ratio claims |
|80input/80output without loss | Isolated candidates and negative pairs | Full requested target remains unestablished |

## Next experiment admission

Do not rerun this passive50turnsuite merely to generate an impressive input ratio.
A future passive-event dispatcher must prove exact durable recording, exact ACK,
unknown-event fallback and later recoverability before calls are skipped. It may
be useful for Luna specifically; any economics needs a fresh baseline and includes
all registration/recovery/amortization. No caller may silently classify an event
requiring semantic work as passive.

For Astra, active semantic state reuse is still the higher-value open question:
repeated decisions with unchanged dependencies, genuine amendments and late
relevance—not49identical acknowledgements. A prospective protocol must preserve
all required actions and surprise evidence, bind the current global instructions,
and retain native behavior as fallback. No new model experiment is admitted by
this audit alone.

Reproduce:`horizon_receipt_audit.py <repo> <original-raw-root> <output.json>`.
Machine artifact:`HORIZON_RECEIPT_AUDIT.json`; no new native calls.
