# Integrated V2: 70.53% input / 73.10% output

V2 passed the exact artifact and source-preservation gates, but remains below
75/75. **No Sol freeze.** One fresh development pair, same previously used task
family, High reasoning throughout. Two calls and no experiment-level reruns.

| Metric | Fresh control | V2 candidate |
|---|---:|---:|
| Native input including cached | 107,537 | 31,693 |
| Native output including reported reasoning | 2,394 | 644 |
| Cached input, subset | 85,632 | 15,232 |
| Uncached input | 21,905 | 16,461 |
| Reported reasoning output, subset | 1,338 | 482 |
| Native elapsed seconds | 92.071 | 38.673 |
| Exact artifact bytes | 6,102 | 6,102 |

Uncached-input saving is **24.85%**, not 70.53%; no monetary claim follows from
aggregate input counts. Total reported experimental spend: 139,230 input /
3,038 output tokens. Parent research and physical/server costs remain additional.

V2 changed the evidence and admission contract identified in the
[three-trial audit](SOL_THREE_TRIAL_AUDIT.md): complete small history, source-bound
metadata, task-facing preflight, and caller-owned task-local skill registration.
The candidate made one command, reading `helixcontext/SKILL.md`; no file discovery,
policy reread, payload sample, selector generation or Engine implementation read
appears in its trace. Neither arm's stderr records transport retries or sandbox
denials. This does not prove absence of unreported server costs or hooks.

Registration used the actual native thread ID, verified the pinned skill hash,
and cost 0.072 seconds. Its observer read 101 bytes; the registry retained 55,067
file bytes. Candidate evidence store retained another 115,794 bytes. The JSON
report preserves both runtime-instance I/O ledgers; do not add overlapping
cumulative snapshots. SQLite/physical I/O and money remain unknown.

V2's initial supplied prompt was **8,785 bytes**, slightly larger than V1's
8,540. It nevertheless used far fewer native tokens. The result supports testing
clearer task/verification boundaries instead of optimizing representation bytes
alone. Bundled changes and sampling prevent a single-component causal claim.

To reach 75% against this control, candidate input must be at most 26,884 tokens
and output at most 598. It missed by **4,809 input / 46 output tokens** after
integer rounding. The remaining skill-read round trip is a concrete V3 target;
its exact causal token cost is not identifiable from aggregate receipts. Do not
remove required skill loading, lower High or suppress semantic checks to close
this gap. Native skill attachment is the next mechanism to investigate.

210 engineering tests passed before launch. Bounded artifact correctness is not
general intelligence or long-horizon workflow parity. V2 is implemented and
measured, not frozen as a 75/75 candidate.

[Machine-readable result and hashes](SOL_INTEGRATED_V2_RESULT.json).
