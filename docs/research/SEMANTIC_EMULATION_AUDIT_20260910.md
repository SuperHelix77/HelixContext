# Can Helix make semantics cheaper without removing intelligence?

**Decision: HOLD experiments and implementation.** Research and a read-only audit
of existing receipts identify no qualified general-purpose “semantic simulation”
mode for hosted Astra. There is a useful narrower possibility: avoid recomputing
an already established decision when its authority and dependencies remain valid.
That is conditional reuse, not replacement of new semantic judgment.

Evidence cut: 2026-09-10, active `Helix-Output` commit `6831657`. External primary
sources were read before the failure reconciliation below. No new native call,
offline benchmark, training run, kernel, reasoning-effort change, or deployment
was performed for this research. Coordinator research still consumes model/tool usage;
zero new calls means zero additional benchmark invocations. Source/hash inspection and arithmetic over old
receipts are recorded in [OBSERVATIONS.json](semantic-emulation-20260910/OBSERVATIONS.json).

## 1. The ambiguity in “simulate semantics”

Three different quantities must remain separate:

1. A **user turn** submitted to the native runtime.
2. A **model segment** between tool interactions within that turn.
3. The **semantic work** of interpreting requirements, selecting actions,
   resolving conflicting evidence, and judging whether checks are sufficient.

One user turn can contain many model segments. Asking a model to simulate an
interpreter or reason silently still invokes that model; it may alter generation
but does not make the underlying computation free. Conversely, an authorized ACK
can require no model segment because the transition is already specified exactly.

**CONDITIONAL:** fewer words, fewer forward passes, lower latency, fewer billable
tokens and preserved task capability can coincide. None implies all the others.
We must count reported reasoning as part of output, and cache as a subset of input.

## 2. External research: what actually survives

These are architectural precedents and bounded experiments on other models, not
Helix replication. Paper versions and inspected sections are in the
[source index](semantic-emulation-20260910/SOURCE_INDEX.json).

