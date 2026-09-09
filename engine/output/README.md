# Helix Output

Research branch: `Helix-Output` (Git cannot use spaces in a branch name).
Goal: reduce native input and output by 80% while preserving capability and
workflow. No result here establishes that goal or universal intelligence parity.
Model-specific strategies are mandatory; a measured benefit does not transfer
between models, workloads, or cold/warm execution without evidence.

## Fresh Luna High cold-plan diagnostic

One task, three batches, two fresh calls in fixed control/candidate order. Both
arms received the same reusable processing script, data, rules and verification
obligations. Candidate additionally received the skill and explicit local plan
API recipe, and paid for creating its plan. No pre-created plan subsidy.

| Measurement | Ordinary script control | Cold Helix plan | Change |
|---|---:|---:|---:|
| Native input | 134,824 | 218,973 | +62.41% |
| Native output | 3,140 | 4,519 | +43.92% |
| Reported reasoning output | 1,501 | 1,788 | +19.12% |
| Elapsed seconds | 72.163 | 114.835 | +59.13% |
| Commands | 7 | 6 | -1 |
| Generated command bytes | 2,191 | 5,044 | +2,853 |
| Recorded terminal bytes | 21,052 | 42,682 | +21,630 |

Both final artifacts passed exact values/types, including zero-net regions, and
original sources were preserved. The candidate's plan captured three zero-exit
steps. Both agents recomputed complete-source aggregates. Failure recovery was
not exercised, and the candidate's generated verifier printed errors without
setting a failing exit code. Thus artifact success does not certify workflow
failure parity.

Candidate read substantial engine implementation, re-created integration code,
transcribed result values, and repeated verification. It also narrated an
external registration-helper failure absent from the recorded tool sequence.
Both traces contain the same skill-description-budget warning; that warning
does not substantiate the alleged registration failure. Its cause remains
unestablished. This is observable behavior, not an account of private reasoning.

**Decision: reject this cold API-recipe policy for this Luna fixture.** Fewer
commands did not mean less generation. No expansion to other models follows.
Two calls consumed 353,797 input / 7,659 output tokens in total; parent research
is additional. Cached input is included in input totals, not added again.
Preparation/storage counters and hashes are in
[LUNA_COLD_PLAN_RESULT.json](LUNA_COLD_PLAN_RESULT.json). Physical I/O, complete
engine overhead and monetary cost are not fully measured. Raw traces remain
local under `research/plan-native-pair-20260909`; no private environment trace
is published. Three batches are one task, not the requested three-task matrix.

## Research basis

[CodeAct](https://arxiv.org/abs/2402.01030) studies executable code as an agent
action representation. It motivates testing action interfaces rather than just
shorter prose; its results do not qualify our current models or interface.

[Anthropic's code-execution analysis](https://www.anthropic.com/engineering/code-execution-with-mcp)
describes keeping intermediate data in code and reusing functions to avoid
repeated model transit. It also identifies execution infrastructure overhead.
Helix already has a deterministic substrate; our negative result shows that
asking an agent to integrate that substrate can consume the expected benefit.

[Tool-design guidance](https://www.anthropic.com/engineering/writing-tools-for-agents)
motivates clear tool boundaries and controllable response detail. The Helix
inference is to return enough checked evidence for the next decision without
requiring implementation discovery. An API description alone has not achieved
this reliably in our Luna runs.

## Conditional propositions, not novelty or capability theorems

**Dual-budget reuse condition.** For model m, let B0/H0 be baseline/Helix setup
costs and b/h their per-reuse costs, separately for input and output. Assume
these rates remain fixed over N uses and include verification, retrieval and
recovery costs. Eighty percent savings requires, for each dimension d:

`N * (0.2*b[d] - h[d]) >= H0[d] - 0.2*B0[d]`.

Proof: rearrange `H0[d] + N*h[d] <= 0.2*(B0[d] + N*b[d])`.
Both inequalities must hold at the same N. If a dimension's left coefficient
is nonpositive and its right side positive, no reuse count succeeds. Input
amortization therefore cannot establish output amortization. This is elementary
algebra conditional on measured stable rates; current cold totals are not warm
rates. Recovery distributions and uncertainty must be measured before use.

**Generation displacement condition.** A deterministic mechanism saves output
only when generation it avoids exceeds its generated setup, invocation,
interpretation and recovery overhead, including changes in reasoning usage.
This follows by subtracting complete output ledgers. Smaller returned tool
text is input evidence, not proof of this inequality. The new Luna pair is a
counterexample to using fewer commands as a sufficient output-saving criterion.

**Checked execution boundary.** Mechanical execution can replace regeneration
only for a previously specified procedure whose applicability and mandatory
checks remain valid. Unknown semantic decisions stay with the model. Process
success is insufficient for semantic acceptance; failure evidence and exact
sources must remain recoverable. This is a design invariant, not a proof of
intelligence preservation.

## Model-specific development priorities

| Model / High | Evidence | Input direction | Output direction |
|---|---|---|---|
| Luna | Query-V2 regressed both; memory saved input but grew output; cold plan regressed both | Exact selected lines and bounded result packets; bypass unsolicited engine discovery | Test compiled CLI interface and deterministic result assembly, with all creation charged |
| Sol | Query-V2 saved 49.57% input / 50% output on one task | Retain candidate for fresh task qualification; bypass unqualified overhead | Inspect its actual generation before introducing plan machinery; no transfer from Luna |
| Astra | Query-V2 saved 25.67% input / 38.63% output on one task | Request-conditioned evidence remains a candidate | Short exact actions and checked source-copy where a caller renderer exists; charge renderer/setup |

These are priorities, not activated production profiles. The query numbers are
historical development evidence, not measurements of the new plan implementation.
Do not pool model totals to hide an individual model's regression.

## Implemented output attack and remaining work

`plan_cli.py --store STORE execute-spec SPEC [--timeout SECONDS]` now performs
explicit registration and checked execution in one deterministic command. The
specification is the same reviewed JSON used by `register`; id/version remain
immutable. Creation cost and exact attempt evidence are retained in the envelope.
Invalid registration executes nothing; failed steps retain evidence and stop
remaining steps. Semantic review and correct result assembly remain required.
This removes the need to generate Python import/registration/invocation glue and
write a reference file for a cold execution. It does not eliminate specification
creation or prove fewer native tokens. Existing `register` and `run` remain.

Three tests cover successful evidence/cost preservation, immutable identity
rejection without execution, and nonzero step stopping. `trace_profile.py` adds
model-independent observable trace anatomy, explicitly separating bytes from
native token counters; two tests cover event counting and unknown usage. Full
prototype plus output tests: **159 passed**. The frozen native trial used the
older copied engine; it is not a test of `execute-spec`.

Next output mechanisms must address Memory (decision/obligation recovery without
re-generated discovery), Reducers (actionable failure evidence without repeated
diagnostic scripts), and Plans (compiled checked operations with exact artifact
assembly). Each needs independent failure tests before a new frozen native pair.
Do not relax reasoning effort, required checks, source scope or failure reporting.
Retain the requested three-model, three-task and latent-future-relevance gates.
