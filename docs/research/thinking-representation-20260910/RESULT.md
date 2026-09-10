# Reasoning representation: languages, notation, and the unchanged final answer

2026-09-10 · Evidence cut `6113735` · **Research and offline accounting only**.
No native model calls, production changes, effort changes, or skill activation.

**Verdict:** reasoning-language choice has direct experimental precedent worth
testing. Special characters have no general token advantage. The best initial
Helix candidate is concise internal working with familiar code/math notation;
modern-language alternatives remain separate, model-specific candidates. Nothing
reviewed establishes capability-preserving thinking-token savings on Astra, Sol,
or Luna. Keep their ordinary model-written final answers intact.

This qualifies the previous [Wenyan audit](../wenyan-reasoning-audit-20260910/RESULT.md):
its character/token warning survives, but lexical counts alone cannot predict
whether a language changes the model's reasoning trajectory.

## Primary evidence and hostile adjudication

| Source | What its experiment establishes | Helix verdict |
|---|---|---|
| [EfficientXLang, EMNLP Findings 2025](https://aclanthology.org/2025.findings-emnlp.845.pdf) | English questions, target-language reasoning, English finals; DeepSeek R1/QwQ/Qwen3 on four math sets. DeepSeek R1's MATH500 row reports unchanged TLP@4 and 18.41% fewer tokens in Chinese, 32.85% Spanish, 36.96% Russian, 37.80% Korean. | **EXTERNAL / CONDITIONAL.** Directly relevant separation. TLP@4 combines correctness and language compliance, estimated from 16 samples; it is not single-run accuracy or workflow parity. Harder-set performance declines. Table 1 and Table 2 use inconsistent change-sign conventions; use absolute Table 8 or explicit per-dataset rows. Open-weight math results do not qualify hosted coding agents. |
| [Chain of Draft](https://arxiv.org/html/2502.18600v2) | On GSM8K, GPT-4o changes from 205.1 tokens / 95.4% accuracy to 43.9 / 91.1%; Sonnet changes from 190 / 95.8% to 39.8 / 91.4%. Some simpler tasks improve both metrics. | **EXTERNAL / CONDITIONAL.** Approximately 79% reduction with 4.3–4.4 percentage-point math loss fails our gate. These are prompted, visible reasoning responses against a CoT baseline, not native Astra hidden-reasoning counters. Do not adopt a five-word-per-step restriction. |
| [How Well do LLMs Compress Their Own Chain-of-Thought?](https://arxiv.org/html/2503.01141v2) | Tests 31 prompts including Chinese, equations-only, abbreviations, no spaces, and length/step limits. Finds substantial accuracy/length tradeoffs and model-dependent prompt rankings. | **EXTERNAL.** Useful counterweight to universal compression claims. The paper's token-complexity limit depends on an explicit assumption; it is not a proved lower bound for Helix or all possible reasoning representations. Visible-response experiments also differ from our hidden-counter intervention. |
| [Language Mixing in Reasoning Language Models](https://aclanthology.org/2025.emnlp-main.132.pdf) | Controls script during reasoning by masking token logits, releasing the constraint for the final answer. Reports accuracy effects on open reasoning models. | **EXTERNAL / INTERFACE MISMATCH.** Demonstrates a real decoder boundary, not a skill-level enforcement mechanism or a token-saving result. No such internal logit-mask control was found in the inspected Codex interface. |
| [Chinese coding preliminary study](https://arxiv.org/html/2604.14210) | Changes task-prompt language, not just reasoning language. Excludes some errored runs and reports different arm denominators. | **EXTERNAL / DOWNGRADED.** Table 2 has the arithmetic anomaly below. Do not use its headline to reject reasoning-only Chinese. Zero reported reasoning also does not establish that a model cannot reason. |
| [Thinking with Reasoning Skills](https://aclanthology.org/2026.acl-industry.154.pdf) | Retrieves procedural cards to reduce rediscovery. Table 1 includes both improvements and reversals: GPT-OSS coding accuracy improves while output and normalized cost increase. Some reported “thinking” measures are completion proxies. | **EXTERNAL / ADJACENT.** Supports studying reusable methods, not a special alphabet. Reported per-query price-ratio accounting is not Helix's complete construction/retrieval/recovery amortization. No new memory tier is justified by this paper alone. |

The PDFs/HTML were retained privately and hashed in [SOURCES.json](SOURCES.json).
We visually checked EfficientXLang's table page to avoid relying on broken PDF
column extraction. External results are neither our replications nor release evidence.

## A counter-study with questionable accounting

**OBSERVED arithmetic, cause UNKNOWN:** multiplying the Chinese-coding paper's
printed means by its arm counts reconstructs nearly identical English/Chinese
totals for every nonzero token metric. For example, MiniMax input is
`298,720 × 50 = 14,936,000` versus `382,974 × 39 = 14,935,986`.
All eight nonzero comparisons permit the same total under nearest-integer
rounding. Its reported mean ratios consequently track the inverse sample-count
ratios. This could reflect an aggregation/reporting issue; raw per-task receipts
are needed to distinguish causes. We cannot assign a causal language penalty from
these aggregates. [Audit arithmetic](AUDIT.json); [source Table 2](https://arxiv.org/html/2604.14210).

## What special characters actually buy

**OBSERVED lexical census:** nine notation pairs and six short contract variants,
counted with `o200k_base` and `cl100k_base`. These are public, manually authored
statements, not captured model reasoning or a representative language benchmark.

| String | o200k tokens | cl100k tokens |
|---|---:|---:|
| `x != y` | 3 | 3 |
| `x ≠ y` | 4 | 3 |
| `a and b` | 3 | 3 |
| `a ∧ b` | 4 | 3 |
| `x` | 1 | 1 |
| `𝑥` | 3 | 3 |
| The value is not null and the count is at least 10. | 14 | 14 |
| `value != null and count >= 10` | 8 | 8 |
| Modern Chinese rendering of that short condition | 9 | 11 |
| Wenyan-like rendering | 9 | 10 |

The 14→8 example is a **42.9% reduction in a supplied representation**, not a
42.9% reasoning improvement. Its code-like notation assumes the ordinary intended
null/comparison semantics; different programming languages may require different
operators. Translations are not automatically semantic equivalents in every domain.

**INFERRED recommendation:** prefer familiar notation when its meaning is already
clear. A prettier glyph, emoji, rare character, or custom alphabet is not a new
model token. Character count, UTF-8 bytes, tokenizer tokens, and model competence
with a notation are separate variables. Context changes tokenization too.

Base64 and zlib/base64 round trips are also measured in the audit. Exact byte
recovery does not imply that a model can reason directly over the encoding. A
decoder, legend, expanded context, or extra model turn must be charged. Do not
introduce an unfamiliar codebook just to make a string look smaller.

## Can a skill force this only inside thinking?

**UNKNOWN compliance; supported steering only.** The inspected client exposes
reasoning effort and summaries, but no internal-language enforcement field. A
prompt may influence behavior; it cannot prove the language of inaccessible
reasoning. Reasoning summaries are not the raw trace and should not be used as a
language-compliance certificate. See the [local schema audit](../wenyan-reasoning-audit-20260910/SCHEMA_AUDIT.json)
and [official reasoning guide](https://developers.openai.com/api/docs/guides/reasoning).

Keep High/XHigh fixed. Do not substitute low effort, smaller output caps, shorter
displayed summaries, or a forced early final for representation efficiency.
Decoder constraints and latent-token methods require different runtime/model
access; they are not supplied by renaming a skill.

## The Helix cost boundary

Let `R` be reported reasoning tokens and `V` all other generated tokens, including
tool calls and the normal final. With uncached/cached input `Iu/Ic`, the accounting
identity for a candidate is:

`net saving = po × [(R0 − R1) + (V0 − V1)]`
`           + pu × (Iu0 − Iu1) + pc × (Ic0 − Ic1)`
`           − incremental preparation/retrieval/recovery cost`.

Use an explicit price snapshot if evaluating currency; this is not an included-plan
quota formula. Retries belong in the arm totals. Do not double-count reasoning if
it is already included in the API's output counter. This is accounting, not a new
theorem about cognition.

The [existing mixed-W50 receipts](../wenyan-reasoning-audit-20260910/COST_BOUND.json)
have candidate `R=1,137` within `O=7,797`, versus control `O=6,009`.
**CONDITIONAL:** halving only candidate R leaves 7,228.5 output tokens, still
20.29% above control. Even deleting all R leaves 6,660. Language steering might
change other generated work or calls, but that would be a new behavioral result,
not evidence from this subtraction. Do not spend a native run expecting this
narrow intervention alone to rescue that failed candidate.

## Decision for Astra, Sol, and Luna

| Candidate | Decision now | Reason |
|---|---|---|
| Concise English working + familiar code/math notation | **HYPOTHESIS: first pilot candidate** | Small interface change; preserves exact identifiers and allows expansion. No hard word/step limit. |
| Modern Chinese, Spanish, or Russian reasoning; ordinary final | **HYPOTHESIS: separate language arms** | External precedent warrants testing, but there is no measured best language for any Helix model. Select one before a run; do not screen many and conceal the selection cost. |
| Wenyan/classical shorthand | **DEFER** | Inspected Caveman evidence does not qualify thinking savings. Archaic compression may add interpretation work or erase qualifications. |
| Unicode-only / custom glyph codebook / encoded working | **REJECT as default** | Local counts provide no general advantage; comprehension and decoding costs are unqualified. |
| Hard thinking limit, lower effort, forced short final | **REJECT for this objective** | Changes the capability/output contract instead of demonstrating representation efficiency. |

No candidate is applied to this coordinator. The narrowly specified, future
[pilot protocol](PROTOCOL.md) preserves normal model-written answers and counts
actual native reasoning tokens without asking for or storing private reasoning.
Successful small pilots would justify a fresh capability cohort, not a parity claim.

Reproduce the offline census with `python3 audit.py` in this directory; `--write`
regenerates the data. It checks saved counts and table arithmetic, not model ability.
