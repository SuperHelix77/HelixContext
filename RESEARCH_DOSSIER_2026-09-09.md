# HELIX — MECHANISM DISCOVERY, COST-BOUND ANALYSIS, AND ARCHITECTURE TRANSFER
### A hostile research dossier on the 80/80 objective

**Date:** 2026-09-09 · **Auditor:** independent researcher (no implementation performed)
**Repository:** `SuperHelix77/HelixContext`, branches `main` (28 commits), `helix/named-plans-v1` (38), `Helix-Output` (41) — all three inspected.
**Reproduction scripts:** `research/cache-adjusted-ledger/{ledger.py,dollar.py}`

---

## 0. How to read this document

**Claim tags used throughout:**

| Tag | Meaning |
|---|---|
| `OBSERVED` | Directly present in a repository receipt with hash commitments |
| `REPLICATED` | Measured more than once, on more than one task or model |
| `INFERRED` | Derived from observation by explicit arithmetic or logic, assumptions stated |
| `HYPOTHESIS` | Proposed causal mechanism, not yet measured |
| `CONDITIONAL` | True only if stated assumptions hold; assumption is named |
| `UNKNOWN` | Not measurable from available traces; deliberately not guessed |

**A note on what the repository is.** Every number in the repository that matters was recomputed
from the raw receipt files, not from prose. Where prose and receipts disagree, the receipt wins and
the disagreement is reported. Two things you asked me not to do — manufacture precision, and
inherit conclusions — were the two things the repository most needed.

---

## 1. EXECUTIVE VERDICT

### 1.1 The one-sentence answer

**Helix's problem is not that its mechanisms are weak. It is that it has been measuring the wrong
denominator, and the denominator error is large enough to have misrouted the last several
experiments.**

### 1.2 Seven findings, in order of importance

**F1 — The computation-placement hypothesis is CONFIRMED, by the cleanest natural experiment in the
repository.** `OBSERVED` + `REPLICATED`

The *same* mechanism — model selects record IDs, a deterministic renderer assembles exact bytes —
produced a **94.8% input regression** for Sol when the model had to write an ID file and invoke a
helper itself (`engine/render-pilot/README.md`: 58,386 → 113,760), and a **67.3% input saving** when
the caller owned the assembly and the model returned six IDs with zero tool calls
(`engine/output/SOL_CALLER_COMPLETION_RESULT.json`: 45,393 → 14,824). Astra moved the same way:
−89.2% → +25.7%. Nothing about the evidence representation changed between those two experiments.
**Only the location of the mechanical work changed.** That is as close to a controlled demonstration
of computation placement as this corpus contains.

So: the working hypothesis in §1 of the brief is correct, and it is correct *strongly* — but it is
being tested on the wrong axis (see F2).

**F2 — Gross-token accounting is not just imprecise; it is biased in *both directions*, and the
direction is model-specific.** `OBSERVED` + `INFERRED`

