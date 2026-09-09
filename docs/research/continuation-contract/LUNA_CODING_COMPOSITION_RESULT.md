# Luna coding composition: fresh 75/75 candidate

**OBSERVED:** Combining the already frozen V7 delegation kernel with V3 caller
preparation/completion cleared the accepted 75/75 criterion on one fresh known
coding pair. **80/80 did not pass.** No new kernel prose, lower reasoning effort,
output cap or tool restriction was used. No general release is claimed.

| Counter | Fresh native | Fresh composed Helix | Saved |
|---|---:|---:|---:|
| Input | 120,350 | 16,642 | 86.17% |
| Output, including reported reasoning | 3,630 | 760 | 79.06% |
| Cached input | 94,720 | 6,912 | Subset; not additional input |
| Uncached input | 25,630 | 9,730 | 62.04% |
| Reported reasoning output | 1,621 | 516 | Subset of output |

Both arms passed the four original tests and the 4,433-case oracle. Exact source
publication and protected tests/settings were verified. The candidate used one
segment and zero model tool calls. It retained ordinary tools and semantic probes;
the caller performed staging, checks and publication. This changes responsibility,
not the task's required behavior.

The [fresh audit](LUNA_CODING_COMPOSED_FRESH_PAIR_RESULT.json) and
[freeze receipt](LUNA_CODING_V1_75_FREEZE.json) bind exact streams, source artifacts,
kernel, protocol and outputs. Randomized arm order was native then Helix. N=1
known coding pair: its median equals the observation and uncertainty is not
estimated. There was no retry. The profile is
`LUNA_CODING_V1_75_CANDIDATE`, not a model-wide release.

## Why this composition was tested

The earlier V7 general coding trial still paid for setup and mechanics. The newer
V3 caller-owned path removed that work but used the default base. Their composition
had not been measured. The task prompt, skill and local preflight instruction bytes
were required to equal V3. The new candidate used the exact prior V7 kernel.

An initial adaptive candidate used 16,623 input / 632 output tokens. Against a
retained fresh native control that was 90.85% / 83.67%. Against the retained V3
default-base candidate, input/output fell 13.36% / 53.90%, but uncached input
**increased 5.53%**. The fresh pair above then tested the same configuration.
Neither comparison proves the kernel caused all output improvement: sampling and
trajectory variation remain. The earlier unfavorable V3 fresh pair remains visible.

The [offline anatomy](LUNA_CODING_COMPOSITION_ANATOMY.json) found that the client
base fell from 17,766 bytes / 3,552 proxy tokens to 6,187 recorded bytes / 1,033
proxy tokens. The 2,519-token proxy difference is close to the adaptive streams'
2,563 native-input difference; this is not exact causal token attribution.
Server-side instructions remain unknown.

## Audit amendment, not a model rerun

The first audit required the 6,188-byte kernel file to equal raw native metadata
byte-for-byte. Codex recorded the exact file **minus its final newline** and marked
it custom. Audit V1 therefore stopped. V2 permits only that exact one-byte
normalization and preserves both hashes. Native execution and task graders were
unchanged. The revised check was frozen before the fresh pair. The original
auditor remains in Git history; no unfavorable model sample was discarded.

## Additional capability checks and limits

A [post-hoc domain audit](LUNA_CODING_DOMAIN_AUDIT.json) independently used rational
arithmetic for 1,200 varied cases, including up to 2,048-bit totals, plus container,
integer-subclass, empty/zero, exact-sum, tie and invalid-input checks. Each arm passed
1,213 valid and 18 invalid cases without modifying its inputs or protected files.
These extra checks were designed after source inspection; they are not holdout
model evidence or proof over arbitrary overloaded Python objects/resource limits.

For ordinary nonnegative integer inputs with weight sum W>0, the inspected
implementation computes q_i=floor(T*w_i/W), then adds one to the largest
T−sum(q_i) remainders, breaking ties by original index. This preserves integer
allocations and exact sum T. Validation and the zero/empty branches remain explicit.
This arithmetic argument does not certify model intelligence or an entire workflow.

The caller's public/oracle check took 0.068 s; memory preflight took 0.180 s and
retained 13,080 raw bytes, excluding eight other-scope hits under the benchmark's
no-other-runs rule. Raw capture retained 128,264 bytes for native and 66,636 for the
candidate. The new adaptive stream plus fresh pair consumed **153,615 input and
5,022 output tokens** in total. Research/coordinator effort, complete physical I/O
and production isolation/delivery costs are outside those receipts.

The native control reported that its memory helper failed on an out-of-directory
permission check. The candidate's caller preflight succeeded outside the model
sandbox. That difference is part of this composite product comparison, not an
isolated base-kernel effect. Both model sessions used the same workspace-write
sandbox; the caller check process is a separate execution boundary. Economics
under the normal desktop permission configuration still need qualification.

Publication checks the staged artifact and uses a one-file atomic replacement.
The surrounding checks do not exclude an uncooperative writer between the last
check and replacement. Concurrent-writer isolation and application delivery remain
production gaps; these results apply to the controlled fixture.

The new kernel/contract is exported as a
[portable candidate](../../../engine/profiles/luna-coding-v1-75/README.md). It is not
globally activated. Existing research callers are not yet a production Codex-app
adapter. Engine remains active on ordinary semantic routes; unsupported work must
not be silently treated as mechanically resolved.

## Decision

Freeze this coding configuration at the accepted 75/75 boundary; do not tune the
same fixture to move 79.06% to 80%. The remaining work is prospective varied-task
qualification, W50 lifecycle closure and production caller/application integration.
Sol and Astra retain separate qualification requirements. Broad intelligence and
workflow parity and the full 80/80 goal remain open.
