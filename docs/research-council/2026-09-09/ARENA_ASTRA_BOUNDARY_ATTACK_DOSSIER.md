# Arena Astra boundary attack — frozen intake

**Role:** clean-room hostile architecture review of the Helix-Astra responsibility boundary.

**Access constraints:** researcher had **no GitHub access** and used only the supplied brief. No native benchmarks were run and no external sources were used.

**Imported artifact provenance**

- Uploaded archive: `helix-agent-cost-optimization.zip`
- Archive SHA-256: `632335b401b818c1a09b3c7754858b640ce5527b9ac93b64fb416d87b3d2926f`
- Extracted `src/App.tsx` SHA-256: `7b29475417c50d07783d9022bdb9a5385844a5e9c968d8119584840f895f4ef0`
- `package.json` SHA-256: `120a85258bae0ebae05d6096bb64cad2dd52b0229cdcafe875cedc6f51d99726`

This file freezes the research conclusions. It is **not** a Helix implementation decision.

## Executive verdict

**INFERRED — MODIFY, THEN FALSIFY.**

The preferred responsibility boundary is **Boundary B: batch deterministic execution, then preserve an Astra semantic review turn**.

The researcher rejects both extremes:

- **Boundary A:** Astra drives execution and review throughout. Safest continuity, but potentially expensive.
- **Boundary C:** caller/Engine closes the task without another Astra turn under a prior completion contract. Not justified on the supplied coding evidence because an apparently successful mechanical result can still contain a semantic defect.

Recommended pattern:

> Astra decides the patch → caller/Engine applies exactly that patch and runs already-authorized checks → Astra reviews changed state and decides whether the task is actually complete.

The recommendation is deliberately more conservative than exception-only semantic re-entry.

## Evidence discipline

The dossier explicitly treats all Helix numbers as **SUPPLIED**, not independently verified.

Supplied development comparisons used by the researcher:

| Comparison | Native input change | Output change | Signal |
|---|---:|---:|---|
| Sol selection/assembly | −88.10% | −88.98% | narrow success |
| Astra selection/assembly | −67.35% | −65.78% | below target |
| Astra coding repair | **+29.66% cost** | −6.35% | regression |

The researcher preserves these limitations:

- Sol’s headline total-input result is not the same as uncached-input or monetary savings.
- Astra coding regression is not explained by bootstrap, receipts, or redundant reading from the supplied evidence.
- Caller registration was already owned outside the model in the supplied coding run.
- No Engine implementation read or generic API discovery was observed in that run.
- Post-edit rereading may represent useful semantic review rather than waste.
- Lossless representation compression can increase model output/reasoning work.

## Responsibility boundary

**INFERRED:** Astra should own the semantic decision and all ambiguity-bearing judgments.

Astra should decide:

- what repair/patch to make;
- how requirements should be interpreted;
- what checks are semantically adequate;
- whether evidence is sufficient;
- whether the changed code actually solves the task;
- how to respond to unexpected behavior.

Caller/Engine may own only mechanics already fixed by Astra’s recorded decision and bound state, including:

- applying the exact chosen patch to the bound preimage;
- running already-authorized checks;
- exact copying and serialization;
- state/version bookkeeping;
- transactional publication;
- mechanical predicate checks;
- exact evidence retention.

Determinism alone is not sufficient authority. State, requirements, and authorization must still be valid immediately before execution.

## Preferred flow

`ASTRA: decide patch` → `CALLER/ENGINE: apply + check` → `ASTRA: review + reconsider`

Stale state, unexpected output, partial execution, or unresolved semantic choices stop the batch and return to Astra rather than silently closing or abandoning the task.

## Minimal receipt position

The researcher argues for the smallest familiar artifact rather than a new certificate framework.

Suggested hot representation:

- operation/bound action;
- before/after state identity;
- actual check results;
- explicit unchecked obligations;
- exact evidence handle.

Expanded provenance can remain cold/retrievable.

Important trust boundary:

- hashes identify bytes;
- check success certifies only the declared predicates;
- neither establishes semantic correctness, requirement completeness, or dependency completeness.

Receipts may help delegation, but they are not yet proven to save Astra work and can themselves become an abstraction tax.

