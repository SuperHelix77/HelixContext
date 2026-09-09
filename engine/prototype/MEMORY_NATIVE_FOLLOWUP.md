# Frozen memory candidate: native exploratory follow-up

The original control experiment remains budget-stopped. A separately declared
one-call follow-up ran its unchanged, previously frozen candidate prompt against
the same raw history with Luna High. No new control was purchased. The follow-up
explicitly changed the post-call overrun flags to 250,000 input / 8,000 output,
retained the 600-second timeout and prohibited retries or matrix expansion.
These are post-call thresholds, not hard inference caps. This is an exploratory
historical-control comparison, not a fresh randomized pair.

| Measurement | Retained control | Helix follow-up |
|---|---:|---:|
| Native input | 194,759 | 117,385 |
| Native output | 1,659 | 1,908 |
| Reported cached input | 167,424 | 95,488 |
| Reported reasoning output | 674 | 852 |
| Elapsed | 49.292 s | 57.687 s |
| Commands | 2 | 3 |
| Command text bytes | 1,019 | 698 |
| Terminal output bytes | 578 | 7,471 |
| Artifact changes | 1 | 1 |
| Agent messages | 3 | 4 |

Both artifacts matched exact expected values/types, including chronological
updates and the retained original region. Both raw sources remained unchanged.
Native input decreased **39.73%**; output increased **15.01%**. The joint 80%
target failed. This finite task does not establish general capability parity.

## Trace findings

The control used a Python filter that printed only matching source lines. The
candidate used `rg` over JSONL records, which printed entire matching records,
then `jq` across all 50 records. Both created and verified the answer. The supplied
partial evidence did not eliminate source inspection, and the candidate expanded
more terminal content despite generating fewer command bytes.

The candidate also narrated unavailable memory/registration helpers. The recorded
tool sequence contains no corresponding helper attempt, so that statement is
model narration, not a verified runtime failure. Both runs emitted the same
warning that skill descriptions were shortened by the runner's skills budget.
This comparison uses that common configuration; it is not evidence about all
installed skills under unrestricted context.

These observations do not expose private model reasoning or establish a causal
effect from one prompt sentence. They do falsify treating shorter commands or
smaller supplied context as sufficient evidence of reduced native output cost.

## Accounting and decision

Combined native cost of the retained control and follow-up: **312,144 input and
3,567 output tokens**. Parent research is additional. Candidate preprocessing was
68.6 ms and retained 268,217 logical store bytes; physical I/O and money remain
unmeasured. Do not add cache/reasoning categories to native totals or treat them
as a dollar-saving percentage.

`MEMORY_NATIVE_FOLLOWUP.json` records source trace hashes, exact results, usage and
trace counters. Raw traces remain local. No further calls are scheduled by this
diagnostic and the candidate is not promoted. Future work should test whether
typed terminal extraction and a valid caller bootstrap avoid the observed extra
work, while preserving missing-evidence recovery and ordinary control tools.
