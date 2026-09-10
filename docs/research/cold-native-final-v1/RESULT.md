# Astra High: prepared cold recovery, complete native final

**OBSERVED:** one fresh paired development run, frozen in `4d577eb`. Both answers
passed exact field/type, Unicode, trailing-whitespace, leading-zero, base64 and
source-event checks. Both finals are the original complete model-written JSON;
no caller replacement, normalization or effort reduction. No implementation or
installed configuration changed.

| Measure | Engine ordinary control | Prepared recovery | Saving |
|---|---:|---:|---:|
| Native input | 92,012 | 19,979 | 78.29% |
| Native output | 468 | 179 | 61.75% |
| Cached input | 72,064 | 7,808 | 89.17% |
| Uncached input | 19,948 | 12,171 | 38.99% |
| Reported reasoning output, included above | 0 | 60 | — |
| User turns / model segments / commands | 1 / 4 / 3 | 1 / 1 / 0 | — |
| Native session seconds | 28.48 | 9.21 | Excludes caller preparation |

**CONDITIONAL economics:** the dated official Standard API scenarios in
[PRICING.json](PRICING.json) give $0.294944 → $0.138468 short-context equivalent
(53.05% saving), or $0.578188 → $0.272461 long-context equivalent (52.88%).
These are neither Codex included quota nor actual billing nor complete cost.
Rates came directly from the [official pricing source](https://developers.openai.com/api/docs/pricing.md);
the exact dated bytes and hash are retained. The live HUD refreshes independently.

## What changed observably

Control located the tag with `rg`, displayed the first 16,000 characters of history,
then generated a Python extraction and base64 round-trip check. Candidate received
the existing executor's completed extraction and original note before inference,
and issued no commands. Both had the same full source, original client base,
installed settings, ordinary tools, High effort and attached skill. The candidate
correctly attributed extraction to the caller. No source files changed.

First-segment input rose from 19,639 to 19,979: the packet had a 340-native-token
initial cost in this pair. Total savings came from eliminating subsequent source
acquisition/extraction cycles. No access to hidden reasoning is claimed. Zero
reported reasoning in control is a counter observation, not absence of cognition.
This exact lookup demonstrates delegation of resolved work; it does not establish
cheaper novel semantic reasoning or general Astra parity.

The candidate does not meet either 80/80 or 65/65 on this task. For 80%, the observed
control allows 18,402.4 input and 93.6 output tokens. The candidate's first segment
already exceeds both. Even hypothetically deleting all 60 reported reasoning
tokens while fixing everything else leaves 119 output, only 74.57% saving. This
is fixed-trajectory arithmetic, not a lower bound, feasible intervention or reason
to suppress reasoning. No cosmetic follow-up run is justified by proximity to65%.

## Complete accounting boundary

Caller preparation took 0.514s including both memory recalls; both zero-turn native
preflights took 0.578s. Archive/reopened extraction took 0.001905s and separately
wrote/read/verified the 25,794-byte source. Optional memory returned 23,234 raw bytes
per arm; no other-task memory was injected. Raw model evidence and audit copies
remain charged. See [AUDIT.json](AUDIT.json) and [RESEARCH_ACCOUNTING.json](RESEARCH_ACCOUNTING.json).

**OBSERVED code path / INFERRED logical traffic:** the frozen full-binding validator
reads 221,837,176 bytes per pass, dominated by the 220,585,024-byte Codex executable.
Seven calls during the pair imply **1,552,860,232 bytes of logical binding reads**.
Three preflight calls imply another665,511,528 bytes, and one audit call221,837,176.
Preparation hashing and other reads are additional. Physical SSD traffic and total
CPU/energy are UNKNOWN; OS caching can change physical cost. These counts are
derived from the executed successful path and frozen file sizes, not I/O tracing.
Thus the 1.9ms recovery figure is not total Helix overhead. This research harness
needs a qualified session-level executable binding before reuse at production
scale; a mutable pathname or unchecked timestamp is not an equivalent replacement.
No such optimization was silently applied to these receipts.

## Qualification

32 offline tests plus7 subtests passed; the initial test collection import failure
was fixed before any inference. Both zero-turn preflights passed. Native/raw usage,
per-segment sums, effective model/effort/config, source and final hashes agree.
Both native attempts are retained (111,991 input /647 output in total); no retry.

This is an exposed40-event/120-note snapshot, not40live model turns or independent
holdout. Arm order was randomly frozen control-first; caching/order effects need
replication before extrapolation. State bindings protect this closed request,
not completeness of caller-supplied authority or hostile concurrent writes.
The comparator is Engine-managed ordinary execution under installed Helix
continuity, not pristine Codex. One separate family pilot cannot be spliced into
another release policy's seven-cell median. No model release, self-deployment,
novel cognition claim or normal Codex-app integration follows.

**Next:** retain this scoped candidate and design the user's harder mixed W50
workflow. Its real semantic checkpoints must share durable completion order with
passive events. Count internal model segments at each checkpoint, not merely four
user turns, and keep ordinary complete model-written answers.
