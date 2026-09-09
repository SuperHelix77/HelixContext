# Astra Medium research dossier 01 — frozen intake

**Council role:** independent architecture/mechanism research cell

**Evidence cut:** supplied package reflects the Helix state before the later Sol Integrated V2 `70.5% input / 73.1% output` development result. Do not retroactively rewrite this dossier with later evidence.

**Source package:** `extreme-llm-token-reduction-research.zip`

- source ZIP SHA-256: `4cca96670a9b7bcb9428e0762b7efde9b7c2a432b30a9ef3c155f700d159517f`
- extracted `src/research.ts` SHA-256: `79a13669b6b23d77195eb0f496b3c4091c0a4424cffb72f7ae33c86dca018a07`
- generated package contained a Vite/React research UI; this dossier freezes the substantive research content, not the presentation layer.

## Evidence status

The research cell explicitly marked supplied Helix experiment numbers as **reported observations, not independently verified**. External references establish architectural precedent only; they do not verify Helix performance.

## Executive verdict

The cell converges on the same high-level shift now emerging elsewhere in the council:

> **Representation reduction is not computation reduction.**

Helix should move toward **computation placement**: the model retains novel semantic judgment, evidence sufficiency decisions, and genuine caution; the Engine should own deterministic mechanics, exact assembly, bookkeeping, hashing, state maintenance, checked execution, and previously established mechanical verification.

The cell does **not** claim universal `80/80`. It treats `75/75` as an economically meaningful intermediate target and warns that novel reasoning-heavy tasks may have a fixed semantic floor too large for `80/80`.

## Model-specific findings

### Sol High

**Reported observation:** caller-side deterministic completion was the strongest supplied end-to-end result at the evidence cut: approximately `67.3%` less native input and `71.9%` less native output, with correct artifacts reported for both arms.

Mechanism boundary:

1. Sol makes the semantic selection.
2. Caller/Engine performs exact artifact assembly and byte verification.
3. The model is not asked to emit the mechanical completion.

Historical selective evidence was reported at approximately `49.6% input / 50.0% output` savings.

The cell explicitly rejects multiplying these component savings as though independent. It recommends a matched factorial experiment to measure overlap and interaction.

### Luna High

**Reported observation:** cold generic named plans regressed badly: approximately `62.4% more input / 43.9% more output` despite a correct final artifact.

Visible behavior reportedly included Engine-source inspection, generated integration/setup code, and additional verification. A separate selective-memory experiment reportedly reduced input by `39.7%` while increasing output by about `15%`.

Working phenotype hypothesis: Luna should receive a tiny stable typed interface, explicit preconditions and failures, and aggressive native bypass. Generic API discovery and helper-source inspection should not be normal execution paths.

### Astra High

**Reported observation:** historical exact-evidence work reportedly saved approximately `25.7% input / 38.6% output`.

The cell treats repeated verification/source inspection/state reconstruction as hypotheses derived from visible behavior, not privileged access to hidden reasoning.

Its primary Astra mechanism is a **scoped proof-carrying execution receipt**: versioned operation identity, immutable input root, executor/verifier versions, output root, exit status, checked predicates, unchecked obligations, exact-evidence retrieval handle, and a checker verdict from a configured trust boundary.

Important caveat preserved by the cell:

- a hash binds bytes; it does not prove semantic correctness;
- a signature identifies an issuer; it does not prove the issuer's assertions;
- a test receipt proves only the stated test execution/result;
- Astra must retain semantic judgment about requirement adequacy, evidence sufficiency, unexpected effects, and uncaptured obligations.

## Cost model

The cell decomposes Helix cost into these practical categories:

| Component | Candidate action | Key warning |
|---|---|---|
| Fixed instructions | amortize | provider framing / required policy may remain a native floor |
| History & source | select / relocate | retrieval and reconstruction still cost; sufficiency remains semantic |
| Semantic reasoning | preserve | novel judgment may dominate and cap maximum savings |
| Procedural generation | relocate / reuse | cold setup can negate savings |
| Tool integration | remove from model | only if the interface is already understood |
| Mechanical verification | relocate / cache | scope, trust boundary and freshness remain explicit |
| Coordination & recovery | relocate / amortize | novel failures still wake the model |
| Helix overhead | minimize / count | schemas, receipts, retrieval, setup and retries are not free |

## Mechanism library

### M01 — Semantic decision IR — P0 — Sol

**Thesis:** let the model choose meaning; let the runtime produce the bytes.

A task-specific typed selection carries stable source IDs, exact spans, ordering, and semantic choices. The caller owns joins, copying, formatting, hashing, and publication. Unknown IDs or incomplete selections fail before side effects.

Failure boundary: ambiguous selection, unstated formatting requirements, or novel transformation logic must remain an unresolved obligation for the model or native execution. No silent approximation.

### M02 — Proof-carrying receipts — P0 — Astra

**Thesis:** replace “trust this helper” with scoped, checkable execution claims.