| Approach | Primary finding and limit | Verdict for current Astra |
|---|---|---|
| Continuous latent reasoning | Coconut feeds hidden states back as embeddings and uses staged training. Its Table 1 improves synthetic logical reasoning, but GSM8K is **34.1% versus 42.9%** for its language-reasoning baseline. Latent computation still takes model passes. [Coconut, v3, §§4–5](https://arxiv.org/html/2412.06769v3) | **DEFER.** Interesting model research; no hosted-Astra weight/embedding control established and no general parity. A “think latently” instruction does not implement this architecture. |
| Recurrent internal computation | Huginn iterates a recurrent block, trading internal computation for capability. The reported prototype has 3.5B parameters and was trained on 800B tokens. This is a model architecture, not a client instruction. [Huginn, v1](https://arxiv.org/html/2502.05171v1) | **DEFER.** Could be a future local-model study. It does not demonstrate cheap, unchanged Astra cognition. |
| Training latent reasoning more aggressively | A subsequent study found mathematical-performance and stability limitations under both supervised and reinforcement-learning variants. This is scoped counterevidence to universal no-loss latent compression, not a proof against all latent methods. [Özeren and Aßenmacher, v1, §6](https://arxiv.org/html/2512.11816v1) | **WEAKENS** confidence in adopting latent reasoning without capability testing. |
| Short textual drafts | Chain of Draft uses shorter intermediate text. On its GSM8K comparison, GPT-4o falls **95.4%→91.1%**, and Claude 3.5 Sonnet **95.8%→91.4%**, relative to their verbose reasoning baselines. Other tasks perform differently. [Chain of Draft, v2, Table 1](https://arxiv.org/html/2502.18600v2) | **REJECT as a no-loss claim.** Short drafts are testable prompting, but not evidence for Astra parity or our unchanged final-answer contract. |
| Reusable reasoning procedures | SELF-DISCOVER prepares a task-level structure and then applies it to instances. Its large compute comparison is against inference-heavy self-consistency, not ordinary Helix/Astra execution. Preparation and the per-instance structure both have costs. [SELF-DISCOVER, v1, §§2–3](https://arxiv.org/html/2402.03620v1) | **CONDITIONAL.** Reuse is plausible only with amortization and applicability checks. Do not repeat Luna's cold-plan integration tax. Store auditable procedure facts, not private chain-of-thought. |
| Program-aided solving | PAL separates translating a natural-language problem into a program from executing that program. Its interpreter performs arithmetic/symbolic operations; the model still chooses the program. [PAL, ICML 2023](https://proceedings.mlr.press/v202/gao23f.html) | **SURVIVES within existing Engine mechanics.** It does not solve requirement adequacy, and generated glue can cost more than the operation it replaces. No new interpreter framework is justified. |
| Exact speculative decoding | A draft proposes tokens and a target evaluates probability distributions with a correction rule. Under its assumptions, target sampling distribution is preserved while serial decoding can accelerate. [Leviathan et al., ICML 2023, §2](https://proceedings.mlr.press/v202/leviathan23a/leviathan23a.pdf) | **DEFER to a controllable inference backend.** This is not “ask Luna, then ask Astra whether it looks right.” Exact correction requires decoder access unavailable in the inspected Helix interface. Latency savings do not establish hosted token-bill savings. |
| Incremental computation | Self-adjusting computation tracks dependencies and propagates changes rather than repeating an entire known computation. [Acar, CMU thesis](https://csd.cmu.edu/academics/doctoral/degrees-conferred/umut-a-acar) | **STRONGEST transferable principle, CONDITIONAL.** Program dependencies can be instrumented; completeness of dependencies for an open-ended semantic conclusion is not automatically knowable. |

### Supported hosted-model boundary

**EXTERNAL:** current official guidance says Astra has no `none` reasoning effort
and supports persisted reasoning; it also lists log-probability controls as
unsupported. [Astra guidance](https://developers.openai.com/api/docs/guides/latest-model)

**EXTERNAL:** OpenAI documents that reasoning tokens are billed output. Persisted
reasoning remains opaque; continuity is supported through response history or
encrypted items. `reasoning.context` distinguishes current-turn from earlier-turn
reasoning on supported models. Its effective value should be observed rather
than guessed. [Reasoning guide](https://developers.openai.com/api/docs/guides/reasoning)

**OBSERVED locally:** the runner delegates a persistent native thread to Codex.
The inspected `TurnStartParams` has effort, model, additional-context and tool-output
fields, but no direct `reasoning.context` property. That does not prove an internal
or configuration route cannot exist. No hidden-state editing or custom decoder
interface was established. We did not inspect or modify private reasoning content.

**UNKNOWN:** hosted internal algorithms, backend reasoning preservation details,
and server-added context. A client schema cannot prove their absence. There is no
evidence here that Helix can switch Astra into Coconut or control its latent steps.

## 3. What failed first, and what the failures mean now

Order below follows the mechanism progression; newer receipts override early
projections. These are exposed development cases with differing contracts, not
one interchangeable release population.

| Mechanism / evidence | Observable outcome | Consequence for semantic emulation |
|---|---|---|
| Cold model-facing plans | Luna **134,824→218,973 input; 3,140→4,519 output**. [Output history](../../engine/output/README.md) | An abstraction can create model work. A semantic simulator that must be learned or integrated inside the task risks the same failure. |
| Source plus caller preflight | Astra coding **98,251→127,397 input; 1,464→1,371 output**. Supplied source and skill were reread; both arms passed finite behavioral checks. Evaluator-corrected development evidence. [Coding result](../../engine/output/ASTRA_PATCH_RESULT.md) | More prepared context does not imply less model computation. Source duplication is observable; hidden distrust is not. |
| Mechanical PASS treated as insufficient | Astra reproduced an empty-batch/alias-cursor defect after successful mechanical checks. [Safety challenge](continuation-contract/NATIVE_BOUNDARY_SAFETY_RESULT.md) | New semantic investigation had real value. A cheap automatic ACCEPT based on those checks would lose capability. |
| Mandatory review, then moving review earlier | Post-review pair saved **13.42% input / 50.20% output**. A separate prereview pair saved **32.75% / 9.59%**, with uncached input increasing. Prereview still contained four model segments. [Post-review](continuation-contract/NATIVE_BOUNDARY_PAIR_RESULT.md), [prereview](continuation-contract/NATIVE_PREREVIEW_PAIR_RESULT.md) | Eliminating a separate final invocation did not eliminate the initial inspection/probing cycle. The pairs differ; their numerical gap is not a timing-only causal effect. |
| Shorter mechanical-authority kernel | Defect case improved input; valid case regressed **−22.91% input / −27.77% output** and added four passing semantic probes. [Kernel audit](continuation-contract/BASE_KERNEL_PAIR_RESULT.md) | Changing instructions changed observed work, not just text length. No single clause was causally isolated. Extra probes cannot be declared useless merely because they passed. |
| Exact previous-test reuse, original Astra base, XHigh | Latest two-case medians **35.86% input / 20.44% output**, uncached **−15.39%**; dated short API-equivalent median **8.68%**. The 20% weighted admission gate failed. [Current result](astra-reuse-v1/RESULT.md) | Reuse removed repeated execution but retained source/coverage inspection and a new decisive probe. Mechanical reuse is useful; semantic-work removal is unqualified. |
| W50 state transitions | Historical selector/caller-rendered Astra result saved **98.26% / 90.72%**. [W50 transfer](continuation-contract/TRANSITION_TRANSFER_V1_RESULT.md) | Forty-nine resolved ACKs can disappear as model invocations. This does not show that the final unresolved policy judgment disappeared, or qualify caller-rendered finals under the current contract. |
| Current full model-written W50 attempt | Control stopped at ACK 2: `ACK E02.` instead of `ACK E02`; candidate never ran. **40,413 input / 15 output** retained. [Stopped receipt](w50-native-final-v1/STOPPED.json) | A protocol-format failure, not evidence against or for semantic emulation. Punctuation attribution is plausible, not isolated. V2 remains untested and unlaunched under the research pause. |

No failed attempt is silently retried, removed from accounting, or repaired into
a passing final answer. The original renderer-based wins remain historical; they
are not pooled with the stricter model-written-final cohort.

## 4. New read-only findings from the latest Astra receipts

We verified 20 public file/report bindings, all four private native/raw stream
hashes, public per-segment sums, final-answer hashes, and native request counts.
We did not rerun probes or benchmarks. The previously recorded cross-replays remain
finite semantic evidence, not new independent replication.

### Cross-turn persistence is not the missing turn here

Every latest review arm started **one thread and one user turn**. Ordinary valid
review used five segments; prepared valid review used three. Defect review used
six versus four. These continuations already occurred within the same native turn.
We have no observed thread-reset defect to fix. Earlier-turn reasoning reuse does
not, by itself, explain how to eliminate those within-turn segments.

### Even free reported reasoning would not be enough on these fixed trajectories

Let `O` be reported total output and `R` its reported reasoning subset. Consider
the deliberately unrealistic bookkeeping operation `O_candidate := O − R`, with
all other output held constant:

| XHigh case | Control O | Candidate O | Candidate R | Candidate O−R | Hypothetical saving vs control |
|---|---:|---:|---:|---:|---:|
| Valid | 1,679 | 1,089 | 558 | 531 | 68.37% |
| Default-limit defect | 1,619 | 1,526 | 532 | 994 | 38.60% |
| Two-case median | | | | | **53.49%** |

**CONDITIONAL ARITHMETIC, not a lower bound:** this does not predict an actual
intervention, input changes, or preserved answers. A different trajectory could
change other tokens too. It does establish that merely deleting the reported
reasoning subset from these recorded candidates cannot produce a 65% median
output saving. Other output includes tools, narration, final text and formatting;
we do not relabel it all as removable mechanics.

In the prepared valid arm, its final segment alone cost 793 output tokens,
including 516 reported reasoning tokens. Retaining only that segment would save
52.77% against its observed control, with unchanged segment cost. This independently
weakens “just preload everything and the target follows.”

### Why current checks cannot stand in for semantics

Both prepared cases passed 23 public tests and two previous Astra probe programs.
The defective version changed the omitted search limit from 10 to 9. Both native
review arms wrote and executed a new 12-record witness, then rejected the defect.
The old tests established their checked predicates; they did not establish API
compatibility. Adding this now-known test improves regression coverage, but it
cannot make the next unseen semantic defect impossible.

## 5. Two conditional propositions, not new grand theorems

### Decision-relevant information must reach the deciding mechanism

Suppose two allowed states require different decisions, but a system gives the
deciding component identical observations and prevents further retrieval. That
component cannot guarantee the correct decision for both states. A deterministic
component returns the same answer; a stochastic component has the same answer
distribution. At least one required distinction remains unavailable.

This elementary argument does not prove all compression is lossy. It identifies
the obligation: preserve a sufficient distinction or a route to retrieve it. In
Helix, a PASS-only packet misses the default-limit distinction. In a future-relevance
case, a new task can change which old facts are required; prior relevance decisions
must not permanently hide them.

### Known deterministic consequences can be reused without new model judgment

For a deterministic operation `f`, if all inputs, dependencies and authority that
determine `f` remain bound and unchanged, a previously established `f(x)` remains
the same result. Reuse additionally requires intact evidence and authorized effects.
This establishes result consistency, not that the original semantic choice or
specification was adequate. Unknown dependencies invalidate the shortcut.

These propositions explain both outcomes: ACK elision works within an explicit
grammar; open-ended code approval cannot be inferred from an incomplete test suite.

## 6. Best candidate: reuse established decisions, compute only unresolved changes

**HYPOTHESIS, not implemented:** use the existing state/receipt substrate to bind
completed obligations individually. Do not build another generic plan language,
simulator prompt, memory platform or model-facing registration workflow.

- **Caller:** binds task/authority/repository versions before inference; separates
  `pending_mechanics` from `unresolved_semantics`; validates reuse eligibility and
  prepares the relevant state. Unknown classification retains normal model access.
- **Helix Context:** keeps current requirements and unresolved questions available,
  presents exact relevant evidence, and preserves retrieval/skill continuity. It
  does not tell Astra that passing tests settle adequacy or impose a fixed probe cap.
- **Engine:** executes already authorized deterministic steps, records exact
  evidence, publishes receipts transactionally, and performs idempotent delivery.
  A failed mechanical operation is not a successful semantic completion.
- **Persistent state:** versioned facts, completed actions, exact artifacts,
  assumptions, dependency bindings, unresolved questions and checked/unchecked
  obligations. Facts and decisions have different authority and invalidation rules.
  No private chain-of-thought is extracted, reconstructed or stored as a substitute.
- **Astra sees:** the current task, exact relevant source, what is mechanically
  established, what changed and what remains unresolved. It still decides meaning,
  correctness, coverage, novel probes and whether more evidence is necessary.
- **Astra need not regenerate:** existing registrations, equivalent hash checks,
  exact copy procedures, ACKs or bookkeeping whose prerequisites are established.
  Source/test access remains available; an inspection is not automatically waste.
- **Failure/recovery:** optional context failure falls back to exact/native access
  within the active Engine. Stale authority, conflicting roots, unknown operations
  and unresolved obligations block semantic execution and trigger refresh or model
  judgment. Duplicate delivery cannot repeat side effects. Failed publication keeps
  the last committed head authoritative.

Reuse is invalidated by task/contract changes, newly relevant evidence, dependency
changes or unknown closure, executor/checker changes affecting the claim, conflicting
results, expired authority, failed recovery and explicitly requested fresh review.
An unchanged file hash alone cannot override a new user question. Cold evidence
must remain discoverable when relevance changes unexpectedly.

**Current final-answer contract remains binding:** ordinary complete model-written
prose/code, or JSON when the task originally requests JSON, after relevant actual
execution evidence. No selector substitution, caller-composed final, or prewritten
answer delivery is adopted. Thus zero model invocations for an entire novel task
are not the objective under this contract. The opportunity is removing redundant
intermediate invocations while preserving the model's real decision and final.

Normal Codex-app pre-inference interception is still unproven. A skill begins too
late to cancel the invocation that loaded it. The research caller demonstrates a
boundary, not a shipped desktop interception point.

## 7. Economics before another experiment

For a reuse opportunity, define baseline cost `C_A`, eligibility/preparation cost
`C_g`, deterministic reuse cost `C_d`, fallback overhead `C_f`, construction cost
`C_build` amortized over `N` uses, and safely reusable fraction `r`:

`E[C_H] = C_g + r*C_d + (1-r)*(C_A + C_f) + C_build/N`.

Assuming the same `C_A` for the compared opportunities, positive expected saving
requires `r*(C_A-C_d) > C_g + (1-r)*C_f + C_build/N`. Heterogeneous tasks require
per-task accounting before aggregation. Lower-model proposals need their own
generation, verification, rejection and fallback terms; a small draft is not free.

Measure input, cached/uncached input, output/reasoning, tool calls, latency,
preprocessing, storage, retrieval and recovery separately. A single scalar cost
requires declared units and prices; model tokens and Engine bytes cannot simply
be added. API-equivalent cost is not included-plan quota. Current memory read
amplification and ledger full-prefix verification remain systems costs, not reasons
to weaken exact recovery.

No observed safe reuse fraction for general Astra coding currently supports a
65/65 median forecast. The two-case arithmetic above is diagnostic and stays
outside the fixed seven-cell release cohort. No release or self-deployment follows.

## 8. Smallest falsifier and explicit stop conditions

**Proposed only; not run.** Before any model experiment, challenge the eligibility
decision with an already available receipt and three states:

1. Identical bound task/state: reuse only its explicitly checked obligations.
2. Changed dependency with an old receipt: reject stale reuse.
3. Correct hashes and PASS results, but the known default-limit semantic defect:
   never infer overall ACCEPT from those results; preserve unresolved review.

Add a new-task/late-relevance case before treating the gate as long-horizon safe.
If the gate needs a model to decide every eligibility question, count that call;
it may eliminate the intended saving. If it cannot distinguish case 3 without
open-ended judgment, that is a legitimate model boundary, not a reason to hard-code
this defect into a supposedly universal semantic verifier.

A future native falsifier would compare one ordinary and one reuse arm on the
same task, base, effort, tools and final contract, with both valid and held-out
defective states. Capability checks must cover actual defects, required actions,
evidence recovery and final claims, not a fixed count of probes. This is a future
design only, not a launch authorization or present certification.

Stop before a native call if no measured obligation can disappear, required
dependencies cannot be bound, or preparation adds another model-mediated setup
cycle. Stop promotion on lost defects/actions, stale acceptance, altered final
authorship, missing costs, or economic regression. Preserve negative receipts.

**Terminal verdict:** genuine latent/internal reasoning is real research, but we
cannot emulate it on hosted Astra with a skill and claim unchanged intelligence.
The defensible target is cheaper reuse of *established* semantics plus ordinary
Astra reasoning for new semantics. The current evidence is not strong enough to
launch a semantic-emulation experiment or change this agent's reasoning policy.
W50 V2 and further native attacks remain on hold pending a mechanism that survives
these analytical and capability conditions.