70.48% of all input tokens in the project corpus are *cached* reads (`results/cost-audit.json`:
14,609,152 of 20,728,819). Cached reads are billed at roughly 0.1× the fresh-input rate on the
GPT-5.x family [1](https://openai.com/index/introducing-gpt-5-2/)[3](https://crazyrouter.com/en/blog/gpt-5-pricing).
Therefore the percentage Helix has been reporting is not the percentage that matters, and — critically —
it is wrong in *opposite directions on different experiments*:

| Experiment | Gross input saving | Full-price (uncached) input saving | Direction of error |
|---|---:|---:|---|
| Sol caller-completion | **67.3%** | **22.6%** | gross **overstates** 3.0× |
| Astra query-V2 | **25.7%** | **0.13%** | gross **overstates** ~200× |
| Sol query-V2 | 49.6% | **77.9%** | gross **understates** 1.6× |
| Luna V3 aggregate | 25.3% | **53.6%** | gross **understates** 2.1× |

Astra's 25.67% headline input saving reduces full-price input by **7 tokens out of 5,365**
(`NATIVE_RECEIPT_RECHECK.json`: 44,405−39,040 = 5,365 → 33,006−27,648 = 5,358). Its entire measured
input win is on tokens the provider discounts by 90%.

**F3 — Under a realistic price vector, Helix V3 is substantially more valuable than published, and
the gap is ~1.7×.** `CONDITIONAL` on GPT-5.x rates; the actual models have **no published rate card** (`UNKNOWN`)

| Model | Published gross input saving | Published gross output saving | **Conditional dollar saving** @ $1.25 / $0.125 / $10 per M |
|---|---:|---:|---:|
| Luna High | 25.28% | 32.93% | **45.8%** |
| Sol High | 20.99% | 5.36% | **35.4%** |
| Astra High | 17.11% | −4.41% | **32.0%** |

(Sensitivity across cache discounts k∈{1.0,0.25,0.10} and output:input price ratios p∈{4,8,16}:
Luna 25.5→46.6%, Sol 20.4→36.0%, Astra 16.5→32.6%. The ranking is stable; the magnitude is not.)

The reason is structural: Helix removes uncached input and output, which are the *expensive*
tokens, and leaves cached prefix re-reads, which are the *cheap* ones. **Helix has been
under-advertising itself under the one metric that maps to money, while over-advertising under the
one it has been reporting.** This inverts the strategic picture in §7 of the brief: Astra is not
17% cheaper, it is ~32–43% cheaper per dollar on the tasks where its output did not regress.

**F4 — 80% *gross* input reduction is structurally impossible on the long-horizon workloads under
this harness, and I can bound it.** `CONDITIONAL` + `OBSERVED`

Per-turn native input decomposes into a host-owned prefix plus caller/turn content:

| Model | Task | Input/turn | Cached (=host prefix)/turn | Caller prompt/turn | Turn work/turn | **Ceiling on gross input saving** |
|---|---|---:|---:|---:|---:|---:|
| Luna | W50 | 17,906 | 11,499 | 3,390 | 3,016 | **35.8%** |
| Luna | L40 | 20,782 | 10,564 | 6,099 | 4,118 | **49.2%** |
| Sol | W50 | 18,520 | 12,751 | 3,390 | 2,378 | **31.2%** |
| Sol | L40 | 21,483 | 9,662 | 6,098 | 5,722 | **55.0%** |
| Astra | W50 | 18,665 | 12,695 | 3,390 | 2,579 | **32.0%** |
| Astra | L40 | 21,909 | 11,376 | 6,099 | 4,433 | **48.1%** |

The "ceiling" column is the uncached fraction: the maximum gross saving attainable even if Helix
drove *all* non-cached input to zero at zero added cost. It is an upper bound, not a forecast.
Helix V3 realised 20.6% / 27.8% (Luna), 15.2% / 26.6% (Sol), 9.7% / 24.3% (Astra) against those
ceilings — i.e. **it captured roughly 55–75% of the available uncached input on L40 and 40–60% on
W50.** The remaining headroom is real but bounded at 15–28 gross percentage points, not 55.

The host prefix P ≈ 10,500–12,800 tokens/turn is re-paid every single turn and Helix cannot touch it
in this harness (`--ephemeral`, fresh `codex exec` per turn, `skills.max_context_tokens=512` — see
`benchmarks/frozen-high/run_benchmark.py`). **This is the single largest irreducible cost term in
long-horizon work, and the only lever on it is N, the number of turns.**

**F5 — The output ceiling is a reasoning floor, not an engineering floor.** `OBSERVED` + `CONDITIONAL`

In the winning Sol pair, residual output is **401 tokens, of which 364 are reported reasoning
(90.8%)**; non-reasoning output is 37 tokens. Helix has already removed essentially all
non-reasoning generation on that task. Project-wide, reported reasoning is 44.80% of output
(`results/cost-audit.json`: 71,073 of 158,659). The repository already derived this bound
(`engine/prototype/OUTPUT_FRONTIER.json`) and then did not act on it: for the memory candidate,
reaching 80% output would require eliminating **521 reasoning tokens even if every other generated
token disappeared.** `CONDITIONAL` on the assumption that `reasoning_output_tokens ⊂ output_tokens`
(which the repository adopts from OpenAI's documented convention but has not independently traced).

**Conclusion: 80% output reduction is not achievable by any mechanism that preserves High-effort
reasoning on tasks where reasoning dominates the ledger. It is achievable only on tasks where
output is mechanical — which is exactly the class where caller-side completion already wins.**

**F6 — Payload reduction has repeatedly been mistaken for saving, and the repository has already
caught itself doing this three times.** `OBSERVED`

- Memory selective fixture: **98.54% smaller payload** — but it assumes the correct literal query,
  and the naive fallback was **58% larger** than full-history replay, later corrected to 0.35%.
  No native saving was ever established for it (`MEMORY_PAYLOAD_RESULTS.md`).
- Command wrapper: **9.2 MB → ~2 KB** (a 4,600× byte ratio) — and the repository explicitly ruled
  that this cannot be used as a forecast of native savings (`engine/interface-feasibility/RESEARCH.md`),
  because the native next-call context was *far smaller* than the 1 MB command event.
- Index integrity: the fix that makes memory search safe raised application object reads from 514 to
  **109,678 bytes** and operations from 3 to 103 (`MEMORY_INDEX_INTEGRITY.md`).

Three separate places where a spectacular local ratio was correctly identified as *not* a native
saving. The discipline exists. The problem is that the local ratios keep being generated faster
than they are being converted.

**F7 — The most valuable external result I found is not a compression technique; it is a
*stability* technique, and it points at the opposite of what Helix's memory system does.**

Mastra's Observational Memory scores **94.87% on LongMemEval with gpt-5-mini** and 84.23% with
gpt-4o — beating the *oracle* configuration [2](https://mastra.ai/research/observational-memory).
Its stated mechanism: **a stable context window with no per-turn dynamic retrieval injection**, so
the prefix is reproducible and prompt-cacheable across turns. Helix's `workflow_memory` is a
*retrieval* system: the model searches, then expands. Every retrieval reshapes the next turn's
prefix and destroys cache locality. LongMemEval itself shows why curation can beat replay:
GPT-4o falls from 0.924 (oracle evidence) to 0.640 reading full history [5](https://arxiv.org/pdf/2410.10813).

**This is the one place where I think Helix's architecture is not merely un-optimized but pointed
in a direction that fights the billing model.** See §14.3 and §16.T8.

### 1.3 Direct answers to the terminal questions

**Is 80/80 achievable?**

- **On the workload class Helix has been benchmarking (Q4 / A / W50 / L40): no. Not for input, and
  not for output.** Input is bounded at 31–55% gross by the host prefix; output is bounded by the
  reasoning floor at 59% or worse on Luna-class tasks, and Astra's output *regressed*.
- **On the workload class that caller-side completion targets (evidence selection → deterministic
  assembly), 80/80 gross is plausibly reachable**, because the baseline there is inflated by
  model-generated glue. Sol's pair reached 67.3/71.9 with a 37-token non-reasoning residual.
- **In dollars, 80% is not the right target.** The correct target is a price-weighted cost
  reduction, and on that metric Helix V3 is already at 32–46%, with a defensible route to 55–65%
  that does not require 80% on either gross axis.

**Should Sol be frozen at 75/75 if the composed candidate misses?** See §13.6. Short answer: **no,
freeze the *mechanism* and the *boundary*, not the number** — and only after a second independent
replication on a fresh fixture, because n=1 with a fixed arm order is not a freeze-grade result.

---

## 2. RECONSTRUCTED HELIX STATE

### 2.1 What Helix actually is today

`OBSERVED` — assembled from `engine/CONTRACT.json`, `engine/README.md`, `skills/helixcontext/SKILL.md`,
`engine/prototype/CHECKPOINT.md`.

Helix is a **caller-owned deterministic middleware plus a small prose skill**. It is not an
interception layer, not an installed hook, and not a native session compressor. The runner
(`benchmarks/frozen-high/run_benchmark.py`) launches **a fresh `codex exec --ephemeral` per turn** and
reconstructs released context through an external caller. That is a *deliberate* design choice and
it is also the source of the host-prefix term in F4.

**Information path (control):** caller replays complete history each turn → model sees everything.
**Information path (candidate):** caller sends small resident state + current event; older events
live in `history.jsonl`; the model must retrieve before deciding.

**Subsystems:**

| Subsystem | Status | Measured? |
|---|---|---|
| Content-addressed evidence store (`evidence.py`) | Implemented, 185+ tests | Offline only |
| Typed reducers (generic / pytest / compiler) | Implemented | Offline; native mixed |
| Independent verifier (`verification.py`) | Implemented | Offline |
| Exact byte renderer (`renderer.py`) | Implemented | Native pilot: **regressed Sol/Astra** |
| Caller-side completion (`copy_handles.py`) | Implemented | **Native: Sol 67.3/71.9** |
| Workflow memory (`workflow_memory.py`) | Implemented (lexical, no embeddings) | Payload only; native **failed** |
| Named plans (`named_plans.py`, `plan_cli.py`) | Implemented | **Offline overhead positive; native rejected Luna** |
| Line index (`line_index.py`) | Implemented, opt-in | Offline; loses at ≤5 lookups |
| Interception (`post_tool.py`, hooks) | Prototype, **not installed** | Two native attempts **failed** |
| Live HUD (`engine/hud/`) | Implemented, read-only, zero inference | n/a |
| Post-compaction skill restoration | One bounded Sol probe | Not certified |

### 2.2 The measurement corpus

`OBSERVED` — `results/cost-audit.json`, `results/frontier-native-usage.json` (897 receipts).

| Ledger | Value |
|---|---:|
| Native calls with usage | 897 |
| Input tokens | 20,728,819 |
| — of which cached | 14,609,152 (**70.48%**) |
| Output tokens | 158,659 |
| — of which reported reasoning | 71,073 (**44.80%**) |
| Local evidence file bytes | 13,405,742 |
| Failed attempts without usage | 3 |
| Parent / coordinator tokens | **UNKNOWN, explicitly excluded** |

The repository is honest that this is a lower bound. It is also honest that it contains **all**
candidates including regressions, not just the selected policy — which is why the receipt file
(`frontier-native-usage.json`) shows a Luna W "on" arm totalling **2,144,268 input tokens** while
the published V3 figure for that cell is 710,887. Both are true: the published number is the
selected V3 policy; the receipt file retains the rejected V1/V2 attempts that had redundant
caller-owned bookkeeping. **The published V3 numbers are selected from a superset.**
`OBSERVED`; the selection itself is disclosed, not hidden.

### 2.3 What is genuinely unknown

`UNKNOWN` — and I am not going to guess at these:

- Actual dollar rates for `gpt-5.6-luna`, `gpt-5.6-sol`, `gpt-6-astra`. No public rate card exists.
- The composition of the ~10,500–12,800 token/turn host prefix. Not attributable from traces.
- Whether `cached_input_tokens` counts intra-invocation prefix re-reads or only cross-invocation
  cache hits. **This matters**: on Q4 (single native invocation) cached is 83% of input, which is
  only possible if intra-invocation re-reads count. That means "cached" is *partly reducible* by
  shortening the internal step chain — and my ceiling bound in F4 is therefore conservative in a
  way I cannot quantify.
- Physical I/O, disk allocation, remote compute, electricity.
- Whether Helix's arm ever silently changed task semantics (see §17).

---

## 3. FAILURE-HISTORY SYNTHESIS

Every negative result, with its cost. **The repository retained all of these — 3 failed attempts
without usage, all regressions published, no regrading.** That is the strongest methodological
asset Helix has.

| # | Experiment | Model(s) | Outcome | Evidence |
|---|---|---|---|---|
| N1 | Query V1 (ambiguous `total_count`) | all 3 | Fixture defect, not a saving | `frontier-interim.json` |
| N2 | Evaluator V1 grader mismatch | all 3 | All six outputs falsely graded fail; preserved, not regraded | `native-pilots/README.md` |
| N3 | Typed-terminal projection | Luna | **−6.9% in / −76.1% out** | `TRACE_DIAGNOSIS.md` |
| N4 | Literal-query V1 | Sol | −2.3% in | `TRACE_DIAGNOSIS.md` |
| N5 | Literal-query V2 | Luna | −3.5% in / −0.2% out | `NATIVE_RECEIPT_RECHECK.json` |
| N6 | Renderer (ID file + helper) | **Sol** | **−94.8% in / −13.5% out** | `render-pilot/README.md` |
| N7 | Renderer (ID file + helper) | **Astra** | **−89.2% in / −26.3% out** | `render-pilot/README.md` |
| N8 | Memory vs retained control | Luna | input −39.73%, **output +15.01%** | `MEMORY_NATIVE_FOLLOWUP.md` |
| N9 | Memory fresh control | Luna | Budget-stopped at 194,759 in; candidate never launched | `MEMORY_NATIVE_CONTROL_STOP.md` |
| N10 | **Cold named-plan API recipe** | **Luna** | **+62.41% in / +43.92% out** | `LUNA_COLD_PLAN_RESULT.json` |
| N11 | Named-plan offline overhead | n/a | +1.46 ms (256 B), +7.68 ms (1 MiB); **no finite break-even** | `NAMED_PLAN_OVERHEAD.md` |
| N12 | Named-plan metadata binding | n/a | ctime-only change rejected unchanged bytes | `NAMED_PLAN_OVERHEAD.md` |
| N13 | Native interception attempt 1 | Sol | Strict hash guard rejected both replacements | `interception/README.md` |
| N14 | Native interception attempt 2 | Sol | Packets emitted, model returned **null schema fields** | `interception/README.md` |
| N15 | Peer-event / ACK delivery | — | Failed: model shell could not write protected runtime dir | `engine/README.md` |
| N16 | Line index | n/a | **−202% byte saving at 1 lookup**; loses up to 5 | `engine/README.md` |
| N17 | V1/V2 long-horizon policy | **Luna** | W50 **2.39× input / 5.89× output**; failed ACK format | `FRONTIER_REPORT.md` |
| N18 | Alias recoding for selection | n/a | Saves 36 selection tokens, costs **649 input tokens** for a legend | `CALLER_COMPLETION.md` |
| N19 | Interim V3 Q4/A/W50/L40 | Astra | Output **−4.41%** | `FRONTIER_REPORT.md` |

### 3.1 The pattern, stated precisely

`INFERRED` from N3–N19.

Sorting every paired experiment by whether the candidate arm's **command count** fell relative to
control:

- **Commands fell, saving positive:** Sol query-V2 (3→1, +49.6%), Sol typed-terminal (3→1, +53.9%),
  Sol caller-completion (2→0, +67.3%), Astra typed-terminal (2→1, +31.8%).
- **Commands fell, saving negative:** Luna typed-terminal (3→2, −6.9%).
- **Commands equal, saving negative:** Luna query-V2 (1→1, −3.5%), Sol query-V1 (1→1, −2.3%).
- **Commands fell, catastrophic:** Luna cold plan (7→6, **+62.4%**).

The repository already stated this: *"fewer commands is a useful diagnostic signal, not a causal
proof or sufficient admission rule"* (`TRACE_DIAGNOSIS.md`). I confirm it and sharpen it:

> **The intervention boundary that predicts the sign of the outcome is not how much text Helix
> removes, and not how many commands it removes. It is whether the model is required to author,
> discover, or verify the machinery that does the removing.**

The three worst failures (N6, N7, N10) are precisely the three cases where the model was handed an
API and expected to integrate it. N10's own trace says it: *"Candidate read substantial engine
implementation, re-created integration code, transcribed result values, and repeated verification."*
And N6/N7 → caller-completion is the controlled reversal. This is exactly the failure chain in §1 of
the brief, and it is now `REPLICATED` across two models and two mechanisms.

### 3.2 The pattern nobody named: construction cost is not amortized in the benchmark

N10 and N11 both paid full construction cost inside a single measured episode. The repository's own
algebra (`engine/output/README.md`) says amortization requires
`N·(0.2·b[d] − h[d]) ≥ H0[d] − 0.2·B0[d]`, and its own measurement says **h[d] > b[d]** for plan
execution at both tested input sizes — meaning the left coefficient is negative and **no reuse count
succeeds**. Named plans are not merely unproven; under the measured offline rates they are
*provably* non-amortizing for the tested workload (`CONDITIONAL` on those rates being the warm
rates, which the repository correctly flags as unmeasured).

**Named plans should be stopped, not paused.** There is no measured path to a positive left-hand
coefficient, and the cold-plan native test (N10) is the empirical confirmation.

---

## 4. COST ANATOMY

### 4.1 The decomposition I will actually defend

The brief's proposed decomposition is serviceable but has one defect: it treats
`C_history`, `C_source/tool`, `C_procedural_generation` and `C_verification` as separate additive
terms. They are not identifiable from these traces, and treating them as additive is what produced
the "83.5% composed Sol" arithmetic the brief correctly warns against. I propose a decomposition on
the **identifiable** axes instead.

**Input side.** Per native invocation *t*:

```
I(t) = P_host(t)                 # host prefix: system prompt, tool schemas, skill catalog,
                                 #   environment block. Re-sent every turn. ~10.5–12.8k tokens.
     + M(t)                      # caller-supplied prompt (OBSERVED: resident_prompt_proxy_tokens)
     + W(t)                      # work generated inside the turn: tool calls, tool output,
                                 #   retrieved evidence, intermediate steps
     + R_hist(t)                 # replayed history (in control arms, folded into M)
```

`P_host` and `M` are directly bounded by the receipts. `W` is a residual. `R_hist` is
caller-controlled and is the only term Helix compresses *directly*.

**Output side:**

```
O(t) = REASON(t)                 # reported reasoning_output_tokens (a measured subset)
     + MECH(t)                   # mechanical generation: glue, bookkeeping, copied bytes,
                                 #   verification narration, tool arguments
```

`REASON` is measured. `MECH` is the residual, and **MECH is the only term Helix can legitimately
attack without touching reasoning quality.**

### 4.2 Measured anatomy — long horizon

`OBSERVED` from `results/frontier-v3.json` + per-turn `resident_prompt_proxy_tokens` in
`results/frontier-native-usage.json`.

| Model | Task | Arm | In/turn | Cached/turn | Uncached/turn | Caller prompt/turn | In-turn work/turn | Out/turn |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Luna | W50 | off | 17,906 | 11,499 | 6,407 | 3,390 | 3,016 | 135 |
| Luna | W50 | on | 14,217 | 10,664 | 3,552 | **395** | 3,157 | 66 |
| Luna | L40 | off | 20,782 | 10,564 | 10,217 | 6,099 | 4,118 | 92 |
| Luna | L40 | on | 15,006 | 11,082 | 3,923 | **473** | 3,450 | 71 |
| Sol | W50 | off | 18,520 | 12,751 | 5,769 | 3,390 | 2,378 | 18 |
| Sol | W50 | on | 15,705 | 10,718 | 4,986 | **394** | 4,592 | 24 |
| Astra | L40 | off | 21,909 | 11,376 | 10,532 | 6,099 | 4,433 | 15 |
| Astra | L40 | on | 16,592 | 11,154 | 5,437 | **473** | 4,964 | 15 |

**Read the Luna L40 row.** Helix cut the caller-supplied prompt by **92.2%** (6,099 → 473) and gross
input per turn fell **27.8%**. The arithmetic: it saved 5,626 tokens of prompt and paid back 668
tokens of in-turn work (4,118 → 3,450 net of the prompt change; the raw in-turn work actually rose
for Sol and Astra).

**This is the quantitative answer to "why do local savings disappear."** On the long-horizon
workloads, the term Helix controls is 29% of the bill at baseline and 3% after the intervention.
The other 97% is host prefix plus work the model performs inside the turn — and the in-turn work
*grew* for two of three models.

### 4.3 The five irreducible terms

| Term | Magnitude | Removable by Helix? | Relocatable? | Amortizable? | Model-specific? |
|---|---|---|---|---|---|
| `P_host` host prefix | 10.5–12.8k tok/turn | **No** (in this harness) | No | Only via **fewer turns** | No — identical across models (18,520 / 17,906 / 18,665 on W50) |
| Reported reasoning | 44.8% of output | **No by contract** | No | No | **Yes, violently**: Luna 10,038 / Sol 1,219 / Astra 374 across V3 |
| Platform cache behaviour | 70.5% of input is cached | No | n/a | n/a | Mildly (Astra 61.5% vs Luna 59.6%) |
| Skill/tool catalog | bounded at 512 tok by runner | Partly (fewer tools) | No | Yes | No |
| Semantic decision content | the actual answer | **Must not** | No | No | Yes |

The model-specificity of reasoning volume is the most under-exploited fact in the corpus:
**Luna emits 8.2× more reasoning tokens than Sol and 26.8× more than Astra on the same V3 task
battery** (10,038 / 1,219 / 374), yet Astra's total output is *lowest* and Astra's output *regressed*
under Helix while Luna's improved 32.9%. Whatever Helix does to output, it is doing it to a
different substrate in each model.

---

## 5. WHY LOCAL SAVINGS DISAPPEAR — THE CAUSAL DECOMPOSITION

### 5.1 Six named mechanisms, each with a receipt

**M1 · Integration tax (the dominant term).** `REPLICATED`
The model must read, instantiate, and verify the machinery that saves it tokens. N6/N7 vs
caller-completion gives the magnitude for Sol: **−94.8% → +67.3% on the identical mechanism**, a
swing of 162 gross percentage points attributable to placement alone. For Luna, N10 shows the tax
exceeds 62% of baseline input. The tax is paid in `W(t)`, not in `M(t)`.

**M2 · Reconstruction of removed structure.** `OBSERVED`
N8: Helix supplied partial evidence; the candidate *"expanded more terminal content despite
generating fewer command bytes"* — 578 → 7,471 terminal output bytes while command bytes fell
1,019 → 698. Removing context caused the model to go get more context, at a worse token-per-fact
ratio. When evidence is removed without a *binding* that the model trusts, the model rebuilds it.

**M3 · Verification doubling.** `OBSERVED`
The renderer's own verdict: *"the packet does not eliminate ordinary source checking"*
(`LUNA_REGRESSION_ANALYSIS.json`). N10's candidate *"recomputed complete-source aggregates"* after
receiving a plan that had already computed them. Helix's evidence is advisory; the model is still
accountable, so it re-derives. **This is the term that "proof-carrying" mechanisms must attack
(§15.1) — not by asserting correctness, but by making re-derivation unnecessary.**

**M4 · Narrated-but-absent work.** `OBSERVED`, twice
N10's candidate narrated an external registration-helper failure absent from the recorded tool
sequence. N8's candidate narrated unavailable memory/registration helpers with no corresponding
call. Both traces contain the same skill-budget warning. The repository correctly refuses to treat
these as verified runtime failures **and correctly still counts the tokens they cost.** The model
spends generation on machinery it only believes exists. `HYPOTHESIS`: this is what happens when an
API is described but not *bound* — the description is enough to trigger integration behaviour and
not enough to complete it.

**M5 · Bookkeeping that the caller should own.** `OBSERVED` (fixed in V3)
V1/V2: Luna W50 at **2.39× input and 5.89× output** of control, driven by *"repeated memory lookup
attempts, archive reads and ledger changes."* V3 removed duplicate caller-owned bookkeeping and
Luna W50 went from +139% to −51.2% output. **This is the single largest measured improvement in the
project's history and it came from deleting Helix code, not adding it.**

**M6 · Cache-locality destruction.** `HYPOTHESIS` — not directly measured, but see F7
Per-turn retrieval injection reshapes the prefix every turn, so the host cannot cache it. Helix's
memory design (`search` → `retrieve` → expand) is exactly this pattern. `CONDITIONAL` on the runner
counting intra-invocation re-reads as cached, which I cannot verify.

### 5.2 Which is dominant?

`INFERRED`, with the confidence grading stated:

| Mechanism | Evidence strength | Estimated magnitude where active |
|---|---|---|
| M1 Integration tax | **REPLICATED** (2 mechanisms × 2 models, sign-flipped) | 60–160 gross pct points |
| M5 Caller bookkeeping | **OBSERVED** (V1/V2 → V3, same task) | ~190 output pct points on Luna W50 |
| M2 Reconstruction | **OBSERVED** (N8, byte counters) | +15% output; input still improved |
| M3 Verification doubling | **OBSERVED** (trace review, 2 episodes) | Unknown magnitude; `UNKNOWN` |
| M4 Narrated work | **OBSERVED** (2 episodes) | Small in tokens, carcinogenic in design |
| M6 Cache locality | **HYPOTHESIS** | `UNKNOWN` |

**M1 is dominant, and M1 is a placement problem, not a compression problem.** The brief's hypothesis
is validated. But note the corollary the brief does not draw: **M1 is also the cheapest to fix**,
because it is fixed by *removing* the model's access to the machinery, not by making the machinery
better. Every improvement to Helix's API surface that makes it more capable has so far made M1
worse (N10 is the proof: a strictly more capable `execute-spec` CLI produced +62% input).

---

## 6. EXTERNAL RESEARCH FINDINGS

### 6.A Agent memory / state externalization

**MemGPT / Letta** [6](https://aiwiki.ai/wiki/letta) — OS-inspired tiers (core / recall / archival),
agent self-edits memory blocks via tool calls. The recurring critique across every survey I read is
the one that matters for Helix: *"every memory operation costs inference tokens, since the agent has
to reason about what to store and how"* [7](https://vectorize.io/articles/letta-vs-langchain-memory);
*"more tokens per turn and slower loops, because the agent spends some of its reasoning budget on
memory housekeeping"* [8](https://sureprompts.com/blog/letta-memgpt-walkthrough). This is M5 in the
literature. **Letta's failure mode is Helix's V1/V2 failure mode, and Helix already diagnosed and
fixed it. Helix is ahead of Letta here.**

**Observational Memory (Mastra)** [2](https://mastra.ai/research/observational-memory) — the most
important external result. 94.87% LongMemEval (gpt-5-mini), 84.23% (gpt-4o) vs oracle 82.4%.
Mechanism: background observer replaces consumed messages with a dated, prioritised **event-based
decision log**; 3–6× compression on conversational text, **5–40× on tool-call-heavy agent
workloads**; and — the part Helix needs — **a stable context window with no per-turn dynamic
retrieval injection, so the prefix is prompt-cacheable across turns.** Distinction from compaction
is explicit: compaction is "bulk unstructured message summarization"; OM is "compact event logging."

**LongMemEval** [5](https://arxiv.org/pdf/2410.10813) — long-context LLMs lose 30–60 accuracy points
reading full history vs oracle evidence (GPT-4o 0.924 → 0.640). **Full-history replay is not the
capability-preserving option; it is often the capability-destroying one.** This materially weakens
the objection that compressing history loses latent relevance.

**MemoryAgentBench** [9](https://arxiv.org/pdf/2507.05257) — finds RAG-style and commercial memory
agents *underperform* long-context models on holistic ("learning across the input") competencies,
and degrade as context grows. Direct counterweight to the OM result and to Helix's memory design:
**partial retrieval is not free of capability cost, even when it is free of token cost.**

### 6.B Command / tool output reduction

**RTK (Rust Token Killer)** [10](https://landscape.jimmysong.io/projects/rtk/)[11](https://zengineer.blog/blog/tech/rtk-token-killer-deep-dive/)
— single Rust binary, transparent PreToolUse hook rewriting, 100+ commands, <10 ms overhead,
**60–90% claimed reduction**, headline "118,000 → 23,900 tokens per 30-minute session."
Critically: *these are vendor blog figures using bytes/4 token estimates*, not tokenizer
measurement and not whole-task billing evidence. Helix's own review reaches the identical
conclusion (`memory-and-reducers-roadmap.md`). The genuinely transferable design elements are:
(a) **small-output bypass** — don't reduce what is already small; (b) **tee-to-raw on failure**;
(c) `rtk discover` — measuring *missed* opportunities rather than asserting captured ones.

**Anthropic, code execution with MCP** [12](https://www.anthropic.com/engineering/code-execution-with-mcp)
— the 150,000 → 2,000 token (98.7%) headline. But the same vendor's *other* two releases tell the
honest story [13](https://particula.tech/blog/code-execution-with-mcp-token-reduction-pattern):
Tool Search Tool cut tool definitions ~77K → ~8.7K (**85%**), while **Programmatic Tool Calling cut
average usage only 43,588 → 27,297 (37%) on complex research.** The 98.7% is a single contrived
Drive→Salesforce workflow. **This is the external analogue of Helix's wrapper: a spectacular local
ratio on a workload chosen to flatter it, and a 37% number on a realistic one.** Anthropic's own
portfolio is the best available evidence that headline ratios do not transfer.

**CodeAct** [14](https://arxiv.org/abs/2402.01030) — executable Python as unified action space;
~30% fewer steps, up to 20% higher success. Microsoft's Hyperlight port reports 52.4% latency and
**63.9% token reduction** on a representative workload [15](https://devblogs.microsoft.com/agent-framework/codeact-with-hyperlight/).
Useful, but note the shape of the win: it comes from **collapsing N model turns into 1**, which is
precisely the lever on `P_host` identified in F4.

### 6.C Computation placement / action compilation

**Options / macro-actions (HRL)** [16](https://www.imsuperintelligence.ai/post/problem-of-temporal-abstraction-options-frameworks-in-reinforcement-learning/)
— an option = (initiation set, intra-option policy, termination condition). The transferable
content is the **initiation set**: a macro-action is only reusable where it is *known applicable*,
and the framework makes applicability an explicit, checkable precondition rather than an inference.
Helix's named plans got the immutability half right and the **initiation-set half wrong** — there is
no applicability predicate, only a dependency hash, which is why N10's model had to read the engine
to decide whether to use it.

**Voyager skill library** [17](https://arxiv.org/abs/2305.16291) — *"without its skill library lost
15.3× in tech-tree milestone speed"* [18](https://arxiv.org/html/2603.07670v1). Procedural memory is
the highest-leverage memory tier by a wide margin, and the skill is stored as **verified runnable
code indexed by natural-language description, composed on the fly.** This is the closest external
analogue to what Helix's "verified macro-action" should be — and note the ordering: *verify first,
then admit to the library.* Helix's `checked_steps` already supplies the verify half.

**Partial evaluation / Futamura** [19](https://grokipedia.com/page/futamura) — specialize an
interpreter against a known-static input. The transferable principle is **binding-time analysis**:
classify every piece of information as *static now* or *dynamic later*, specialize against the
static, and ship only the residual. Helix has never performed an explicit binding-time analysis on a
workflow. `plan_dependencies.py` is an implicit, incomplete one (declared files + executable hashes,
but explicitly *not* transitive closure or libraries).

**Self-adjusting computation / dynamic dependence graphs** [20](https://www.cs.cmu.edu/~guyb/papers/ABBHT09.pdf)
— the empirical caution is the valuable part: *"asymptotic speedups are rare: for many computations
and modifications, change propagation is no faster than recomputing from scratch."* Adar et al. got
speedups only by combining DDGs *with memoization*. **Directly predicts N11's result** (plan
validation no cheaper than re-execution) and warns against expecting incremental-evidence schemes to
pay off without a memo layer.

### 6.D Prefix / KV reuse — and the distinction the brief demanded

| Kind | What is saved | Billable? | Latency? | Actual model work? |
|---|---|---|---|---|
| Provider prompt caching (OpenAI, Anthropic) | KV recompute + **~90% of input price** | **Yes**, at ~0.1× | Yes, large | **No** — same FLOPs, skipped prefill |
| vLLM / SGLang automatic prefix cache | GPU prefill | n/a (self-hosted) | Yes | **No** |
| Semantic / response cache | **The entire call** | Yes, fully | Yes, huge | **Yes** — this is the only kind that removes model work |
| KV cache (autoregressive) | Per-token recompute | No | Yes | No |

[1](https://openai.com/index/introducing-gpt-5-2/)[3](https://crazyrouter.com/en/blog/gpt-5-pricing)[4](https://www.flexera.com/blog/ai/prompt-caching-breakdown/)[21](https://myengineeringpath.dev/genai-engineer/llm-caching/)

**The consequence for Helix, stated bluntly: prefix caching already gives back 90% of the price of
the single largest input term (`P_host` and history replay). Helix has been attacking the cheapest
tokens in the ledger. The expensive tokens are first-read evidence and output — and those are the
ones caller-side completion actually attacks. That is why it is the only mechanism that produced a
large win.**

### 6.E Semantic caching / reasoning reuse

**StepCache** [22](https://arxiv.org/html/2603.28795) — step-granular reuse: retrieve a prior
request, preserve step order, **verify per-step**, patch only the first failing step and its
downstream dependents, and **skip-reuse** (fall back to full regeneration) when inconsistency
signals predict reuse won't pay. This is the right shape for Helix: it is reuse *with* verification
and *with* an escape hatch, not reuse by similarity.

**FreshCache** [23](https://arxiv.org/html/2607.04281) — reuse as **risk-constrained temporal
inference**: estimate staleness probability and approve reuse only within a per-tier error budget.
Ablations: the temporal risk gate cuts stale error 14.9% → 3.3%. This is the formal version of
Helix's own invariant *"a search miss is not proof a fact never occurred."*

**The safety literature's verdict on semantic caching** [24](https://pyimagesearch.com/2026/05/04/semantic-caching-for-llms-ttls-confidence-and-cache-safety/)
is unambiguous that similarity thresholding alone is unsafe — staleness, poisoning, and error-caching
are first-class failure modes, and TTL is a *correctness* mechanism, not an optimization.

**Answer to the brief's question** ("can repeated reasoning be safely replaced by previously
verified semantic artifacts without freezing behaviour incorrectly?"): **yes, but only for
artifacts with (a) an explicit applicability predicate, (b) a soundness-carrying receipt, and (c) a
deterministic invalidation trigger.** Helix's `named_plans` has (a)-ish and no (c); `frozen_search`
has (a) and (c) and no (b). No mechanism in Helix has all three.

### 6.F Database / compiler / OS analogies — the transferable ones

| Source domain | Mechanism | Genuine transfer to Helix | Not a superficial analogy because… |
|---|---|---|---|
| Query optimizers | **Prepared statements / plan cache** | `plan_cli execute-spec` | Requires an applicability predicate (parameter binding), not just a hash — Helix lacks this |
| Query optimizers | **Cost-based vs rule-based** | Admission policy | Helix has break-even arithmetic (`plan_costs.py`) but no cost model feeding admission |
| JIT | **Tiered compilation + OSR** | Hot-path detection | Helix has no notion of "hot" workflows at all |
| Partial evaluation | **Binding-time analysis** | Deciding what is static per task | Directly produces an applicability predicate |
| Build systems (Bazel/Nix) | **Content-addressed, hermetic actions** | Already implemented (`evidence.py`, `checked_steps`) | — already transferred |
| Build systems | **Remote cache + cache eviction policy** | Absent | Helix has storage but no admission/eviction policy |
| Incremental computation | **DDG + memoization** | Absent; predicts N11 | Empirically warns speedups are rare without memoization |
| OS | **Demand paging with LRU** | Absent | Helix's memory has no eviction |
| Proof-carrying code | **Heavyweight prover / lightweight checker** | **Absent — highest-value gap** | Replaces the consumer's re-derivation (M3) with a cheap check |
| Event sourcing | **Append-only log + projections** | Implemented (`workflow_memory`) | — already transferred |
| Capability systems | **Unforgeable references** | `copy_handles` catalog refs | — already transferred |

**The two rows that matter most are "binding-time analysis" and "proof-carrying code." Neither is
implemented in Helix, and between them they address M1 and M3, the two largest loss terms.**

---

## 7. TRANSFERABLE MECHANISMS

Ranked by expected leverage × orthogonality ÷ (implementation + benchmark cost). Full ranking in
§15; here I give the mechanism content.

### 7.1 Stable-prefix resident state (from Observational Memory) — *highest leverage*

Replace per-turn retrieval injection with a **monotonically-appended, never-rewritten observation
log** that is rendered identically every turn. Retrieval, when needed, appends to the log rather
than being injected into a per-turn slot.

- **Removes:** `R_hist` replay, per-turn prompt variance, cache misses caused by prefix reshaping.
- **Adds:** observer write cost (deterministic, no inference — Helix can do this today), log growth.
- **Could the model reconstruct it anyway?** Yes, by reading `history.jsonl` — which is precisely
  what the L40 traces show it doing (in-turn work 3,450–4,964 tokens/turn). **So the log must be
  sufficient, or the model will go get the rest.** This is why OM's accuracy beats oracle: the log
  is *sufficient*, not merely *small*.
- **Falsify cheaply:** offline — hold out a turn-1 fact needed at turn 40; measure whether the
  model still reads `history.jsonl`. Then native: W50 with log-on vs current state-on.

### 7.2 Applicability-predicate macro-actions (from options + prepared statements + partial evaluation)

A Helix macro-action is `(id, version, hash) + binding-time map + applicability predicate + verified
step list`. The predicate is **evaluated by the engine**, not inferred by the model. The model sees
`APPLICABLE` or `NOT_APPLICABLE: <reason>` — never the implementation.

- **Removes:** M1 entirely for the covered workflow. This is the mechanism whose absence caused N10.
- **Adds:** predicate evaluation (deterministic, microseconds).
- **Why N10 failed and this might not:** N10 handed Luna a *recipe* and asked it to decide
  applicability. This hands it a *verdict*.

### 7.3 Proof-carrying tool results (from PCC)

Every engine-produced packet carries a **checker-verifiable receipt**: which source hashes it read,
which invariants were verified, what was omitted and where the omitted bytes live. The model is told
"re-derivation is unnecessary because the receipt is checkable," and — critically — Helix must then
**accept the model's reliance** rather than praising re-derivation in the skill text.

- **Removes:** M3 verification doubling.
- **Adds:** receipt bytes (small — `copy_handles` receipts are ~4.7 KB for 36 handles).
- **Risk:** if the receipt is not independently checkable, this is just an assertion, and models
  that audit (Astra) will ignore it. **Astra is the test case.**
- **Falsify:** A/B the same evidence packet with and without a receipt that states the verified
  invariant set; measure whether the model still recomputes. Single model (Astra), 2 calls.

### 7.4 Turn amortization (from CodeAct)

Collapse N turns into 1 invocation. This is the **only** lever on `P_host`.

- **Removes:** `(N−1) × P_host ≈ (N−1) × 11k` tokens.
- **Adds:** longer single contexts (quadratic attention inside the turn), loss of per-turn
  checkpointing.
- **Ceiling arithmetic:** on W50, if 50 turns became 5, gross input would fall ~90% — *but the W50
  benchmark requires 50 sequential turns by construction.* **The lever applies to real workflows,
  not to this benchmark. This is a benchmark-blinder, and it should be named as one.**

### 7.5 Cache-aware cost accounting (from ClawTrace/CostCraft)

ClawTrace reports cache reads at their real rate and finds that counting them at the fresh rate
**overstates true cost by 1.6–2.0×** [25](https://arxiv.org/html/2604.23853v2). Adopt this as the
primary metric. Helix already has the data; it does not have the metric.

### 7.6 Skill/body progressive hydration (from SkillZip / SkillReducer)

SkillZip: 72.1% delivered-context reduction vs top-55 whole-skill loading, 47.0% total prompt
reduction end-to-end [26](https://arxiv.org/html/2608.05604). SkillReducer: 48% description /
39% body compression, **26.8% end-to-end** [27](https://arxiv.org/html/2603.29919v2). Directly
applicable to the Helix skill body, and — importantly — **SkillReducer reports that aggressive
compression did *not* degrade pass rate** (retention 0.910–0.956 across compression bands), which is
reassuring for compressing `SKILL.md`.

---

## 8. CLAUDE-MEM ANALOGUE AUDIT

Claude-Mem: five lifecycle hooks (SessionStart / UserPromptSubmit / PostToolUse / Stop / SessionEnd),
AI-compressed observations into SQLite + vector search, three-tier progressive disclosure (compact
index → timeline → full details), auto-injection at session start [28](https://www.datacamp.com/tutorial/claude-mem-guide)[29](https://dev.to/shimo4228/embedding-memory-into-claude-code-from-session-loss-to-persistent-context-54d8).

| Capability | Claude-Mem analogue | Helix current status | Evidence | Missing piece | Expected leverage | Risk |
|---|---|---|---|---|---|---|
| Persistent project memory | SQLite observations, cross-session | **Partial** — `workflow_memory` persists to SQLite, project-scoped | `WORKFLOW_MEMORY.md` | Session/session continuity is labelled, not enforced | Low–Med | Duplicated storage (305,620 logical bytes vs 100,588-byte history) |
| Indexing | FTS5 + Chroma vectors | **Partial** — FTS5 only, deliberately no embeddings | `workflow_memory.py` | Semantic/hyponym recall | Med | Adding embeddings adds cost before measured benefit — Helix's own rule says wait |
| **Exact provenance** | Observation refs only | **Superior** — SHA-256 object + byte range + source hash | `evidence.py`, `renderer.py` | — | High (already owned) | Retrieval amplification (514 → 109,678 bytes after integrity fix) |
| Restart recovery | SessionStart auto-injection | **Absent as a product**; one bounded Sol compaction probe | `engine/README.md` | Certified restoration across arbitrary skills | **High** | Probe was one episode |
| Semantic retrieval | Vector search | **Deliberately absent** | `workflow_memory.py` docstring | — | Low (correctly deferred) | Lexical miss ⇒ wrong conclusions |
| Summaries | AI-compressed observations | **Deliberately absent** — "no generated summaries or inference calls" | `WORKFLOW_MEMORY.md` | — | Low | Runtime cost of compression (Claude-Mem pays per observation) |
| **Procedural memory** | Not present | **Superior** — `named_plans` + `checked_steps` + `copy_handles` | `NAMED_PLANS_STATUS.md` | **Applicability predicate** | **Highest** | N10 — integration tax ate the benefit |
| Compaction restoration | SessionStart re-injection | **Absent** — compaction capsule is a *design*, not code | `memory-and-reducers-roadmap.md` | Implementation + certification | **High** | Unmeasured |
| Cost of memory creation | Haiku, ~400 in/150 out per observation (~16.5k/session) | **Zero inference** — Helix indexes deterministically | `WORKFLOW_MEMORY.md` | — | **Helix wins outright** | Index storage ~2× source |
| Cost of retrieval | MCP search call (model-driven) | Caller-side, no inference | `workflow_memory.py` | — | **Helix wins** | Read amplification |

**Verdict: do not clone Claude-Mem.** Helix is *ahead* of Claude-Mem on the three things that
matter for this objective — zero-inference indexing, exact byte provenance, and procedural memory —
and *behind* on the two that matter least for cost but most for continuity (restart recovery,
compaction restoration).

**The one mechanism worth taking is not Claude-Mem's; it is Observational Memory's stable-prefix
log.** Claude-Mem's auto-injection is per-session and restructures the prefix at every session
start; OM's log is stable and cacheable. For a token-cost objective, **OM's design strictly
dominates Claude-Mem's.**

---

## 9. RTK ANALOGUE AUDIT

| Capability | RTK analogue | Helix current status | Evidence | Missing piece | Expected leverage | Risk |
|---|---|---|---|---|---|---|
| Typed command reducers | 100+ command filters (git, cargo, npm, ls, grep) | **Partial** — generic + pytest + compiler reducers only | `engine/README.md` | **Command coverage is the whole product** | High **if** native interception works | Reducer must not discard decisive evidence |
| Command rewriting (transparent hook) | PreToolUse hook rewrites `git status` → `rtk git status` | **Prototype, not installed** — `post_tool.py` | `interception/README.md` | Native envelope compatibility | **Highest** (gate is closed) | Two native attempts **failed** |
| Safe bypass (small output) | Small outputs pass through | **Implemented** — output budget fallback | `interception/README.md` | — | Med | — |
| Raw output preservation | `tee` full output on failure | **Superior** — content-addressed SHA-256 archive of raw stdout/stderr, exit/signal, timing | `evidence.py` | — | High (already owned) | Storage duplication |
| Exit-status preservation | Preserved | **Superior** — exit + signal + timeout + env label, independently verified | `verification.py` | — | High | — |
| **Truncation awareness** | Not addressed | **Superior and measured** — native truncation framing matched on head/tail/line-count; 25,622 raw event bytes vs 4,101 hook-received bytes | `interception/README.md` | — | High | Narrow observed-format adapter |
| Exact retrieval | Not offered | **Superior** — `HELIX_FULL_OUTPUT=1` expansion, line ranges, batched | `line_index.py`, `evidence.py` | — | High | Full-object read amplification |
| **Broad command coverage** | 100+ commands, `rtk discover` to find gaps | **Absent** — 3 reducers | `engine/README.md` | A conservative adapter registry | High | Each adapter is a correctness surface |
| **Transparent interception before model context** | Yes, production | **NO — the binding constraint** | N13, N14 | Working hook delivery | **Blocking** | Two failures; hook delivery ≠ emission |

**Verdict: do not clone RTK.** Helix's evidence substrate is strictly better than RTK's on
provenance, exit-status fidelity, truncation awareness, and exact retrieval. RTK wins on exactly one
axis — **it is actually installed.**

**That axis is not a detail; it is the entire product.** RTK's claimed 60–90% is realized *only*
because it sits in the path. Helix has a better reducer behind a closed gate.

**But — and this is the important qualification — RTK's own numbers are vendor blog figures using
bytes/4.** The honest external estimate of what a command-output reducer is worth, once a native
runtime already truncates, comes from Anthropic's Programmatic Tool Calling: **37%**. And Helix's
own N3 shows the reducer can be *net negative* (Luna −6.9% in / −76.1% out).

**Therefore: the interception gate is worth opening, but it is not worth opening first, and it is
not the route to 80/80.** It is worth opening because without it Helix cannot touch `W(t)` at all.
Rank it behind §15.1–§15.3.

---

## 10. SOL PHENOTYPE

`gpt-5.6-sol`. Evidence base: 6 query-V2 receipts, 2 render-pilot, 2 caller-completion, 4 V3 tasks.

### 10.1 Observable behaviour that drives Helix overhead

1. **Sol's wins track the control's command count, not Helix's mechanism.** query-V2 +49.6% with a
   3-command control; query-V1 −2.3% with a 1-command control. `OBSERVED` (`TRACE_DIAGNOSIS.md`).
2. **Sol pays an enormous integration tax when it must operate machinery** — render-pilot −94.8%
   (58,386 → 113,760). `OBSERVED`.
3. **Sol pays almost none when the caller owns the machinery** — caller-completion +67.3% with
   **zero tool commands**, 49-byte response. `OBSERVED`.
4. **Sol's reasoning volume is low and elastic**: V3 reasoning 1,219 tokens across 4 tasks
   (vs Luna 10,038); caller-completion reasoning fell 632 → 364 (−42.4%). `OBSERVED`.
5. **Sol's output does not improve on long-horizon tasks**: V3 W50 output −26.1%, L40 −6.9%.
   `OBSERVED`.
6. **Sol's uncached input is highly compressible** on evidence tasks: query-V2 −77.9%;
   caller-completion only −22.6% (because the control's input was 58% cached).
   `OBSERVED` + `INFERRED`.

`INFERRED` synthesis: **Sol is a low-reasoning, high-compliance, tool-loop-heavy executor.** Its
cost is concentrated in `W(t)` — the tool loop — not in `REASON(t)` and not in `P_host`. It does not
audit (unlike Astra) and it does not narrate repairs (unlike Luna). It does what it is told,
including reading an entire engine when told an API exists.

### 10.2 What is removable

| Term | Removable? | Basis |
|---|---|---|
| Tool-loop generation (`W`) | **Yes, near-totally** | caller-completion: 2 commands → 0, command bytes 2,068 → 0 |
| Model-side verification narration | **Yes** | absent from the winning trace entirely |
| Reported reasoning | Partly (−42.4% observed) | but see the freeze risk, §10.5 |
| Evidence volume (`M`) | Yes, on evidence-shaped tasks | query-V2 −77.9% uncached |
| `P_host` | **No** | 10.7–12.8k/turn on every Sol task |
| Long-horizon per-turn work | **No — it grew** | W50 in-turn work 2,378 → 4,592 |

### 10.3 Mechanisms ON / OFF

**ON:** caller-side completion (with pinned catalog) · request-conditioned evidence selection ·
deterministic byte assembly · engine-evaluated applicability verdicts · aggressive skill-body
compression · **native bypass when Helix's own overhead exceeds the target** (mandatory for
long-horizon: Sol's W50 output regressed 26%).

**OFF:** named plans / cold API recipes (**proven harmful on Luna, never tested on Sol — do not
transfer**) · any mechanism requiring Sol to read engine source · per-turn retrieval injection in
long-horizon · caller-owned bookkeeping that Sol must maintain · alias recoding (rejected for cause:
saves 36 selection tokens, costs 649 legend tokens).

### 10.4 Achievable ceiling

`CONDITIONAL` on replication beyond n=1:

- **Evidence-selection → assembly workload class (the Sol sweet spot): 65–80% input, 70–85% output.**
  Already at 67.3/71.9. Residual output is 90.8% reasoning, so the *output* ceiling is essentially
  "however much reasoning Sol needs." Reaching 80% output requires reasoning to fall below 285
  tokens against the 1,427 baseline. Observed in-pair: 364. **This is a 21% reasoning reduction
  away.**
- **Long-horizon class: 25–35% input only; output will regress.** Do not deploy.
- **Dollar basis across the V3 battery: 35.4%, with L40 alone at 52.6%.**

### 10.5 Smallest falsifier

> **Two calls. Same fresh fixture as `SOL_CALLER_COMPLETION_RESULT.json`, but with two additional
> records whose eligibility depends on a fact stated only in a record the model must retrieve, plus
> one deliberately stale catalog generation.**
> **Null:** caller-completion does not reproduce ≥60% input saving on a *second* independent
> fixture, or the stale catalog is silently used.
> **Cost:** ~60k input / ~2k output. **This must be run before any composition work**, because the
> entire 67.3/71.9 claim currently rests on a single pair with a fixed arm order and no correction
> turn.

### 10.6 The freeze risk nobody has priced

Caller-completion's winning trace has **zero tool calls**. That is a saving *and* a capability
change: the model did not verify the source itself. The receipt deliberately leaves
`semantic_success: null` (`OBSERVED`) — Helix is explicitly not claiming the selection was right,
only that the bytes match the selection. **On a task where the model must discover eligibility
rather than be handed metadata, zero-tool-call completion may fail silently.** §10.5 tests exactly
this.

---

## 11. ASTRA PHENOTYPE — `HELIX-ASTRA PHENOTYPE V0`

`gpt-6-astra`. This is the strategic target and, per F3, the most undervalued result in the corpus.

### 11.1 Observable behaviour

1. **Astra barely reasons in tokens**: 374 reasoning tokens across all four V3 tasks; 0 on W50-on
   and L40-on; query-V2 reports 0 in one arm. `OBSERVED`.
2. **Astra's output regressed under V3** (−4.41%) while its input improved (17.11%) — the only model
   where the two moved oppositely. `OBSERVED`.
3. **Astra's input saving is almost entirely on cached tokens**: 25.67% gross → **0.13%** uncached
   on query-V2 (5,365 → 5,358). `OBSERVED` + `INFERRED`.
4. **Astra's baseline is the cheapest of the three** ($1.1159 vs Luna $1.2450 on the V3 battery),
   and its per-task dollar saving on L40 is **43.4%** — competitive with Luna's 53.4% despite a
   gross-output regression. `CONDITIONAL`.
5. **Astra regressed hardest on the render pilot** (−89.2% input) and gained consistently on typed
   projections (+31.8% in, +33.8% out) and query projections (+25.7% in, +38.6% out). `OBSERVED`.
6. **Astra went 2 commands → 1 across every projection candidate** and its input saving stayed in a
   tight 26–32% band. `OBSERVED` (`TRACE_DIAGNOSIS.md`).

`INFERRED` synthesis: **Astra is a low-token, high-certainty, audit-prone executor.** It does not
spend tokens deliberating; it spends them *confirming*. Its 26–32% input band across three different
candidates is the most stable per-model signal in the corpus — it looks like Astra performs a fixed
amount of confirmation work regardless of what Helix supplies, and Helix's variance shows up in
whether that work grows or shrinks.

**Crucially: Astra regressed on output when Helix asked it to do something unfamiliar (renderer),
and regressed on output in long-horizon, and gained on output when Helix simply gave it better
evidence (+38.6%).**

### 11.2 HELIX-ASTRA PHENOTYPE V0

**Design principle: never ask Astra to trust; always let Astra check *cheaply*.**

| Element | Specification |
|---|---|
| **Input mechanisms** | (1) Request-conditioned typed projection — the one mechanism with a stable 26–32% band. (2) **Stable-prefix observation log**, not per-turn retrieval. (3) **Proof-carrying evidence packets** with independently checkable receipts. (4) Aggressive skill-body progressive hydration. |
| **Output mechanisms** | (1) Caller-owned deterministic assembly (like Sol) **but with the verification receipt inline**. (2) Caller-owned bookkeeping — never ask Astra to maintain a ledger. (3) **No** requirement to narrate verification: the receipt *is* the verification. |
| **Trusted Engine guarantees** | Byte-identity of every retrieved span (SHA-256 + range) · exit/signal fidelity · omission accounting (what was dropped and where it lives) · invariant-check results from an **independent** verifier that never calls the reducer · immutability of catalogs and plans under (id, version, hash). |
| **Receipts Astra needs** | source hash + byte range + generation · invariant set actually checked (explicit list) · omitted-region count and retrieval handles · verifier identity and its independence from the producer · **applicability verdict** for any macro-action · staleness/invalidation trigger. |
| **What Astra must still reason about** | Semantic selection · eligibility and precedence rules · whether the *invariant set in the receipt* is sufficient for this decision · supersession and authority · late relevance · what to do on a FAILED retrieval. |
| **What Astra must NEVER regenerate** | Byte-level copying · hash re-derivation · command boilerplate · the verification the Engine already performed and certified · history it has already been given in stable form · the dependency check for a plan the Engine has already validated. |
| **Bypass rules** | Bypass Helix whenever: (a) the task is single-turn and evidence-light (Q4: −1.7% in, −0.3% out — both arms within noise); (b) a retrieval returns FAILED (fall back to raw history, never to a partial packet); (c) the projected saving is < 15% *uncached* input; (d) the mechanism requires Astra to read Engine source. |
| **Likely failure modes** | Astra ignores an uncheckable receipt and re-derives (M3 returns, output regresses) · stable log omits a decisive fact and Astra does not notice (silent) · aggressive compression of the skill body removes a caution Astra was actually following · Astra's confirmation loop expands when receipts are unfamiliar, costing more than the evidence saved (this is my leading explanation for the −4.41% output regression). |
| **Smallest native falsifier** | §19. |

### 11.3 The recursive research multiplier — analysed explicitly

The brief asks whether cheap Helix-enabled Astra can research the remaining models more cheaply.
**Quantify before believing it.**

`OBSERVED` (`results/cost-audit.json`): the project has spent 20,728,819 input / 158,659 output
tokens across 897 native calls to date, excluding unmetered parent/coordinator usage.

`CONDITIONAL` (GPT-5.x rates): that corpus is **≈ $27.5** of task-run cost (input
$6.12M×1.25 + cached $14.61M×0.125 + output $158.7k×10 → $7.65 + $1.83 + $1.59 = **$11.07**; the
remainder of project spend is unmetered parent conversation, which is `UNKNOWN`).

*If* Helix-Astra reached 60% dollar reduction on research-shaped work, each future research
iteration costs 0.4×. The multiplier on a **fixed budget** is 2.5× more experiments. The multiplier
on a **fixed number of experiments** is 0.4× cost.

**But three things cap this:**

1. **The bottleneck in this project has not been token spend — it has been statistical power.** 897
   calls already exist and the strongest claim in the repository still rests on **n=1 pairs with
   fixed arm order**. A 2.5× increase in the number of underpowered experiments does not fix that;
   it makes the multiple-comparisons problem worse. **Cheap experiments raise the false-discovery
   rate before they raise the true-discovery rate.**
2. **The unmetered parent conversation is excluded from every saving claim.** If parent/coordinator
   usage is large relative to task usage — and on a project of this shape it plausibly is — then a
   60% reduction on task runs may be a small fraction of true spend. `UNKNOWN`, and it should be
   measured before the multiplier is invoked.
3. **Astra is the model whose output regressed.** Using it to run research is fine; using it to
   *adjudicate* research on other models is not, until the regression is explained.

**Verdict: the recursive multiplier is real but second-order, and it is a multiplier on a quantity
that is not currently the binding constraint.** Spend the first 48 hours raising power per
experiment, not lowering cost per experiment. **Do not use the multiplier as a justification for
launching matrices.**

---

## 12. LUNA PHENOTYPE

`gpt-5.6-luna`. The cautionary phenotype.

### 12.1 Observable behaviour

1. **Luna reasons enormously**: 10,038 reasoning tokens on the V3 battery — **8.2× Sol, 26.8×
   Astra** — and 44–48% of its output is reasoning. `OBSERVED`.
2. **Luna is the only model with a positive output saving on V3** (+32.93%). `OBSERVED`.
3. **Luna is the only model where Helix has produced catastrophic regressions**: V1/V2 W50
   **2.39× input / 5.89× output**; cold plan **+62.41% in / +43.92% out**; typed terminal −76.1%
   output; memory +15.01% output. `OBSERVED` ×4.
4. **Luna narrates repairs.** Its renderer-off trace shows two failed hash checks inside commands
   whose aggregate exit was zero, and an explanation attributing an assertion failure to newlines —
   which the trace contradicts. `OBSERVED` (`behavior-study/THEOREMS.md`).
5. **Luna's regressions are the ones Helix fixed by deletion, not addition**: V3 removed duplicate
   caller-owned bookkeeping and Luna W50 went from +139% input to −20.6%. `REPLICATED`.
6. **Luna's V3 Q4 output did not improve** (−0.5%) while its input improved 31.6%. `OBSERVED`.

`INFERRED` synthesis: **Luna is a high-reasoning, self-repairing, verification-looping model.** It
spends its budget on deliberation and repair. Helix's mechanisms that add surface area
(APIs, plans, ledgers, helper discovery) feed Luna's repair loop and are catastrophic. Helix's
mechanisms that *remove* requirements (V3's caller ownership) are strongly positive.

### 12.2 Removable / ON / OFF

**Removable:** caller-owned bookkeeping (**proven, largest single win in the project**) · duplicated
history replay · redundant verification loops when a checkable receipt exists.
**Not removable:** reasoning volume (44–48% of output; the repository's own OUTPUT_FRONTIER puts the
conditional max saving at 59.37% for the memory control and 48.64% for the candidate).

**ON:** caller-owned bookkeeping removal · caller-side completion for exact-copy subtasks ·
stable-prefix observation log · aggressive task-level bypass.
**OFF — hard:** named plans (**proven +62%**) · cold API recipes · any Engine-source inspection ·
per-turn retrieval injection · any mechanism that adds a ledger Luna must maintain.

### 12.3 Ceiling

`CONDITIONAL`: **35–50% input, 25–40% output on long-horizon** (already achieved 25.3/32.9 gross;
45.8% dollar). **Never 80/80**: the reasoning floor alone caps output at ~59% and the observed
output saving is 32.9%. **Luna cannot reach 80% output without suppressing reasoning, which the
project has correctly ruled out.**

### 12.4 Smallest falsifier

> **Two calls, cold-plan mechanism, but with the applicability predicate pre-evaluated by the engine
> so Luna never reads Engine source.** Null: input saving still negative. This tests whether N10's
> failure was "plans are bad for Luna" or "**making Luna decide applicability is bad for Luna**" —
> two very different conclusions, and the second one is salvageable.

### 12.5 Strategic note

The brief's premise — "if Sol becomes ~75% cheaper, optimizing Luna may cease to matter" — deserves
a direct challenge. **Luna is not a cost problem; it is a variance problem.** Luna's spread runs
from +42.6% (task A input) to −94.7% (query-V2 uncached input) to +139% (V1/V2 W50). A model with
that variance is not one you stop optimizing; it is one where **you must build a bypass gate**,
because the expected value of applying Helix to Luna is positive but the tail is terrible. **The
deliverable for Luna is a router, not a compressor.**

---

## 13. SOL COMPOSITION ANALYSIS

### 13.1 The arithmetic the brief asked me to reject — rejected

Naive residual-independence gives 83.5% input / 86.0% output. **This is invalid and the repository
already contains the theorem that kills it** (`behavior-study/THEOREMS.md`, Proposition 1):

> `G = Σ_{e ∈ ∪S_i} w(e) − H`. Summing individual removals instead overcounts intersections.

The proof's own counterexample: two mechanisms each removing the same 60-token event from a
100-token baseline save 60, not 120.

### 13.2 Why the overlap is near-total, from the traces

| | Mechanism A (request-conditioned evidence) | Mechanism B (caller-side completion) |
|---|---|---|
| Attacks | `M(t)`: the evidence block in the prompt | `W(t)`: the tool loop that produces/verifies the answer |
| Sol query-V2 | 3 commands → 1 | — |
| Sol caller-completion | — | **2 commands → 0**, command bytes 2,068 → 0 |

**B already removed the entire tool channel that A compresses the output of.** In B's winning trace
there are **zero tool calls and zero recorded terminal bytes**. There is no tool output left for A
to reduce. `OBSERVED`.

Three overlap regimes, bounded:

| Regime | Assumption | Input | Output |
|---|---|---:|---:|
| Additive (invalid) | disjoint, no overhead | 116.9% | 121.9% |
| **Naive residual-independence** | independent residuals | **83.5%** | **86.0%** |
| **Perfect subsumption** | B's removed set ⊇ A's | **67.3%** | **71.9%** |

The truth is between the last two, and **closer to perfect subsumption than to independence**,
because B's arm had no tool output at all.

### 13.3 The residual is the answer, and it is a reasoning floor

`OBSERVED`: B's candidate used **14,824 input / 401 output**, of which **364 output tokens are
reported reasoning (90.8%)** and 37 are everything else.

So the composition question reduces to:

> Can Sol's *reasoning* on this task fall from 364 to below 285 (to hit 80% output against the
> 1,427 baseline), and can its input fall from 14,824 to below 9,079 (to hit 80% against 45,393)?

A can only help with the second. There is no mechanism in Helix that reduces reasoning without
violating the project's own rule. **Therefore 80/80 on Sol's current fixture is not reachable by
composing A and B. It is reachable only by (i) choosing a fixture with a larger mechanical baseline,
or (ii) reducing reasoning.**

### 13.4 What integration boundary minimises interference

`HYPOTHESIS`, with a concrete specification:

> **A supplies the semantic substrate; B supplies the actuation boundary. They must not both touch
> `W(t)`.**

Concretely: A's evidence selection must be **caller-evaluated and delivered complete** — the model
receives the selected evidence in the prompt and performs **no** tool call to obtain it. B then
receives the model's selection and performs **no** model-side verification. The two mechanisms meet
at a single interface: *the model returns semantic identifiers only.*

This is precisely what the winning trace did (`["r-04-2","r-07-2"]`). **The 67.3/71.9 result is
already the composed mechanism, executed once.** The composition question is therefore not "can we
add A to B" but **"is the 67.3/71.9 trace A-enabled or not?"** — and the manifest shows the
candidate received *"the same complete selection metadata"* as the control, i.e. **A was effectively
in both arms.** `OBSERVED` (`SOL_CALLER_COMPLETION_RESULT.json`, `manifest.comparison`).

**This is the most important thing in this section.** If A was in both arms, then A's marginal
contribution to B is already counted, the residual-independence arithmetic is measuring an
intervention that has already been applied to the baseline, and **the naive 83.5% is not merely
optimistic — it is double-counting a mechanism that is already inside the number.**

### 13.5 Does a route to ≥75/75 exist?

`CONDITIONAL`. Yes — but not by composition. By **fixture selection + boundary discipline**:

1. **Baseline inflation is legitimate if the baseline is realistic.** An ordinary agent asked to
   produce a 6,102-byte exact artifact from a 36,628-byte source, with strict booleans and
   inclusive-expiry traps, genuinely writes a script, runs it, inspects output, and fixes it. That
   is 2 commands and 2,068 bytes — already efficient. The control was **not** handicapped.
2. **The remaining lever is output.** 401 output, 90.8% reasoning. To reach 75% output against
   1,427, the residual must be ≤ 357. Observed: 401. **A 11% reduction away.** Plausible if the
   skill body is compressed (SkillReducer reports 26.8% end-to-end from skill compression alone
   [27](https://arxiv.org/html/2603.29919v2)) and if the caller's pinned catalog removes the need
   for Sol to reason about catalog validity.
3. **The remaining lever for input is the skill + evidence block.** 14,824 input with a 49-byte
   response means ~14.7k of input is context the caller supplied plus host prefix. Compressing the
   skill body and the evidence representation is the only route, and it is bounded by sufficiency.

**Realistic estimate for a clean composed Sol candidate: 70–80% input, 72–82% output, with the
median around 74/77.** `CONDITIONAL`. That straddles 75/75 and straddles 80/80.

### 13.6 Freeze recommendation

**Do not freeze on this pair.** Reasons, in order:

1. **n=1 pair, fixed arm order, no correction turn, no recovery case.** The repository's own
   `review.next` field says a 75% threshold was accepted by the user *and* that this pair reaches
   neither threshold — so there is nothing to freeze yet anyway.
2. **The control had 26,240 cached tokens; the candidate had 0.** On a price-weighted basis the
   saving is **45.7%, not 67.3%**. If the freeze threshold is economic, it has not been met.
3. **Zero tool calls is an untested capability boundary** (§10.6).
4. **The candidate received "the same complete selection metadata" as the control** — so this pair
   does not isolate B from A.

**Freeze the *boundary*, not the number:** caller-owned assembly, pinned immutable catalog, model
returns semantic identifiers only, catalog staleness fails loudly. That boundary is sound, cheap,
and testable. The number is one sample.

---

## 14. THREE CANDIDATE FUTURE ARCHITECTURES

### 14.A CONSERVATIVE — "Cache-Aware Helix V4"

**Target: 40–60% dollar reduction, strong parity, deployable now.**
`CONDITIONAL` on the price vector; gross-token savings will look worse than this.

| Element | Specification |
|---|---|
| **Information path** | Stable-prefix observation log (appended, never rewritten) + current event + typed evidence packet. Identical prefix across turns ⇒ maximal provider cache hits. |
| **Execution path** | Unchanged ordinary tool use. Engine mediates only explicitly-routed commands. |
| **Model responsibilities** | All semantic decisions, all verification that the Engine has not certified. |
| **Engine responsibilities** | Zero-inference indexing; content-addressed evidence; typed projection; **proof-carrying receipts**; caller-owned bookkeeping (never the model's); deterministic byte assembly on request. |
| **Memory responsibilities** | Append-only event log; exhaustive timeline fallback always available; **a search miss is an explicit FAILED retrieval, never an empty success**; integrity scan on query; no eviction policy needed at this scale. |
| **Reducer responsibilities** | Generic + pytest + compiler only. Small-output bypass. Raw archive always. **Do not open native interception.** |
| **Expected failure modes** | Log omits a decisive fact (mitigated: exhaustive fallback + late-relevance gate) · log grows and eventually must be summarized (unaddressed) · Astra ignores uncheckable receipts and re-derives. |
| **Irreducible costs** | `P_host` × N · reported reasoning · the first read of any evidence · the semantic decision itself. |
| **Measurable ceiling** | Input: the uncached fraction, 31–55% on long-horizon (§4.2). Output: 100 − reasoning share, i.e. ~52% for Luna, ~90% for Sol. Realistic: **45–60% dollar.** |
| **Assumptions required** | Provider cache discount ~0.1× · output:input price ratio ~8:1 · reasoning must not be suppressed · log sufficiency holds at 40+ turns. |

**Why this first:** it changes the *metric* and the *prefix shape* without opening the interception
gate or adding any mechanism the model must integrate. Both are low-risk and both attack terms that
are large.

### 14.B AGGRESSIVE — "Model-Specific Computation Placement"

**Target: 60–80% dollar on routable classes, with native bypass elsewhere.**

Adds to 14.A:

| Element | Specification |
|---|---|
| **Information path** | As 14.A, plus **task-class router** evaluated by the Engine *before* the model sees the task: evidence-assembly / long-horizon / novel-reasoning / mechanical. |
| **Execution path** | **Macro-action registry with engine-evaluated applicability predicates.** Model sees `APPLICABLE` or `NOT_APPLICABLE: reason`, never the implementation. Named plans are **deleted**, not paused (§3.2). |
| **Model responsibilities** | Semantic selection; eligibility; supersession; late relevance; what to do on FAILED retrieval. **Never:** byte copying, hash derivation, boilerplate, ledger maintenance, applicability determination. |
| **Engine responsibilities** | Everything deterministic, plus **binding-time analysis** at plan registration (explicit static/dynamic classification), plus proof-carrying receipts, plus a **memo layer** keyed on (task-class, input-hash, invariant-set). |
| **Memory responsibilities** | As 14.A, plus **procedural tier**: verified macro-actions admitted only after `checked_steps` passes on a held-out input (Voyager's "verify before admission" rule). Plus **admission and eviction policy** — currently entirely absent. |
| **Reducer responsibilities** | A conservative command-adapter registry with measured per-adapter coverage; **native interception opened** with truncation-aware framing; `discover`-style gap measurement. |
| **Expected failure modes** | Router misroutes and Helix overhead exceeds the saving (mitigated: bypass gate with measured per-class thresholds) · macro-action applicability predicate is unsound and the macro is applied where it shouldn't be (mitigated: `checked_steps` + transactional publication) · Astra's confirmation loop expands on unfamiliar receipts · **overfitting to development fixtures** (the biggest risk; §17). |
| **Irreducible costs** | `P_host` × N · reasoning · first-read evidence · the router's own misclassification cost. |
| **Measurable ceiling** | Evidence-assembly class: **70–85% dollar**. Long-horizon: **35–50%**. Novel-reasoning: **0% (bypass)**. Blended over a realistic mix: **55–70%.** |
| **Assumptions required** | All of 14.A, plus: applicability predicates are sound; task classes are identifiable from the prompt without inference; the router's cost is < 1% of task cost; memoization pays off (which self-adjusting-computation literature says is *not* guaranteed [20](https://www.cs.cmu.edu/~guyb/papers/ABBHT09.pdf)). |

### 14.C MOONSHOT — "Semantic Decision IR + Verified Reuse"

**Target: ≥80% dollar on a delimited class. Not a general architecture.**

The core idea: **stop treating the model's output as text and start treating it as a compiled
artifact against a semantic decision IR.**

| Element | Specification |
|---|---|
| **Information path** | The model never receives history. It receives a **decision frame**: the decision to be made, the minimal sufficient evidence set (engine-computed), and the constraint set. No replay. No retrieval injection. |
| **Execution path** | Model emits a **semantic decision IR** — typed, small: `(selection: [handle...])`, `(constraint: predicate)`, `(macro: id, binding-map)`. A deterministic **caller-owned continuation state** machine resolves the IR: expands handles, evaluates applicability, executes macros, assembles bytes, verifies invariants, publishes. **No second model turn on the success path.** |
| **Model responsibilities** | One thing: the semantic decision. Nothing mechanical, on any path. |
| **Engine responsibilities** | Everything else, including **recovery**: on IR validation failure, emit a typed error frame naming the failing handle/constraint — not a free-text error — so recovery is one short turn, not a repair loop. |
| **Memory responsibilities** | **Content-addressed reasoning artifacts**: (decision-class, constraint-hash, evidence-hash) → verified IR, with an explicit **invalidation trigger** and a staleness budget (FreshCache's risk-constrained reuse [23](https://arxiv.org/html/2607.04281)). Plus StepCache-style **per-step verification with skip-reuse fallback** [22](https://arxiv.org/html/2603.28795). |
| **Reducer responsibilities** | Full typed interception. Raw archive. Truncation-aware. |
| **Expected failure modes** | **IR is insufficient for a decision the designers didn't anticipate** — the model must be able to *escape* the IR into ordinary execution, and that escape hatch will be used, and every use must be counted · **constraint drift** invalidates cached reasoning silently · **the minimal sufficient evidence set is computed by the Engine and is therefore a semantic judgement made without a model** — this is the deep problem and it is not solved · IR design overfits to benchmark classes. |
| **Irreducible costs** | One model call per semantic decision · the decision's reasoning tokens · the first read of any novel evidence · the escape-hatch rate × full cost. |
| **Measurable ceiling** | On the **repeated-decision class** (same decision shape, different data): **85–95%** — because the model sees one frame and emits one IR, and everything else is memoized. On **novel-reasoning**: **negative** (the IR constrains more than it saves). |
| **Assumptions required** | Decisions are classifiable into a bounded IR · the Engine can compute minimal sufficient evidence without a model · escape-hatch rate < 20% · invalidation triggers are sound · **the IR does not silently cap capability.** |

### 14.D Where ≥80/80 IS attainable — the honest map

| Workload class | ≥80% gross input? | ≥80% gross output? | Why |
|---|---|---|---|
| **Repeated evidence selection → exact assembly** | **Yes** | **Yes** | Baseline is inflated by model-authored glue (N6/N7 prove it). Sol at 67.3/71.9 with a 37-token non-reasoning residual. |
| **Deterministic transformation / bulk mechanical edits** | **Yes** | **Yes** | No semantic content to lose; caller-side completion covers it. |
| **Repeated software workflows (same CI loop, same repro)** | **Likely** | **Likely** | Macro-actions + memoization; Voyager's 15.3× is the upper anchor [18](https://arxiv.org/html/2603.07670v1). |
| **Repeated evidence analysis over changing data** | **Likely** | **No** (reasoning floor) | Input is compressible; the analysis itself is not. |
| **Long-context research** | **No** (ceiling 31–55%) | **No** | `P_host` × N dominates and is not Helix-removable. |
| **Multi-turn agent projects, real workflows** | **Maybe, via turn amortization** | **No** | Turn amortization is real but unmeasurable on the current benchmark (§7.4). |
| **Novel reasoning-heavy** | **No** | **No** | By definition there is nothing to reuse and everything to think about. |

**Takeaway: 80/80 is a property of a workload class, not of an architecture.** The winning move is
**routing**, not universal compression. Architecture 14.B with a well-built router dominates any
architecture that applies one policy to everything.

---

## 15. NEW MECHANISM SHORTLIST

Ranked by `leverage × orthogonality × falsifiability ÷ (implementation + benchmark cost)`.

| # | Mechanism | Removes | Adds | Reconstruction risk | Cheap falsifier | Best phenotype | Score |
|---|---|---|---|---|---|---|---|
| **1** | **Stable-prefix observation log** (§7.1) | `R_hist` replay; cache misses | Observer writes (no inference) | **High** — model reads raw history if log is insufficient | 40-turn holdout; measure `history.jsonl` reads | All three; **Astra** | **9.0** |
| **2** | **Price-weighted cost metric** (§7.5) | Nothing directly — **it re-ranks everything** | ~20 lines | None | Recompute existing receipts (done here) | n/a | **9.0** |
| **3** | **Engine-evaluated applicability predicate** (§7.2) | M1 integration tax | Predicate eval (µs) | Low — verdict, not recipe | Luna cold-plan re-run with pre-evaluated verdict | Sol, Astra | **8.5** |
| **4** | **Proof-carrying evidence receipts** (§7.3) | M3 verification doubling | ~1–5 KB receipt | **Medium** — Astra may ignore an uncheckable receipt | A/B packet ± receipt; count re-derivations | **Astra** | **8.0** |
| **5** | **Skill-body progressive hydration** (§7.6) | Skill prefix every turn | On-demand module loads | Low — SkillReducer shows retention 0.91–0.96 [27](https://arxiv.org/html/2603.29919v2) | Offline: compress SKILL.md, run existing local tests | All | **7.5** |
| **6** | **Task-class router with bypass** (§14.B) | Negative-saving deployments | Router eval (deterministic) | Low | Replay: would the router have called V1/V2 W50? | **Luna** (variance) | **7.5** |
| **7** | **Caller-owned continuation state** (§14.C) | Second model turn on success path | State machine | Medium — recovery paths | Count turns-to-completion with/without | Sol | **7.0** |
| **8** | **Typed error frames for recovery** | Repair loops (Luna's dominant cost) | Error taxonomy | Low | Inject a failure; measure recovery turns | **Luna** | **7.0** |
| **9** | **Semantic decision IR** (§14.C) | All mechanical output on covered classes | IR design + escape hatch | **High** | Emit IR on 5 known task shapes; measure escape rate | Sol | **6.5** |
| **10** | **Content-addressed reasoning artifacts w/ invalidation** | Repeated reasoning | Store + invalidation logic | **High** — silent behaviour freezing | FreshCache-style staleness budget [23](https://arxiv.org/html/2607.04281) | Sol | **6.0** |
| **11** | **Native interception (open the gate)** | `W(t)` tool output | Hook latency; correctness surface | Medium | Already failed twice — needs envelope work | Astra, Sol | **5.5** |
| **12** | **Command-adapter registry** | Command output tokens | Per-adapter correctness surface | Medium | `discover`-style coverage on real traces | Astra, Sol | **5.0** |
| **13** | **Turn amortization** | `(N−1) × P_host` | Longer single contexts | Medium | Not measurable on current benchmark | Real workflows | **4.5** |
| **14** | **State diffing instead of replay** | History replay | Diff application | Medium | Offline: diff vs replay on 50-event fixture | All | **4.0** |
| **15** | **Speculative prefetch by deterministic policy** | Retrieval latency (not tokens) | Wasted prefetch | Low | Offline hit-rate | none | **2.0** |
| **16** | **Memory eviction / admission policy** | Storage | Risk of evicting decisive evidence | **High** | Not urgent — current scale doesn't need it | none | **2.0** |
| **17** | **Agent bytecode / model-specific command language** | Output tokens | A language the model must learn ⇒ **M1 returns** | Very high | — | none | **1.5** |
| **18** | **Embedding-based semantic memory retrieval** | Lexical misses | Embedding cost + latency | Medium | Helix's own rule: not before measured benefit | none | **1.5** |
| **19** | **Named plans (as currently designed)** | — | — | — | **Already falsified** (N10 + N11). Delete. | none | **0** |

**Two mechanisms the brief listed that I recommend against, with reasons:**
- **Agent bytecode / model-specific command languages** — every mechanism that requires the model to
  learn a new surface has paid the M1 tax in this corpus. N10 is a 62% input regression caused by
  exactly this.
- **Learned/automatic workflow caching** — the roadmap already excluded it, and correctly: it needs
  semantic applicability inference, which is the thing that is expensive.

---

## 16. CONDITIONAL THEOREMS AND UPPER BOUNDS

**T1 — Uncached-input ceiling.** `CONDITIONAL` on cached prefix being untouchable.
For any baseline episode, `max_gross_input_saving ≤ (I − C)/I` where `I` = total input, `C` = cached.
*Proof:* the saving can come only from tokens not served from cache, plus any induced reduction in
`C`. If `C` is fixed, the bound is the uncached fraction. ∎
*Measured:* W50 31.2–35.8%, L40 48.1–55.0%, Q4 16.5–17.5%, A 12.7–17.2%. *(Conservative: if
intra-invocation re-reads count as cached — which Q4's 83% cached fraction implies — then `C` is
partly reducible and the bound is loose by an unquantified amount. `UNKNOWN`.)*

**T2 — Reasoning output floor.** `CONDITIONAL` on `reasoning ⊂ output` and reasoning being held fixed.
`max_output_saving ≤ 1 − R/B`.
*From the repository's own `OUTPUT_FRONTIER.json`:* memory control 59.37%, memory candidate 48.64%,
Luna query-V2 45.68%, Sol query-V2 52.68%, Astra query-V2 100% (R=0, uninformative).
*Consequence:* **no mechanism that preserves High reasoning can reach 80% output on tasks where
reasoning exceeds 20% of output.** For Luna's V3 aggregate (67.4% reasoning) the ceiling is 32.6% —
and Helix achieved 32.93%. **Luna is at its output ceiling.**

**T3 — First-call fixed floor.** `CONDITIONAL` on the candidate leaving the first call unchanged.
`max_input_saving ≤ 1 − first_call_cost / total_cost`.
*From `engine/call-budget/RESULT.json`:* **66.33%** (baseline_large), 52.50% (hook_observe_large),
66.24% / 52.46% / 52.45% (other arms).
*This is the formal statement of the hostile claim "first-call fixed costs make 80% impossible."*
It is **true for that restricted intervention class only**, and the repository says so. It does not
bound redesigned first calls.

**T4 — Compound savings must not be summed.** (Repository Proposition 1.)
`G = Σ_{e∈∪S_i} w(e) − H`. Applied to Sol: the naive 83.5%/86.0% is invalid; the subsumption bound
is 67.3%/71.9%.

**T5 — Dual-budget amortization.** (Repository.)
`N·(0.2·b[d] − h[d]) ≥ H0[d] − 0.2·B0[d]`, required **separately** for input and output.
*Applied:* measured plan execution has `h > b` at both tested sizes ⇒ left coefficient negative ⇒
**no reuse count succeeds.** **Named plans are not unproven; under measured rates they are
non-amortizing.** Stop them.

**T6 — Generation displacement.** (Repository.) A deterministic mechanism saves output only when
the generation it avoids exceeds its generated setup + invocation + interpretation + recovery
overhead. *Applied:* N3 (Luna, −76.1% output) is the counterexample to using fewer commands as a
sufficient condition.

**T7 — Turn-amortization bound (new).** `INFERRED`.
`Total_input = N·P_host + Σ_t (M(t) + W(t))`. `P_host ≈ 10.5–12.8k` tokens/turn is
host-determined and model-independent (W50 off: Sol 18,520, Luna 17,906, Astra 18,665 — a 3.4%
spread across three models). Therefore:
> **The only lever on the largest single input term is N.** No evidence-compression,
> memory, or reducer mechanism can touch it. Batch, don't compress.

*Corollary:* Helix's entire mechanism portfolio addresses `M` and `W`, which together are 29–49% of
long-horizon input. **Even perfect performance on every existing mechanism leaves 51–71% of the
bill.**

**T8 — Cache-locality theorem (new).** `CONDITIONAL` on the runner counting intra-invocation re-reads
as cached.
If the prefix presented at turn `t+1` differs from turn `t` at any position before the last cached
boundary, all tokens after the divergence are billed at full rate.
> Per-turn retrieval injection guarantees divergence. **A stable append-only log is worth more than
> a smaller per-turn prompt**, because it converts full-rate tokens into 0.1× tokens.
*Magnitude, `INFERRED`:* if the stable log converts even 3,000 tokens/turn from full-rate to cached
on W50, that is `50 × 3,000 × (1.25 − 0.125) = $0.169` on a $0.540 baseline — **31 percentage points
of dollar saving on Luna W50 from prefix shape alone, with no change to what the model is told.**

**T9 — The 80/80 impossibility theorem for the current benchmark.** `CONDITIONAL` on T1 + T2 + the
host prefix being irreducible.
On Q4/A/W50/L40, for all three models:
- Input: `max ≤ 12.7–55.0%` (T1). **80% is unreachable.**
- Output: `max ≤ 32.6%` (Luna, T2), ~90% (Sol), ~100% (Astra, uninformative). **80% is unreachable
  for Luna**, and Astra's observed value is **negative**.
> **Therefore: no architecture evaluated on this benchmark can demonstrate gross 80/80 on all three
> models without either (a) attacking `P_host`, which requires turn amortization the benchmark
> forbids, or (b) suppressing reasoning, which the project forbids.**
>
> **The benchmark must change, or the target must change.** I recommend both: adopt a price-weighted
> target, and add a repeated-workflow task class where 80/80 is attainable.

**T10 — Where the remaining Helix headroom actually is.** `INFERRED`.
Combining T1 (achieved vs ceiling):

| Model | Task | Ceiling | Achieved | Headroom |
|---|---|---:|---:|---:|
| Luna | L40 | 49.2% | 27.8% | **21.4 pt** |
| Sol | L40 | 55.0% | 26.6% | **28.4 pt** |
| Astra | L40 | 48.1% | 24.3% | **23.8 pt** |
| Luna | W50 | 35.8% | 20.6% | 15.2 pt |
| Sol | W50 | 31.2% | 15.2% | 16.0 pt |
| Astra | W50 | 32.0% | 9.7% | **22.3 pt** |

**Astra has the largest absolute headroom and the worst achieved fraction — consistent with the
phenotype in §11: Astra does not deliberate, it confirms, and Helix has not yet given it anything
cheap enough to confirm *with*.** This is the strongest single argument for making Astra the
strategic target.

---

## 17. HOSTILE FALSIFICATION FINDINGS

I attempted to break Helix on each count the brief listed. Findings, most damaging first.

**H1 · "The savings are baseline variance." — PARTIALLY SUSTAINED, and this is the worst finding in
the dossier.**
Every headline number rests on **n=1 pair per model per experiment, with fixed arm order** and, in
the V3 battery, `order = ['off','on']` for Luna/Astra but `['on','off']` for Sol
(`run_benchmark.py`). No experiment in the repository has been repeated. No confidence interval
exists anywhere. The largest claimed effects — Sol 67.3/71.9, Luna 25.3/32.9 — are single
observations. **`SUSTAINED`.** There is no statistical basis for any point estimate in this project.
The repository discloses this repeatedly; that is not the same as fixing it.

**H2 · "Hidden work moved outside the accounting boundary." — SUSTAINED.**
Parent/coordinator conversation tokens are explicitly excluded from every saving claim and are
`UNKNOWN` (`cost-audit.json`). Caller CPU is measured but server compute is not. Physical I/O, disk
allocation, and the HUD's own I/O are unmeasured. **The most likely place for Helix's true cost to
hide is the parent conversation**, because a caller-side architecture moves work into exactly the
place the accounting excludes.

**H3 · "Gross savings are not billing savings." — SUSTAINED, decisively. See F2/F3.**
Astra's 25.67% input saving is 0.13% on full-price input. Sol's caller-completion 67.34% is 22.60%
on full-price input. External corroboration: CostCraft finds counting cache reads at the fresh rate
**overstates true cost by 1.6–2.0×** [25](https://arxiv.org/html/2604.23853v2).

**H4 · "Caller-side completion weakened agentic work." — NOT DISPROVEN, and the receipt admits it.**
`semantic_success: null`, deliberately. The winning trace has **zero tool calls**: the model did not
read the source, did not verify eligibility by inspection, and did not check its own output.
48 bytes of model response produced a 6,102-byte artifact. **On the tested fixture that is correct
and efficient. It is one fixture.** The repository's own next-step contract demands "changed
revision eligibility, strict booleans, correction turns, recovery" — none of which have been run.

**H5 · "Output savings come from shorter tasks, not better placement." — NOT SUSTAINED on the
evidence, but the design is vulnerable.**
Turn counts are matched within pairs (W50: 50/50; L40: 41/41; A: 1/1). Luna's largest output win
(W50, −51.2%) is on the *longest* task. So the specific charge fails. **But** the caller-completion
arm removed 2 tool calls, and that is a genuine shortening of the trajectory — and on that arm the
output saving and the task-shortening are the same event, so they cannot be separated by this
design. `UNKNOWN`.

**H6 · "Native tools were handicapped." — NOT SUSTAINED, and the controls are unusually strong.**
The control prompt explicitly says *"Use your normal behavior"* and both arms get identical models,
high effort, and full tool access. `render-pilot` allowed the ordinary arm Python and normal
copying. `MEMORY_NATIVE_FOLLOWUP` gave the candidate `rg` and `jq` and the control Python.
`LUNA_COLD_PLAN` gave **both** arms the same reusable processing script — and Helix still lost by
62%. Where Helix lost, it lost against well-armed controls. **This is a genuine strength.**

**H7 · "Helix gets free deterministic computation the control is denied." — NOT SUSTAINED.**
The control is allowed arbitrary scripting. `render-pilot` explicitly allowed ordinary Python.
`NAMED_PLAN_OVERHEAD` compares against "the existing checked executor." The one place where this
could bite — the caller-owned renderer — is exactly where Helix **lost** (N6/N7), which is evidence
the comparison was not rigged.

**H8 · "Evidence selection leaked expected answers." — NOT SUSTAINED, with one caveat.**
`render-pilot` explicitly states *"The model does not receive the oracle artifact hash or selected
groups in its prompt."* `selection-gate-v2` exists specifically to close a real coverage gap the
team found themselves. The caveat: the selection gate fixture was published, so it is **not a
holdout** — the repository says so.

**H9 · "First-call fixed costs make 80% impossible." — SUSTAINED for short tasks (T3: ≤66.3%), and
the stronger T1/T9 bounds cover long tasks.** This hostile claim is essentially correct.

**H10 · "Model-specific policies overfit development fixtures." — SUSTAINED as a live risk.**
The adaptive-diagnostic's own conclusion: *"These results do not establish a stable model-specific
advantage for every candidate."* Luna's per-task results swing from +42.6% to −94.7% (uncached
input). The V3 suite was reused adaptively across three iterations; Q and L40 controls were newly
run but A/W reused original controls. **No held-out set exists.**

**H11 · "Persistent memory loses latent future relevance." — PARTIALLY SUSTAINED, with a strong
mitigation already implemented.**
The memory payload fixture's selective path is 98.54% smaller **but assumes the correct literal
query** — the exact failure mode. Mitigation is real and good: a search miss is an explicit FAILED
retrieval, exhaustive timeline fallback always available, and all three models *did* recover the
decisive late fact on L40/W50. **But recovering it cost tokens**: the L40 on-arm still reads
3,450–4,964 tokens/turn of in-turn work. Recovery works; recovery is not free.

**H12 · "Exact retrieval destroys semantic recall." — SUSTAINED as a design property, mitigated by
fallback.**
`workflow_memory` is explicitly *lexical*: "Search ranking is recency among lexical matches, not
semantic relevance." MemoryAgentBench [9](https://arxiv.org/pdf/2507.05257) finds RAG-style memory
underperforms long-context models on holistic competencies. Mitigated by exhaustive fallback, but
the fallback is O(history).

**H13 · "Engine integration costs exceed savings." — SUSTAINED, three times.** N6, N7, N10. This is
M1 and it is the project's central empirical finding.

**H14 · "Benchmarking itself creates misleading costs." — SUSTAINED.**
The runner uses a fresh `--ephemeral` invocation per turn. **This inflates `P_host` to
10.5–12.8k tokens × N**, a cost structure that a native persistent session with prompt caching would
not have. *Consequence:* Helix is being benchmarked on a harness where the dominant cost term is an
artifact of the harness. **The measured ceilings in T1 are ceilings for this harness, not for
Helix.** This cuts both ways: it means the published 17–25% gross numbers understate Helix's value
in a real persistent session, and it means the architecture is being optimized against the wrong
cost structure.

### 17.1 What survives the audit

1. **The computation-placement finding survives, and is the strongest result in the project.** It is
   a sign reversal on two models across two mechanisms (N6/N7 → caller-completion), and a sign
   reversal is far more robust to baseline noise than a magnitude is. **This is the one finding I
   would bet on.**
2. **The negative results survive and are more informative than the positive ones.** N10, N11, N13,
   N14, N17 are unambiguous, and they correctly killed three lines of work.
3. **The accounting discipline survives.** Byte-vs-token-vs-dollar distinctions are maintained
   rigorously throughout; subsets are never double-counted; failures are retained; graders are never
   regraded after the fact. **This is better practice than most published agent research.**
4. **The dollar case survives and is stronger than published.** Even under the most conservative
   price assumptions tested (k=1.0, i.e. no cache discount at all), Helix V3 saves 16.5–25.7%. Under
   realistic GPT-5.x pricing, 32.0–45.8%.
5. **What does not survive: any point estimate.** n=1 everywhere, no repeats, no intervals, adaptive
   reuse of the suite, no holdout. **The project's numbers are directions, not magnitudes.**

---

## 18. ONE NEXT SOL EXPERIMENT

### SOL-COMPOSE-1 — "Does the composed boundary hold when the model must discover?"

**Why this one:** it tests the *only* thing that could falsify the strongest result in the project —
that caller-side completion's win is an artifact of the model being handed complete, correct
metadata and never having to verify anything.

| Element | Specification |
|---|---|
| **Control** | Ordinary Sol High. Same fixture, same complete raw source, ordinary tools, efficient scripting permitted and demonstrated in the prompt. No skill. |
| **Candidate** | Sol High + Helix skill + **caller-side completion with a pinned catalog**. Identical mechanism to `SOL_CALLER_COMPLETION_RESULT.json`. |
| **Task (fresh, frozen before execution)** | 48 records, 4 groups. **Two decisive differences from the previous fixture:** (i) eligibility for 2 groups depends on a precedence rule stated in a *separate* policy record the model must retrieve — not in the metadata; (ii) one group's latest revision is **unpublished** and one is **stale relative to the pinned catalog generation**. Target artifact frozen in advance; the model receives neither the artifact hash nor the selected groups. |
| **Exact intervention difference** | Only the caller-owned assembly boundary. Everything else identical: same prompt prefix, same raw source access, same model, same High effort, same tools. |
| **Measured variables** | Native input / output / **cached input** / **reported reasoning** · command count · command text bytes · recorded terminal bytes · tool calls · artifact SHA-256 + byte length · source-unchanged hash · **precedence-rule correctness (graded separately from byte equality)** · **number of turns to completion** · caller CPU seconds · object bytes read/written/hashed · wall seconds. |
| **Parity checks** | (1) Exact artifact bytes vs frozen expected. (2) Source unchanged. (3) Precedence rule applied correctly on both affected groups. (4) Unpublished revision *not* selected. (5) Stale catalog generation **detected and reported**, not silently used. (6) All 48 records eligible (no leaked selection). (7) No unreported retries. |
| **Contamination controls** | Fresh task directory; fixture hashes frozen and verified before launch; arm order **counterbalanced or explicitly randomized** (not fixed); **two independent replicates per arm (4 calls)** — this is the single change that would most improve the project's evidence base; no reuse of the previous fixture's records; the previous pair's numbers are **not** used as a control; same operator, same machine, same time of day if possible. |
| **Stop conditions** | Stop after: any execution failure; any accounting failure (missing usage fields); any overrun of 150,000 input / 6,000 output post-call thresholds; or completion of 4 calls. **No retries. No expansion to other models. No matrix.** |
| **Adjudication rule (prespecified)** | **Mechanism qualifies if and only if:** (a) all 7 parity checks pass in both replicates; (b) **uncached-input saving ≥ 40%** in *both* replicates (this is the price-relevant number; gross ≥60% is secondary); (c) output saving ≥ 65% in both replicates with **no decrease in precedence-rule correctness**; (d) the stale catalog generation is flagged in both replicates. **If (b) fails but (a) and (c) hold, the mechanism qualifies for the evidence-assembly class only and must be routed, not universalized — and the gross headline must be restated with its cache-adjusted value.** |
| **Cost** | ~4 calls, ≈ 120k input / 5k output. |
| **What it does NOT establish** | Workflow parity, long-horizon behaviour, recovery, cross-model transfer. |

**Why uncached ≥40% and not gross ≥75%:** gross ≥75% was achieved once with a control that had
26,240 cached tokens. That number is not reproducible as an economic claim. Uncached input is what
is billed at full rate.

---

## 19. ONE NEXT ASTRA EXPERIMENT

### ASTRA-RECEIPT-1 — "Will Astra stop re-deriving what the Engine already proved?"

**Why this one:** Astra has the largest absolute headroom (T10: 22–24 points on both long tasks), the
most stable input band (26–32% across three candidates), the cheapest baseline, and a negative
output result that nobody has explained. My leading hypothesis for the output regression is **M3**:
Astra's confirmation loop expands when it is given evidence it cannot cheaply check. This experiment
tests exactly that, and it costs four calls.

| Element | Specification |
|---|---|
| **Control** | Astra High, ordinary. Identical log-diagnosis task to `native-pilots/pilot-v2` (a typed projection already measured at +31.8% in / +33.8% out for Astra), fresh fixture values. |
| **Candidate A** | Same typed evidence projection, **no receipt.** |
| **Candidate B** | Same typed evidence projection **+ proof-carrying receipt**: source hash + byte range, the **explicit list of invariants independently verified**, omission count and retrieval handles, verifier identity and its independence from the producer. |
| **Task** | Fresh log-diagnosis with: exact numeric strings, JSON boolean/string distinctions, an early configuration fact, and **a primary failure deliberately outside the reducer's bounded diagnostic list** (forces recovery). Raw original file available to all arms. |
| **Exact intervention difference** | The presence and content of the receipt *only*. Byte-identical evidence otherwise. |
| **Measured variables** | Native input / output / cached / **reasoning** · command count · command bytes · terminal bytes · **count of model actions that re-derive an invariant the receipt already certified** (graded from the trace, prespecified taxonomy) · exact-answer correctness · source-integrity · **recovery correctness on the out-of-scope failure** · wall seconds. |
| **Parity checks** | (1) Exact answer including facts absent from the packet. (2) Source unchanged. (3) Out-of-scope failure correctly recovered in **all** arms. (4) No arm produces a partial packet accepted as complete. (5) Receipt invariants independently re-verified by the grader — a receipt that overstates is a **failure of the mechanism**, not a success. |
| **Contamination controls** | Fixture frozen and hash-verified before launch; **two replicates per arm (6 calls)**; arm order randomized; the pilot-v2 numbers are **not** reused as controls (different fixture); identical prompt prefix; same operator/machine. |
| **Stop conditions** | Stop after any execution/accounting failure, any receipt that fails independent re-verification, any overrun of 150,000 input / 6,000 output, or completion of 6 calls. No retries, no other models. |
| **Adjudication rule (prespecified)** | **Receipts qualify if and only if:** (a) all parity checks pass in both replicates; (b) the **re-derivation count falls by ≥50%** between Candidate A and Candidate B in both replicates; (c) Astra's **output does not increase** in Candidate B relative to Candidate A; (d) input saving ≥25% is maintained in Candidate B. **If (b) holds but (c) fails, receipts change Astra's behaviour but not its cost — report and do not deploy.** **If (a) fails on the out-of-scope recovery in any arm, the typed projection is insufficient for Astra regardless of savings.** |
| **Cost** | ~6 calls, ≈ 250k input / 8k output. |
| **Why this before anything else on Astra** | It is the cheapest test of the single mechanism that addresses Astra's largest loss term (M3), it produces a reusable artifact (the receipt schema), and its failure mode is informative either way. |

---

## 20. STOP / FREEZE CRITERIA

### 20.1 Stop now, do not resurrect

| Item | Reason |
|---|---|
| **Named plans / `execute-spec` cold recipes** | T5: left coefficient negative under measured rates; N10: +62% input on the only native test. **Delete, don't pause.** |
| **Embedding-based memory retrieval** | No measured benefit; Helix's own rule defers it; adds cost to the term Helix is trying to shrink. |
| **Microtask sweeps / three-model matrices** | Already stopped once (`TRACE_DIAGNOSIS.md`); H1 says the problem is power, not breadth. |
| **Byte-ratio claims as savings forecasts** | Already forbidden twice in-repo; enforce it. |
| **Alias recoding for selection** | Rejected for cause: −36 selection tokens, +649 input tokens. |

### 20.2 Freeze criteria (all must hold)

**Mechanism-level freeze** (e.g. caller-side completion):
1. ≥2 independent replicates on ≥2 **fresh** fixtures, arm order counterbalanced.
2. All prespecified parity checks pass in **every** replicate, including recovery and a
   late-relevance case.
3. **Uncached-input saving** reported alongside gross, and the price-weighted saving reported as
   `CONDITIONAL`.
4. Zero unreported retries; complete per-call receipts with trace hashes.
5. A **documented bypass gate**: the measured conditions under which the mechanism must be turned
   off for this model.

**Model-level economic freeze** (e.g. "Sol is economically dominant"):
1. All of the above, plus ≥1 task from **each** of the four workload classes in §14.D.
2. **Both** input and output thresholds met on a price-weighted basis, not gross.
3. A held-out task that was **not** used in developing the policy.
4. No regression on long-horizon output relative to native (currently **failing** for Sol: W50
   −26.1%, L40 −6.9%) — or an explicit, tested bypass that routes those tasks natively.

**Do not freeze on:** a single pair · a gross-token percentage · a fixture the policy was developed
on · any result where the control's cache state differs materially from the candidate's without that
difference being reported.

### 20.3 Metrics to adopt immediately

Replace the headline metric with a **price-weighted cost ledger**, reported as three numbers:
`gross token saving` · `uncached (full-rate) input saving` · `conditional dollar saving @ stated
rate card`. Never report one without the other two. Report `UNKNOWN` where a rate or counter is
absent.

---

## 21. FINAL RECOMMENDATION — THE NEXT 48 HOURS, IN ORDER

The brief asks what I would do, in order, to maximize the probability that Helix makes Sol and Astra
economically dominant **while preserving their intelligence and agentic behaviour.** Nine steps.
Total: **~14 native calls**, i.e. under 2% of the tokens the project has already spent on one
experiment family.

---

**Step 0 (0–1 h, zero native calls). Re-derive the ledger; adopt price-weighted accounting.**
Run `research/cache-adjusted-ledger/*.py` (already committed here). Publish a corrected table
alongside every existing number: gross, uncached, conditional-dollar.
*Why first:* it takes an hour, costs nothing, and it changes the answer to "is Astra worth
optimizing?" from 17.1% to 32.0%. **Every prioritization decision downstream depends on this, and
right now they are all being made on the wrong number.**

**Step 1 (1–4 h, zero native calls). Delete named plans.**
T5 proves non-amortization under measured rates; N10 proves +62% input. Removing them removes an
M1 surface, reduces the skill body, and removes a maintenance sink. **Subtraction is the highest-return
action available and it is free.**

**Step 2 (4–10 h, zero native calls). Build the stable-prefix observation log — offline only.**
Deterministic, no inference. The contract: append-only, never rewritten, rendered identically each
turn, exhaustive fallback always available, a miss is an explicit FAILED retrieval. Then run the
**40-turn offline holdout** (a turn-1 fact needed at turn 40) and measure whether the log alone is
sufficient — if it is not, the model will read `history.jsonl` and T8's gain evaporates.
*Why this is #2:* T8 says prefix shape may be worth ~31 points of dollar saving on W50 **with no
change to what the model is told.** That is the largest single identified gain in this analysis, and
it costs no native calls to build.

**Step 3 (10–14 h, zero native calls). Compress the skill body with progressive hydration.**
SkillReducer's external result is 48% description / 39% body / 26.8% end-to-end with retention
0.91–0.96 [27](https://arxiv.org/html/2603.29919v2). Helix's `SKILL.md` is ~1 KB today, so the
absolute gain is small — but the *shape* (core + on-demand modules) is what matters for the next
step, and it is free to build.

**Step 4 (14–18 h, 4 native calls). Run SOL-COMPOSE-1 (§18).**
Two replicates per arm, counterbalanced. This is the gate on the strongest result in the project.
*If it fails, the entire Sol strategy changes* — and it is better to know that for 120k tokens than
after a matrix.

**Step 5 (18–26 h, 6 native calls). Run ASTRA-RECEIPT-1 (§19).**
Two replicates per arm. Tests M3, the largest identified loss term on the model with the largest
headroom. Produces a reusable artifact (the receipt schema) regardless of outcome.

**Step 6 (26–32 h, zero native calls). Build the bypass router — replay only, no new calls.**
Using the ~900 existing receipts, fit the simplest possible deterministic router: task class →
Helix ON/OFF, with thresholds per model. Validate by replay: **would this router have disabled
Helix on V1/V2 W50 (Luna +139% input) and on Astra Q4 (−1.7%)?** A router that gets those two right
has already paid for itself, and it can be validated without spending a single token.
*Why this matters more than any new mechanism:* Luna's spread is −94.7% to +139%. A model with that
variance needs a gate, not a better compressor.

**Step 7 (32–40 h, 4 native calls, only if Steps 4 and 5 both pass). Engine-evaluated applicability
predicate + proof-carrying receipts, on Luna.**
Re-run the cold-plan task (N10's fixture) with the verdict pre-computed by the Engine so Luna never
reads Engine source. **Null: input saving still negative.**
*This is the cheapest way to distinguish two very different conclusions:* "plans are wrong for
Luna" (abandon) vs "**asking Luna to decide applicability is wrong for Luna**" (salvage the whole
macro-action line). The second reading is consistent with everything else in the corpus, and no
experiment has ever separated them.

**Step 8 (40–48 h, zero native calls). Rewrite the target and publish the corrected frontier.**
Change the objective from `≥80% gross input AND ≥80% gross output` to:

> **≥60% price-weighted cost reduction, verified on a held-out task, with a router that turns Helix
> off where it does not pay, and no reduction in reasoning effort.**

Then publish: the corrected three-number ledger, T1/T2/T3/T7/T8/T9 with their assumptions, all
nineteen negative results, and the workload-class map from §14.D. **The map is the deliverable: it
tells you where 80/80 is available and where it is provably not, which is worth more than another
point estimate.**

---

### 21.1 What I would NOT do in the next 48 hours

- **Not open the native interception gate.** It has failed twice and it is not on the critical path
  to any of the top five mechanisms. RTK's lesson is that installation is the product — but Helix's
  binding constraint today is measurement, not plumbing.
- **Not run a three-model matrix.** H1 says the project's problem is power per experiment, not
  breadth.
- **Not touch reasoning settings.** T2 already says the constraint binds; violating it would
  invalidate every parity claim.
- **Not chase Luna's cost.** Luna's output is at its T2 ceiling (32.93% achieved vs 32.6% bound).
  **Luna needs a router, not research.**
- **Not claim 80/80 from component arithmetic.** T9 proves it is unreachable on the current
  benchmark for all three models.

### 21.2 The one thing I would bet on

> **Helix's next-order win is not a better compressor. It is a stable prefix, a caller-owned
> actuation boundary, and a checkable receipt — plus the discipline to turn itself off.**
>
> The evidence for the placement thesis is a sign reversal across two models and two mechanisms,
> which is the most noise-robust kind of evidence this corpus can produce. The evidence for
> everything else — memory, plans, reducers, indexes — is either negative or unmeasured.
>
> **Stop adding surface area for the model to integrate. Start removing the reasons the model has
> to look.**

---

## APPENDIX A — Provenance of every number recomputed in this dossier

| Figure | Source file (branch `Helix-Output` unless noted) | Receipt/derivation |
|---|---|---|
| V3 per-task input/output/cached/reasoning | `results/frontier-v3.json` | verbatim |
| Per-turn `resident_prompt_proxy_tokens` | `results/frontier-native-usage.json` | verbatim; defined at `benchmarks/frozen-high/run_benchmark.py:58` as tiktoken `o200k_base` over the caller prompt |
| Query-V2 six traces | `engine/prototype/NATIVE_RECEIPT_RECHECK.json` | verbatim, SHA-256 verified by the repository |
| Sol caller-completion | `engine/output/SOL_CALLER_COMPLETION_RESULT.json` | verbatim |
| Luna cold plan | `engine/output/LUNA_COLD_PLAN_RESULT.json` | verbatim |
| Memory follow-up | `engine/prototype/MEMORY_NATIVE_FOLLOWUP.md` / `.json` | verbatim |
| Render pilot | `engine/render-pilot/README.md` | verbatim |
| Typed terminal / literal query | `engine/adaptive-diagnostic/TRACE_DIAGNOSIS.md` | verbatim |
| Output frontier / reasoning floors | `engine/prototype/OUTPUT_FRONTIER.json` | verbatim |
| First-call bound | `engine/call-budget/RESULT.json` | verbatim |
| Project corpus totals | `results/cost-audit.json` | verbatim |
| Named-plan overhead | `engine/prototype/NAMED_PLAN_OVERHEAD.md` | verbatim |
| Wrapper byte ratio | `engine/wrapper-qualification/RESULT.json` | verbatim |
| Index integrity cost | `engine/prototype/MEMORY_INDEX_INTEGRITY.md` | verbatim |
| Runner mechanics | `benchmarks/frozen-high/run_benchmark.py` | read directly |
| Uncached savings, dollar ledger, ceilings, T1/T7/T8/T10 | `research/cache-adjusted-ledger/{ledger.py,dollar.py}` | recomputed; **all rate assumptions marked `CONDITIONAL`** |

## APPENDIX B — External sources

1. OpenAI, *Introducing GPT-5.2* (pricing, 90% cache discount) — https://openai.com/index/introducing-gpt-5-2/
2. Mastra, *Observational Memory: 95% on LongMemEval* — https://mastra.ai/research/observational-memory
3. *GPT-5 Pricing Explained* (rate table) — https://crazyrouter.com/en/blog/gpt-5-pricing
4. Flexera, *Prompt Caching breakdown* (provider multipliers) — https://www.flexera.com/blog/ai/prompt-caching-breakdown/
5. Wu et al., *LongMemEval* (arXiv:2410.10813) — https://arxiv.org/pdf/2410.10813
6. *Letta (MemGPT)* architecture — https://aiwiki.ai/wiki/letta
7. *Letta vs LangChain Memory* — https://vectorize.io/articles/letta-vs-langchain-memory
8. *Letta (MemGPT) Walkthrough* — https://sureprompts.com/blog/letta-memgpt-walkthrough
9. *MemoryAgentBench* (arXiv:2507.05257) — https://arxiv.org/pdf/2507.05257
10. *RTK* project page — https://landscape.jimmysong.io/projects/rtk/
11. *RTK: The CLI Proxy That Cuts Your AI Coding Token Bill by 80%* — https://zengineer.blog/blog/tech/rtk-token-killer-deep-dive/
12. Anthropic, *Code execution with MCP* — https://www.anthropic.com/engineering/code-execution-with-mcp
13. *Code Execution With MCP: Cut Tool Tokens up to 98%* (comparative measured reductions) — https://particula.tech/blog/code-execution-with-mcp-token-reduction-pattern
14. Wang et al., *Executable Code Actions Elicit Better LLM Agents* (arXiv:2402.01030) — https://arxiv.org/abs/2402.01030
15. Microsoft, *CodeAct in Agent Framework* — https://devblogs.microsoft.com/agent-framework/codeact-with-hyperlight/
16. *Problem of Temporal Abstraction: Options Frameworks in RL* — https://www.imsuperintelligence.ai/post/problem-of-temporal-abstraction-options-frameworks-in-reinforcement-learning/
17. Wang et al., *Voyager* (arXiv:2305.16291) — https://arxiv.org/abs/2305.16291
18. *Memory for Autonomous LLM Agents* survey (arXiv:2603.07670) — https://arxiv.org/html/2603.07670v1
19. *Futamura projections / partial evaluation* — https://grokipedia.com/page/futamura
20. Acar et al., *An Experimental Analysis of Self-Adjusting Computation* — https://www.cs.cmu.edu/~guyb/papers/ABBHT09.pdf
21. *LLM Caching — Semantic, KV & Prompt Cache* — https://myengineeringpath.dev/genai-engineer/llm-caching/
22. *StepCache: Step-Level Reuse with Lightweight Verification* (arXiv:2603.28795) — https://arxiv.org/html/2603.28795
23. *FreshCache: Risk-Constrained Freshness-Aware Semantic Caching* (arXiv:2607.04281) — https://arxiv.org/html/2607.04281
24. *Semantic Caching for LLMs: TTLs, Confidence, and Cache Safety* — https://pyimagesearch.com/2026/05/04/semantic-caching-for-llms-ttls-confidence-and-cache-safety/
25. *ClawTrace / CostCraft: Cost-Aware Tracing for LLM Agent Skill Distillation* (arXiv:2604.23853) — https://arxiv.org/html/2604.23853v2
26. *SkillZip: Contract-Preserving Graph Compression* (arXiv:2608.05604) — https://arxiv.org/html/2608.05604
27. *SkillReducer: Optimizing LLM Agent Skills for Token Efficiency* (arXiv:2603.29919) — https://arxiv.org/html/2603.29919v2
28. DataCamp, *Claude-Mem Guide* — https://www.datacamp.com/tutorial/claude-mem-guide
29. *Embedding Memory into Claude Code* — https://dev.to/shimo4228/embedding-memory-into-claude-code-from-session-loss-to-persistent-context-54d8

---

*No production code was changed. No native calls were launched. No skill was modified. Every
recomputation is committed at `research/cache-adjusted-ledger/` and reproducible offline.*
