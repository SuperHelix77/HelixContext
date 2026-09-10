# Astra maintenance: recovered 78.38% input / 75.93% output saving

**OBSERVED:** one fresh randomized Astra High pair crosses 75/75 on an existing-code
maintenance task. It does not cross 80/80. Both artifacts pass 23 public/regression
tests, 94 independent cases and the extra semantic probes written by the native
control. This is a bounded development result, not general capability parity or a
production release. Previous coding failures remain separate.

**CONDITIONAL, protocol recovery:** the original runner stopped after successful
publication because it rejected its own empty lock file. No model was rerun. The
[narrow reconciliation](RECONCILIATION.md) admits only that exact caller-owned
metadata, verifies the publication, reconstructs the candidate exactly, reconciles
native counters/configuration and regrades both artifacts. Original results and
native status remain unchanged. A clean frozen-protocol pass is **false**.

| Measure | Native Astra High | Helix Astra High | Saving |
|---|---:|---:|---:|
| Input | 112,677 | 24,356 | 78.38% |
| Output, including reported reasoning | 1,188 | 286 | 75.93% |
| Cached input | 93,824 | 7,040 | Report separately |
| Uncached input | 18,853 | 17,316 | 8.15% |
| Reported reasoning output | 89 | 93 | 4-token increase |
| Model segments | 5 | 1 | 4 removed |
| Native user turns | 1 | 1 | Same |
| Raw model tool calls | 4 | 0 | 4 removed |
| Recorded elapsed seconds | 58.53 | 13.51 | Different timer boundaries below |
| Finite artifact checks | PASS | PASS | No detected loss on these checks |

Candidate elapsed comes from the closed-session receipt because the outer timer
was not written after the stop. It includes in-session caller execution/checking,
but excludes session construction. Control uses the runner's wider arm timer.
Do not interpret their ratio as an exactly matched latency effect.

## What changed, and what did not

The task extends existing Helix Memory search with validated literal-word `all` /
`any` modes while preserving isolation, ordering, limits, exact evidence and index
integrity. Both arms start from the same existing implementation and public tests.
The private reference and grader are absent from model workspaces. Control uses
the default client base; candidate uses the already-existing Astra delegation
kernel, native skill attachment, complete task-file contents and caller mechanics.
This is a **composite product comparison**, not isolated attribution to exact edits.

Native control discovered files, read source/tests, applied its patch and ran tests,
then generated supplemental semantic probes. Helix emitted three exact old/new
edits in one segment. Engine copied 9,815 unchanged bytes and inserted 394 bytes,
producing the 10,209-byte artifact from a 687-byte model response. No fixture-specific
solution was supplied by Engine. Ordinary tools and semantic review stayed available.

The candidate also passes the control's independently generated literal-operator,
Unicode, empty-query, validation, exact-reference and nonmatching-corruption probes.
That is useful finite evidence that caller completion did not lose the observable
checks on this case. It does not prove that every future semantic probe is preserved.

## Cost and residual diagnosis

At the captured current [official API Standard rates](https://developers.openai.com/api/docs/pricing),
the short-context tariff scenario is **$0.341754 → $0.194500, saving 43.09%**.
The long-context scenario is $0.653808 → $0.381850, saving 41.60%. These are
token-weighted tariff scenarios, **not actual Codex included-plan quota, provider
bills or total system ROI**. Rates, timestamp, raw source hash and arithmetic are
in [COST.json](artifacts/COST.json). The live HUD refreshes its official source every
120 seconds and makes rates unknown after 300 seconds without a successful refresh.
Static reports retain their dated rates; they do not pretend to stay current.

**OBSERVED:** control's first segment costs 19,341 input; candidate's single segment
costs 24,356. The candidate's exact task packet is 31,158 bytes versus control's
1,717-byte initial prompt, while client base size is 6,193 versus 21,269 bytes.
Those bytes are observable components, not a causal native-token decomposition.

**INFERRED:** the large headline comes primarily from removing repeated context
exposure. Most removed input was cached. Candidate's prepared evidence makes its
one invocation larger than control's first invocation, so input percentage and
uncached economics diverge. Calling all 24,356 tokens “Helix overhead” is unjustified.

Output beyond reported reasoning falls from 1,099 to 193 tokens. Reported reasoning
does not fall (89 → 93). This supports moving editing/test orchestration and reporting
out of the model on this task; it does not show cheaper hidden cognition.

An 80/80 target allows 22,535.4 input and 237.6 output. The actual candidate exceeds
those by 1,820.6 input and 48.4 output tokens. With this observed single-segment
trajectory there are no remaining model tool calls or continuations to remove.
No reducer or ACK optimization can remove calls that do not exist. These are
trajectory arithmetic limits, not universal model lower bounds. Do not retune this
known fixture to erase the remaining gap after accepting its 75/75 result.

## Complete accounting boundary

All native attempts: **137,033 input, 1,474 output**, including 100,864 cached input,
36,169 uncached input and 182 reported reasoning tokens. Two fresh native identities;
no reused control, model repair or inference retry. Short-tariff native experimental
spend is $0.536254 before coordinator research and Engine costs.

Preparation took 1.069 seconds, including two real scoped memory consultations and
project registration; memory raw responses total 72,099 bytes, retained privately.
Candidate object-store traffic is 30,081 bytes read, 10,027 bytes written, with a
further 10,027-byte read for post-audit reconstruction. Publication reads the prior
10,027-byte destination and writes 10,209 bytes. Exact-edit compilation/assembly
took 0.000422 seconds; caller checks took about 0.564 seconds per arm. Graders,
publication, native capture, registration and receipt files add storage/I/O. Physical
disk traffic and complete machine energy are unmeasured; do not report zero cost.

Private raw native captures total 289,880 bytes and require reading/writing that
evidence. Reconciliation, repeated independent checks and public verification are
additional research costs. One supplemental-probe replay initially used a script
path with the wrong Python import context, failed before checking the task, and
was then replayed through stdin as in the original native command. The initial
error is retained. No additional model call occurred. Coordinator research remains
in the HUD's separate whole-thread ledger, outside pair denominators and unamortized.

## Scope of current Astra evidence

| Family | N | Input saving | Output saving | Status |
|---|---:|---:|---:|---|
| Fresh W50 continuation | 1 | 98.26% | 90.72% | Bounded 80/80 |
| Earlier varied coding | 3 | Median 83.07% | Median 60.02% | 75/75 unqualified |
| Existing-code maintenance here | 1 | 78.38% | 75.93% | Recovered bounded 75/75 |

Do not blend these into a convenient global median. Models/task families and
protocol qualifications remain explicit. Helix remains active; ordinary semantic
execution remains available when delegation cannot resolve a task.

## Decision and reproduction

Retain this bounded candidate and its exact-edit machinery. Correct the caller's
publication-metadata inventory before another production-oriented run. Keep the
original failed observer protocol frozen. No new Astra inference is justified by
trimming this fixture; further model transfer requires its own frozen controls and
must not inherit this result as proof of general coding economics.

Frozen experiment: `edc77d5`, [FROZEN.json](FROZEN.json). The original native captures,
memory and configuration stay private. [RECONCILED_RESULT.json](RECONCILED_RESULT.json)
contains audited identities/counters and hashes. [Public artifacts](artifacts/MANIFEST.json)
include exact task outputs, usage excerpts, model edits and control-generated probes.

Run `python3 docs/research/maintenance-copy-v1/artifacts/verify.py` for the public
derivative checks, both finite graders, exact reconstruction and supplemental probes.
The published excerpts are not independent provider attestation; the original audit
checks their full private raw streams. Normal Codex-app integration and general
release remain unqualified.
