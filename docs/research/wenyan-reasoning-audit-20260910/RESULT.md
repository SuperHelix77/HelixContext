# Wenyan and reasoning tokens: influence is not enforcement

2026-09-10. Helix evidence cut `7489de6`. **Research only; no new native calls,
effort changes, output caps, language-mode activation or deployment.**

**Verdict:** a prompt can request economical reasoning, but the inspected skill
and supported interfaces do not establish a way to force a specific internal
language or exact reasoning-token count while preserving capability. Wenyan is
primarily a visible communication style. Do not equate fewer characters with fewer
tokens, or fewer displayed thinking-summary words with less model reasoning.

## Sources and boundary

The current [Caveman skill](https://github.com/JuliusBrussee/caveman/blob/15581d14007fd01fb3f132016741962f34936ca2/skills/caveman/SKILL.md)
was inspected at `15581d14007fd01fb3f132016741962f34936ca2`
(2026-09-07T08:19:43Z). It describes response styles, including three Wenyan levels,
and explicitly qualifies its character reduction separately from token reduction.
It contains no enforced internal-reasoning budget. Its visible-output constraints
also conflict with this project's normal-final-answer contract and required
progress communication. Treat these as audited source content, not activation.

The installed `nellavio` skill is a related Wenyan variant: 2,296 UTF-8 bytes,
546 `o200k_base` proxy tokens; hash in `COST_BOUND.json`. Its character-reduction
claim is not native reasoning evidence. Neither its persistence instructions nor
its request to remove hedging permits deleting meaningful uncertainty.

**OBSERVED:** the committed [Caveman benchmark runner](https://github.com/JuliusBrussee/caveman/blob/15581d14007fd01fb3f132016741962f34936ca2/benchmarks/run.py)
compares normal, concise and Caveman Anthropic responses and records output usage.
Its inspected call does not enable a separate thinking configuration or report
separate reasoning counters. This runner does not establish Wenyan internal-token
savings on Astra, Sol or Luna. We did not execute it or open any credentials.

The larger repository also has a distinct [reasoning-effort optimizer](https://github.com/JuliusBrussee/caveman/blob/15581d14007fd01fb3f132016741962f34936ca2/proxy/providers/openai/reasoning_effort.go).
When invoked under its intended policy gates, its helper fills an absent supported
effort field with `low`; it preserves an explicit caller effort. This is effort
selection, not language compression. Comments acknowledge possible answer changes.
Source inspection is not proof that a particular deployment enables the helper or
that its eval gate establishes broad parity. Our explicit High/XHigh conditions
remain intact.

## Actual controls

Current [official OpenAI reasoning documentation](https://developers.openai.com/api/docs/guides/reasoning)
documents qualitative `reasoning.effort`, usage counters and optional reasoning
summaries. Raw reasoning is not exposed. `max_output_tokens` constrains the combined
generation and can terminate a response before a visible answer. A summary setting
does not specify a reasoning budget. These controls do not promise unchanged quality.

The local Codex app-server schema snapshot exposes `effort` and `summary`, with
`outputSchema` governing the final assistant message. The inspected turn/settings
properties do not expose a separate internal-language or exact reasoning-budget
field (`SCHEMA_AUDIT.json`). This is a bounded client-interface observation, not
proof of every possible hosted capability. No undocumented field was attempted.

## Zero-inference tokenizer check

We counted the upstream author's own example strings using `o200k_base`:

| Example | English style | English tokens | Wenyan style | Wenyan tokens |
|---|---|---:|---|---:|
| React rendering | full | 22 | full | 23 |
| React rendering | ultra | 14 | ultra | 13 |
| Connection pooling | full | 16 | full | 20 |
| Connection pooling | ultra | 11 | ultra | 15 |

All Wenyan versions have fewer characters. Three of these four comparisons use
more tokenizer tokens. **OBSERVED lexical examples only:** this is neither a
representative language benchmark nor a semantic-equivalence certification. It
refutes a general assumption that shorter Wenyan strings must tokenize more cheaply.
Native models may use different tokenizers; internal representation remains unknown.
`TOKEN_EXAMPLES.json` preserves the counted examples and exact basis.

## Existing Astra receipts kill the narrow rescue hypothesis

The latest [mixed W50 candidate](../w50-semantic-v1/RESULT.md) used 7,797 output
tokens, including 1,137 reported reasoning tokens (14.58%). Control output was
6,009. Even the hypothetical free deletion of the entire candidate reasoning subset,
with everything else fixed, leaves:

`7,797 - 1,137 = 6,660`, or **10.83% more output than control**.

The 80%-saving budget is 1,201.8 tokens. Thus reasoning-token compression *alone*
cannot rescue this recorded trajectory under unchanged other output. This is not
an irreducible capability bound: changed behavior could alter tool code, number of
segments and final output too. Nor is zero reported reasoning equivalent to zero
semantic computation; the model makes semantic choices in ordinary tool/code output.

This calculation does not generalize to Luna or other tasks whose reported reasoning
share is different. It prevents spending another Astra call solely to validate a
mathematically insufficient deletion strategy. Stream hashes and arithmetic are in
`COST_BOUND.json`.

## Research decision

Keep the accepted model effort, ordinary tool access and complete model-written
answers. Do not hard-cap thinking, force Wenyan finals or silently select low effort.
If a later prompt candidate targets redundant *work* at unchanged effort, measure
reported reasoning, all other output, repeated input, uncached input, calls and full
task success separately. Keep native-counter auditing, independent probes and hostile
value-domain checks. Smaller summaries or display text are not a saving receipt.

An internal-language instruction is at most an **UNTESTED behavioral hypothesis**.
The tokenizer examples supply no reason to privilege it over concise ordinary
instructions, and current Astra cost anatomy supplies no route from that change
alone to 80/80. No Wenyan native sweep is justified by this audit. A future experiment
would need a concrete predicted behavioral change beyond the reasoning-count term,
with fresh matched trials and unchanged capability gates.

The goal remains open. No new parity claim, release median or self-application is
created here. Downloads, source inspection and coordinator analysis are R&D cost.
