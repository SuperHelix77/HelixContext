# Required per-model report and HUD measures

User requirement: optimize ordinary model execution inside always-on Engine too.
Retaining ordinary execution does not end optimization work. Attack measured setup,
repeated evidence acquisition, procedural generation, state transitions and redundant
re-entry without lowering effort, removing tools or suppressing semantic checks.

On completion of each model's work, publish one report and HUD profile covering:

* Coding, retrieval/selection, cold recovery and continuation as distinct families.
* Exact native input, cached/uncached input, output including reported reasoning,
  model turns, tool calls, wall time and Engine preparation/recovery/I/O costs.
* Per-pair savings `100*(1-candidate/control)` for each metric, then median of those
  per-task percentages. Do not substitute ratio-of-totals for median; show both.
* Sample count, task/release identities, fresh/reused control, development/holdout,
  successful/failed pairs, semantic/agentic checks and confidence limits.
* Model-specific ordinary-mode behavior and component activation; Engine stays active.
* Monetary estimates only with dated verified prices, uncached/cached/output weighting
  and known extra costs. Unknown quota conversion stays unknown. A token-equivalent
  price estimate is not measured included-plan allowance savings.

Do not pool cached headline savings with uncached or output savings. Do not mix a
50-turn ACK fixture into a three-task coding/retrieval median without showing the
separate strata and the weighting. Preserve negative savings; never discard a failed
pair to improve median. If a failed run has no valid comparable completion, report
its cost and failure and mark that pair's savings noncomparable, not zero or a win.
Show missing latency/storage/pricing fields explicitly instead of assuming zero.

Starting verified baseline: `continuation-contract/LUNA_TASK_MEDIANS.json`, computed
from the existing three-pair capability receipt. Median task savings are **9.15%
input, −62.30% output, 14.36% uncached input**. This is historical development evidence,
not results from the newly revised always-on execution contract. W50 remains separate.
These unfavorable medians belong in the HUD alongside the bounded W50 win.

HUD should display medians only for a declared cohort, with family filters, N,
release and confidence labels, plus per-task drill-down. The user requested full
HUD work after Luna qualification; this contract and baseline are prepared now.