Receipt contains operation/version, immutable input root, environment digest, output root, exit status, checked predicates, unchecked obligations, and evidence handle. Only allowlisted verifier versions and matching dependency roots may be accepted.

### M03 — Prepared agent statements — P1 — all models

**Thesis:** reason about a bounded procedure once, then bind fresh parameters later.

Transfer from database prepared statements: cache a validated typed workflow, its parameters, preconditions, dependencies, and invalidation rules—not hidden reasoning.

### M04 — Semantic delta execution

**Thesis:** previous verified state + semantic delta → minimal recomputation.

Only invalidated dependencies and unresolved semantic obligations return to the model. This is an incremental-computation / build-system style attack on repeated state reconstruction.

### M05 — Persistent task frames

Keep goals, decisions, unresolved questions, dependencies, and exact references outside conversational replay. Preserve model-visible uncertainty rather than collapsing it into a falsely complete summary.

### M06 — Transparent typed reducers

Intercept before the model, preserve raw evidence and exact failures, and use native fallback. Evaluate by native token impact, not byte reduction alone.

### M07 — Model-specific agent ABI

One semantic runtime may expose different measured presentations per model. Candidate instruction set: `SELECT`, `RETRIEVE`, `APPLY`, `VERIFY`, `CONTINUE`, `EMIT`.

Desired properties: minimal description length, deterministic semantics, explicit failures, no routine Engine-source inspection, stable session-to-session behavior.

### M08 — Caller-owned continuations

Wake the model for unresolved judgment, not for every deterministic step. Use explicit continuation IDs, durable events, idempotency keys, transactional publication, and safe replay/compensation rules.

### M09 — Prepared context slices

Materialize bounded evidence views with the query, source roots, selection policy, exact handles, and coverage gaps. Reuse only while dependencies and task scope still match. Never present a selected slice as universally sufficient.

## Proposed experiments

### EXP-001 — Selective evidence × caller completion — Sol High — P0

A matched `2×2` factorial:

- A: native control
- B: selective evidence only
- C: caller completion only
- D: both

Keep task instances, tools, model version, reasoning settings, immutable inputs, and evidence recoverability matched. Randomize arm order and repeat trials. Count every model call, setup, retrieval, retry, failure, verification step, and Helix overhead.

Primary decision gate: support `75/75` only if both aggregate native savings clear the target under prespecified uncertainty and quality gates. Do not infer interaction by multiplying historical percentages.

### EXP-002 — Receipt-backed mechanical verification — Astra High — P0

Compare:

- raw results
- compact unstructured summary
- checker-backed receipt

Seed stale dependency roots, altered outputs, missing tests, unknown verifier versions, and semantic requirement violations outside certified predicates. Mechanical invalidity must fail mechanically; semantic violations must still elicit model judgment.

### EXP-003 — Rigid ABI vs native bypass — Luna High — P1

Compare native execution, generic plan, and a six-command typed ABI. Separate cold first-use setup from warm repeated tasks. Do not hide exact evidence; make Engine-source inspection unnecessary rather than impossible.

### EXP-004 — Dependency-aware procedure reuse — all models — P1

Evaluate cold preparation and repeated parameter bindings at `1, 5, 10, 25` uses. Include changed dependencies/tool versions/policies. Report break-even horizon, invalidation frequency, recovery work, and false cache-hit rate.

## External sources used by the cell

1. Packer et al., **MemGPT: Towards LLMs as Operating Systems** — virtual context management and explicit memory tiers; architectural precedent only.
2. Bazel official docs, **Remote caching** — action hashes, content-addressed outputs, declared inputs/environment/toolchain identity for reuse/invalidation.
3. PostgreSQL official docs, **PREPARE** — separation of parse/analyze from execution, generic vs parameter-specific plans, dependency-triggered replanning.
4. George C. Necula, **Proof-Carrying Code** — precedent for mechanically checked scoped properties; Helix receipts are not automatically PCC.
5. RTK project documentation — specialized command filters, grouping/truncation/deduplication; command-output savings are not end-to-end agent savings.
6. Claude-Mem project documentation — progressive disclosure via search/timeline/detailed observations; AI-generated memory creation cost must be counted separately.

## Strong claims the cell explicitly refuses

- byte reduction = native token reduction;
- payload reduction = end-to-end cost reduction;
- component percentages combine independently;
- integrity hashes prove semantic correctness;
- one model phenotype generalizes to all models;
- `80/80` is universally attainable;
- task correctness on one assembly fixture establishes general capability parity.

## Council interpretation

This dossier independently strengthens four candidates already emerging elsewhere:

1. **semantic decision IR / caller-owned deterministic completion**;
2. **proof-carrying / scoped certified receipts for Astra**;
3. **prepared cognition / dependency-aware procedure reuse**;
4. **semantic-delta / persistent task-state execution**.

It also strongly supports model-specific policies and native bypass rather than a universal Helix mode.

No mechanism in this dossier is promoted by intake alone. All remain candidates for later disagreement-matrix adjudication against Kimi, Arena, other Astra cells, repository receipts, and fresh falsifiers.
