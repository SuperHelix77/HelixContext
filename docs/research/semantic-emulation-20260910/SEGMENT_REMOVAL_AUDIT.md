# Astra segment removal: preparation alone misses the target

**OBSERVED:** four current XHigh review streams contain 18 model segments and 32
completed shell commands. Their native stream hashes, command identities and
per-segment totals reconcile. This audit reads existing evidence only; it runs no
model or offline benchmark and changes no implementation.

The [event-to-segment map](SEGMENT_REMOVAL_AUDIT.json) identifies public command
receipts by native event index and hash. Labels describe visible activity, not
causal token allocation or hidden reasoning. All segments remain unqualified for
automatic semantic removal.

## A zero reasoning counter is not zero semantic work

In the ordinary defective-case run, segment 4 generated and executed the new
12-record comparison that demonstrated loss of the tenth result. It also ran
existing tests. That segment reports **548 output tokens and zero reasoning-output
tokens**. Its successful exit asserts that the defect exists; the prepared arm's
compatibility assertion intentionally fails on the defect. Neither exit alone is
a correctness label.

Thus semantic work is observable in generated programs even when the reported
reasoning subset is zero. Conversely, the valid ordinary run's segment 4 shows a
hashing command alongside 402 reported reasoning tokens. We cannot infer that those
402 tokens were spent on hashing, or that moving the hash computation removes them.
Removing counters is not the same as removing responsibilities.

## What remains in the prepared paths

| Case / segment | Native input / output | Visible work | Why whole-segment deletion is unqualified |
|---|---:|---|---|
| Valid 1 | 21,254 / 91 | Introduction, working directory and inventory | Navigation could be supplied; actual savings require charging its replacement |
| Valid 2 | 21,475 / 205 | Task, skill, source, dependency and coverage reads | Evidence is needed for the following assessment; omission is not preparation |
| Valid 3 | 33,119 / 793 | Assessment and model-written final | Contains the actual review result; no equivalent pre-existing decision is bound |
| Defect 1 | 21,257 / 216 | Introduction, task/skill/source/coverage reads | These observations enable the defect diagnosis |
| Defect 2 | 30,365 / 297 | Explicit defect diagnosis plus dependency read | The dependency read shares a segment with a new semantic judgment |
| Defect 3 | 34,068 / 485 | New probe generation and execution | Confirms behavior missed by every supplied test |
| Defect 4 | 34,790 / 528 | Assessment and model-written final | Preserves rejection, evidence and required final authorship |

The classification does not claim that every byte or token is necessary. It
identifies what a replacement must preserve before whole segments can disappear.

## Generous preparation-only arithmetic

Assume the initial evidence can be supplied perfectly at **zero additional cost**,
delete the acquisition prefix, and retain all observed diagnosis/probe/final
segments at their original costs. This is deliberately more generous than a real
preparation mechanism: it neither charges added prompt bytes nor reconstruction.

| Case | Retained candidate segments | Input saved vs actual control | Output saved vs actual control |
|---|---|---:|---:|
| Valid | 3 | 75.24% | 52.77% |
| Defect | 2, 3, 4 | 41.05% | 19.09% |
| Two-case median | | **58.15%** | **35.93%** |

These are **fixed-trajectory arithmetic**, not measured savings, a safe deletion
policy or an irreducible model bound. Surgical changes within a mixed segment can
change the trajectory; this calculation does not bound them. Even this generous
prefix-removal scenario does not support a new preparation-only 65/65 or 80/80
benchmark. It also cannot be substituted for the seven-task release median.

For comparison, the actual latest two-case medians remain **35.86% input / 20.44%
output**, with **−15.39% uncached input saving** and a dated **8.68% short-tariff
API-equivalent saving**. The existing weighted admission gate failed. No new
benchmark result or frozen model is created by this audit.

## Next-action gate

Reject another unchanged source-preloading, tool-reduction, thread-persistence or
reasoning-counter-only run as the route to the target on these traces. A new
proposal must name an operation *inside* a mixed segment that has a deterministic,
already authorized replacement, while retaining diagnosis, novel-probe authority,
exact evidence, required actions and the model-written final.

Before inference, document the replacement's pre-existing code, complete declared
dependencies, affected obligations, stale/recovery handling and full preparation
cost. Do not preload these exposed benchmark solutions as reusable intelligence.
A source hash or a prior PASS cannot certify the new task's semantic conclusion.
If no such operation has material measured cost, decline the experiment rather
than sample a shorter answer or reduce effort.

The earlier three-task source-only coding results already reached one segment
and zero tools while missing their output gates; their different final contract
does not repair the current cohort. Together the evidence directs attention to
which computation is being repeated, not to adding another generic interface.

**Status:** research gate remains HOLD. Engine stays active, ordinary Astra
semantics and tools remain intact, and no live profile or configuration changed.

Sources: [current paired review](../astra-reuse-v1/RESULT.md),
[bound semantic review](../astra-reuse-v1/SEMANTIC_REVIEW.json),
[existing probe cross-replays](../astra-reuse-v1/PUBLIC_VERIFICATION.json),
[earlier source-only coding anatomy](../continuation-contract/CODING_OUTPUT_ANATOMY_20260910.md).
