# Astra matched valid execution/review pair

**OBSERVED: 13.42% total-input savings, 50.20% output savings. Below 80/80.**
Uncached input increased **10.05%**. No monetary-savings claim.

Prospective driver commit `6a0b6b0`; manifest SHA256
`eb6dff5153f5f895de66b2c4ac0f557e84f8bc754152d0b7181f652b10c9b132`.
Two fresh `gpt-6-astra` High calls, randomized order on→off, unchanged native runner,
no retries or budget amendments. Frozen prompts let both arms batch their commands.

Both received the same valid proposed module and exact public contract. Both had
the same full declared checker, ordinary tools and post-execution semantic-review
responsibility. Native staged and checked using ordinary commands; Helix used the
existing apply/check helper. Each could add semantic tests. This is supplied-patch
review, not autonomous repair or a representative workflow suite.

| Metric | Native | Helix | Saved |
|---|---:|---:|---:|
| Input | 127,289 | 110,213 | 13.42% |
| Output | 2,737 | 1,363 | 50.20% |
| Cached input subset | 113,792 | 95,360 | — |
| Uncached input | 13,497 | 14,853 | **−10.05%** |
| Reported reasoning subset | 172 | 70 | — |
| Native segments | 6 | 5 | — |
| Commands | 4 | 4 | — |
| Visible command-output bytes | 5,550 | 14,596 | — |
| Native elapsed seconds | 104.55 | 64.77 | — |
| Semantic disposition | ACCEPT | ACCEPT | — |
| Independent declared-check replay | PASS | PASS | — |

Cache and reasoning subsets are not added twice. Command-output bytes are not
native billed tokens. Setup/preflight receipts remain in the local run root;
physical/SQLite I/O, external process effects and complete effective cost remain
unqualified. These totals do not establish account billing savings or TTFT.

## Semantic and artifact audit

Both final assessments explicitly covered staging before mutation, exact-type
validation, unchanged exception identity, stale-cursor preservation on failure,
list identity, successful length synchronization, empty input and domain limits.
Both performed supplemental tests including self-alias inputs, observation
boundaries, sequence-protocol input and recovery. A finite PASS is not proof of
universal correctness; neither answer claimed it was.

The caller verified each staged source was byte-identical to the proposal, both
staged contract/checker files matched their bound originals, all frozen inputs
were unchanged, and independent declared-check replays passed 2,745 sequences /
8,282 transitions in each arm. Raw event hashes and cumulative native usage were
verified against the runner receipts. The Helix helper ran once. Its final reviewed
candidate was accepted into the Engine-owned reference; original working files
were not modified. This is not a deployment into a user's mutable checkout.

## What the pair changes

**STRENGTHENED, bounded:** caller-owned mechanics can reduce output while retaining
post-execution semantic review. This is the first matched valid pair in this lane
that measures that boundary, rather than assuming review can be omitted.

**WEAKENED:** a compact apply/check operation alone is sufficient for 80/80 in this
short review workflow. The candidate still took four commands and five segments,
and exposed more tool-output bytes than native. Evidence navigation persisted;
this is not an Engine-source discovery problem in the observed trace.

**UNKNOWN:** causal contribution of each instruction, caching, stochastic
variation, order, and voluntary native bookkeeping. Native chose to write review
and evidence artifacts; the common task requested final reasoning and verification
but did not mandate a separate report file. This behavior is observed cost, not an
instruction to pad native work. One pair does not isolate those contributions.

**DO NOT PROMOTE:** no universal route, 80/80 freeze, capability-parity declaration,
or claim that the earlier zero-command coding candidate retains this review.
Do not combine this valid pair with the separate defective-patch safety arm in a
savings denominator. Do not pool it with autonomous coding to manufacture parity.

## Research disposition

Keep the helper as bounded deterministic infrastructure; it has demonstrated an
output benefit here but remains insufficient for the objective. Stop framing this
as a missing reducer problem: larger candidate tool output and persistent model
segments require observable cost diagnosis, not another adapter suite. Preserve
Astra's semantic tests and review. The next hypothesis must target a measured
remaining term and predict a benefit that survives preparation and uncached-input
costs before another call is justified.

Authoritative machine result: `NATIVE_BOUNDARY_PAIR_RESULT.json`. Exact prompts,
manifest, preflight receipts and raw native events remain in local research root
`/Users/mert/Documents/ChatGPT/Helix/research/native-review-pair-v1-20260909`.
HUD shows the fresh pair and its measured deltas separately from safety evidence.