## Deployment warning

**CONDITIONAL:** A thin skill can invoke a local Engine operation only if the host coding application exposes enough control to batch the deterministic mechanics. A custom harness does **not** prove that the same savings are deployable through the native skill/application boundary.

The proposal assumes no ability to rewrite platform history, intercept every result before ingestion, control hidden reasoning, or suppress mandatory platform continuations.

## Hostile counterexamples

### 1. Authentic mechanical PASS, semantic failure

A patch passes narrow tests but violates a real contract. Example: a parser passes ASCII checks but wrongly lowercases case-sensitive identifiers.

**Required behavior:** Astra still gets a semantic review turn and can reject/repair despite a mechanical PASS.

### 2. State/dependency drift

Requirements change after the decision, or an undeclared environmental dependency changes behavior while declared hashes remain valid.

**Required behavior:** reject known stale bindings; do not claim complete dependency knowledge; retrieve new evidence and return semantic ambiguity to Astra.

### 3. Partial side effect and retry

A command produces a real side effect and crashes before success is recorded.

**Required behavior:** journal started/completed actions, reconcile uncertain effects, and do not blindly replay.

## Conditional economics

For the supplied Astra coding control:

- control input = `98,251`
- 80% input ceiling = `19,650.2`
- control output = `1,464`
- 80% output ceiling = `292.8`

Against the reported Helix coding candidate (`127,397` input / `1,371` output), reaching 80/80 would require net removal of:

- `107,746.8` input tokens;
- `1,078.2` output tokens;

while holding task requirements and reasoning effort fixed.

Define candidate accounting conceptually as:

`I' = 127,397 - R_i + A_i`

`O' = 1,371 - R_o + A_o`

where `R` is safely removed model work and `A` is added receipt/review/escalation/recovery cost. All four quantities are **UNKNOWN** until measured.

The first reported Helix coding charge (`19,748`) already exceeds the entire 80%-input allowance (`19,650.2`) under an unchanged-first-charge intervention. This is conditional arithmetic, not a causal attribution to bootstrap and not a model lower bound.

## One discriminating experiment

The researcher recommends a **PATCH REVIEW** experiment rather than immediately claiming autonomous repair qualification.

### Offline first

Build a local fixture with:

- explicit contract;
- proposed patch;
- narrow mechanical tests;
- an independent semantic requirement checker;
- stale-state case;
- undeclared-environment/dependency perturbation;
- crash/partial-effect recovery case;
- exact retrieval checks.

No frontier calls until fixture semantics are proven offline.

### Native comparison

Use:

- one matched valid A/B pair;
- two candidate safety challenges: stale preimage and authentic mechanical PASS over a contract-violating patch.

Both valid arms receive equivalent:

- proposed patch;
- initial task evidence;
- tools;
- required checks;
- reasoning setting;
- mandatory semantic-review opportunity.

Boundary A executes separately; Boundary B batches deterministic mechanics. Neutral identifiers should avoid leaking which adverse case should fail.

The adverse arms are safety challenges, **not** savings replicates.

### Stop criteria

Reject the tested design on:

- unauthorized execution;
- stale application;
- missed semantic violation;
- duplicate side effects;
- denied evidence or review.

Safety plus lower input/output in the valid pair is an economic signal only, not general parity.

The missing next evidence after PATCH REVIEW is autonomous repair generation from equivalent unsolved context.

## What not to build

The dossier explicitly recommends **not** building yet:

- a new agent opcode language;
- a signature/certificate ecosystem;
- an automatic completion framework;
- a replay router;
- broad new abstraction layers.

It prefers familiar artifacts—patch/diff, exact evidence, mechanical status, unresolved obligations—until the boundary itself is falsified or supported.

## Final recommendation

**INFERRED:**

> Delegate the sequence, not the conclusion.

The smallest plausible deployable change is one authorized **apply-and-check** composite operation followed by ordinary Astra review.

Move predetermined mechanics out of Astra’s execution loop, but preserve Astra’s opportunity to inspect the resulting state, discover that its own patch is wrong, and revise it.

This is intentionally more conservative than exception-only continuation. The research argues that the expensive review turn may contain real self-correction and therefore should not be removed until independently shown safe.
