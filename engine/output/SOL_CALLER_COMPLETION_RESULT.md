# Sol High: caller-side completion, fresh development pair

| Native measurement | Ordinary control | Helix | Savings |
|---|---:|---:|---:|
| Input tokens | 45,393 | 14,824 | **67.34%** |
| Output tokens | 1,427 | 401 | **71.90%** |
| Reported reasoning output | 632 | 364 | 42.41% |
| Tool commands | 2 | 0 | 2 calls removed |
| Generated command bytes | 2,068 | 0 | 2,068 B removed |
| Native elapsed | 61.179 s | 24.826 s | 59.42% |

Both arms received the same complete selection metadata and raw source access.
The control used efficient scripting. The candidate additionally received the
Helix skill and returned six semantic record IDs without tool calls. The caller
resolved a pinned catalog, assembled the exact **6,102-byte** artifact and
verified copied bytes. Both semantic selections and source-preservation checks
passed. The fixture exposes fallback-to-older-revision, string-boolean and
inclusive-expiry errors; it does not exercise late discovery or recovery.

This is evidence for moving mechanical work out of the model loop. It is not an
isolated causal estimate of the skill, a new universal ceiling or a claim that
reported reasoning tokens reveal private cognition. One task does not establish
general capability or workflow parity.

Two calls consumed **60,217 input / 1,828 output tokens**, excluding parent
research. Cached input was 26,240 in the control and zero in the candidate;
gross input savings are not billing savings. Source archive, catalog construction
and completion costs are retained in the JSON report. Physical I/O and money
remain unpriced. No retries or unreported calls were used.

The result misses both the original 80/80 goal and the user's newly accepted
75/75 Sol-candidate threshold. No freeze or promotion follows from this pair.
Next: one independently switchable Sol integration attempt combining scoped
memory/evidence selection, conservative reducers and caller completion; cold
plans off. Thresholds apply separately to input and output with exact checks.

`SOL_CALLER_COMPLETION_RESULT.json` binds the frozen fixture, prompts, dependency
hashes, native trace hashes, native counters and caller receipts. Raw traces stay
local. The driver is `completion_pair.py`; it is a local native-runner adapter,
not a portable provider-neutral runtime. Re-executing it is a new experiment.
