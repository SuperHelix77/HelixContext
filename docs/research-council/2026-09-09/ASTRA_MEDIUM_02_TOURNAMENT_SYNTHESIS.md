# Astra Medium 02 — tournament synthesis intake

**Status:** FROZEN INTAKE ARTIFACT — planning/synthesis, not independent experimental replication  
**Date received:** 2026-09-09  
**Source artifact:** `helix-llm-cost-research.zip`  
**Archive SHA-256:** `6e6d3d697f05906da7f24d33824f6e1c090ed1553fb87405acc6df92b868e4a6`  
**Primary research source:** `src/App.tsx`  
**Primary source SHA-256:** `510eec0295dcf9768b9b9fcf8eedc4d69b600b21d10d3e2f02a345279a85a460`  
**Primary source size:** 40,300 bytes

## Evidence discipline

This intake must **not** be treated as an independently completed five-cell research tournament. The supplied application repeatedly states that it is a local research/planning workspace, that no independent model runs were performed, that supplied percentages are reported/unverified observations, and that telemetry/monetary cost are unknown. Its value is therefore architectural decomposition, falsifier design, and hypothesis triage rather than new empirical evidence.

All performance numbers below are inherited from supplied Helix observations and remain subject to repository receipts and later adjudication.

## Executive synthesis

Astra Medium 02 converges on the same central architecture shift as the other council lanes:

> **Reduce model work by changing computation placement, not merely by shortening its representation.**

The proposed end-state boundary is:

`Model decides -> Helix Engine executes -> independent checker verifies`

The model should see exact relevant evidence, changed dependencies, explicit assumptions, scoped receipts, and unresolved semantic questions. Deterministic assembly, hashing, bookkeeping, replay, publication, and already-specified checks should remain outside the model. Persistent cognition should store auditable decisions, assumptions, dependency graphs, invariant definitions, content-addressed artifacts, and continuations — not hidden chain-of-thought.

## Cell 1 — cost bounds / impossibility analysis

### Thesis

Native savings are bounded by the **removable share** of each token axis, not by local payload compression. Fixed instructions, novel semantic decisions, and required semantic verification form a workload-dependent floor.

### Conditional bound

For each axis `a in {input, output}` the dossier proposes the accounting form:

`S_a <= R_a - H_a - Q_a`

where:

- `R_a` = removable baseline share,
- `H_a` = native Helix overhead,
- `Q_a` = reconstruction cost induced by the intervention.

Therefore an 80% target requires, at minimum:

`R_a >= 0.80 + H_a + Q_a`

on **both** axes.

This is a conditional accounting bound, not a measured Helix theorem.

### Recommended falsifier

Instrument one representative native trace, partition observable input/output into disjoint cost categories, leave ambiguous attribution as `UNKNOWN`, and compute an oracle-removal ceiling **before** testing another intervention.

### Keep

- provider-native token counters,
- exact-source evidence,
- deterministic execution,
- honest native controls.

### Kill / deprioritize

- byte-to-billing-token estimates,
- inferring hidden reasoning categories from surface behavior,
- treating relocated CPU work as free.

### New ideas

- per-axis oracle-removal bound,
- reconstruction-tax ledger,
- workload-specific native-bypass threshold.

## Cell 2 — systems transfer

### Thesis

The reusable unit should be a **dependency-tracked decision artifact / explicit contract**, not a generic summary and not hidden reasoning. Validated deterministic work can be reused without replaying the entire procedure only when dependencies are explicit and invalidation is conservative.

### Key transfer mechanisms

- partial evaluation of deterministic workflow steps,
- dependency-certified semantic views,
- typed continuations with explicit exception exits,
- prepared cognition / prepared procedure artifacts,
- content-addressed evidence and caller-owned state.

### Critical caveat

Warm reuse is not evidence of cold-start savings. Reuse wins only when avoided native recomputation exceeds setup + invalidation + retrieval + exception-handling cost.

### Recommended falsifier

Freeze one typed procedure and dependency graph. Then:

1. change one declared input and verify only invalidated work is recomputed;
2. change one **undeclared semantic assumption** and verify the system fails closed rather than reusing stale cognition.

### Kill / deprioritize

- generic cold named plans,
- unchecked semantic caches,
- broad framework integration before a single-procedure falsifier.

## Cell 3 — Helix-Astra phenotype

### Thesis

Astra may safely delegate **mechanical** verification only when a receipt makes its scope, trust boundary, checked predicates, and unverified obligations explicit. Semantic caution stays model-side.

A hash binds bytes; it does **not** prove that the selected bytes answer the task.

### Proposed Astra receipt surface

A compact receipt should include enough to identify:

- immutable input/evidence references,
- verifier identity/version,
- procedure identity/version,
- output identity/hash,
- checked predicates/invariants,
- unchecked obligations / scope limitations,
- status,
- exact retrieval escape hatch.

### Smallest Astra falsifier

Use one exact-source assembly task with:

1. a valid receipt,
2. a stale-dependency receipt,
3. a semantically wrong but correctly hashed selection.

Astra should:

- accept/reuse the valid mechanical checks,
- reject stale state,
- still catch the semantically wrong selection,
- retain exact-source retrieval when confidence is insufficient.

### Failure condition

If Astra reconstructs the checker, rereads all evidence, or performs equivalent verification despite a valid scoped receipt, the proposed receipt is not sufficient to reduce native model work.

## Cell 4 — Sol composition

### Supplied observations

- exact/request-conditioned evidence: approximately `49.6%` input / `50.0%` output saved;
- caller-side deterministic completion: approximately `67.3%` input / `71.9%` output saved.

These values are inherited reported observations, not new Astra Medium 02 measurements.

### Thesis

The mechanisms may remove overlapping work. Residual percentages cannot be multiplied as though independent. The illustrative `83.5% / 86.0%` arithmetic is explicitly rejected as a prediction.

### Recommended experiment

A randomized paired **2x2 factorial**:

- native control,
- exact evidence only,
- caller completion only,
- combined exact evidence + caller completion.

Hold constant:

- task contract,
- held-out fixtures,
- model/version,
- reasoning setting,
- evidence availability,
- parity checks,
- accounting boundary.

Meter all four arms end-to-end. This directly estimates interaction/overlap rather than inferring it from separate experiments.

### Keep

- model-owned semantic selection/final responsibility,
- deterministic exact rendering/assembly/validation at caller.

### Kill

- independence assumptions,
- development fixtures as final qualification,
- hidden caller-side semantic decisions mislabeled as deterministic work.

## Cell 5 — wild mechanism search

The artifact generated ten broad candidates and retained only three conceptual survivors:

### 1. Typed semantic decision IR

Model emits only unresolved semantic decisions; Engine performs deterministic mechanics.

Best initial phenotype: **Sol**.

Kill if the model must regenerate integration/glue or inspect Engine implementation to use the IR.

### 2. Dependency-certified continuations

Carry forward explicit state, completed work, dependencies, invalidation conditions, and exception exits so repeated workflows do not rebuild state from history.

Best initial phenotype: repeated, stateful workflows.

Kill if hidden/undeclared dependencies make stale reuse common or conservative invalidation erases the savings.

### 3. Independently checked verification receipts

Move repeatable mechanical checks into Engine/checker and expose compact scoped results to the model.

Best initial phenotype: **Astra**.

Kill if receipt interpretation, trust establishment, or semantic reinspection consumes the removable share.

### Seven concepts explicitly deprioritized

- LLM-generated memory summaries — memory-creation tax / reconstruction risk;
- token codebooks — decoding/interface overhead;
- cold generic macros — integration overhead;
- speculative branches — wasted model calls;
- lossy evidence — parity risk;
- cryptographic-only trust — integrity is not semantic correctness;
- universal routing policy — model-phenotype mismatch.

## Model-specific phenotype synthesis

### Sol

Prefer:

- compact exact evidence,
- tiny semantic decision IR,
- caller-side deterministic completion,
- minimal integration surface,
- factorial interaction measurement before claiming component composition.

### Astra

Prefer:

- explicit scope-bearing verification receipts,
- exact provenance,
- explicit unchecked obligations,
- independent checker,
- semantic exception/retrieval path,
- no suppression of genuine model-side semantic validation.

### Luna

Prefer:

- rigid minimal ABI,
- no Engine-source discovery,
- no generic cold-plan abstraction,
- aggressive native bypass when expected setup/reconstruction exceeds removable work.

## Candidate architecture bet

The strongest architecture proposed by this artifact is:

1. **Model-visible input:** exact relevant evidence, changed dependencies, explicit assumptions, scoped receipts, unresolved semantic questions.
2. **Model output:** a small typed semantic decision / decision IR.
3. **Helix Context:** task-conditioned evidence admission with immutable raw-source escape hatch.
4. **Helix Engine:** tiny stable ABI such as `SELECT`, `RETRIEVE`, `APPLY`, `VERIFY`, `CONTINUE`, `EMIT`; deterministic mechanics remain caller-side.
5. **Persistent cognition:** auditable decisions, assumptions, dependency graphs, invariant definitions, artifacts, and continuations — no hidden CoT.
6. **Invalidation:** transitive dependency invalidation; unknown dependencies force review/native path.
7. **Verification:** receipts bind input/procedure/dependencies/output/checker/status/predicates to exact evidence and state only what was actually checked.
8. **Routing:** choose the cheapest validated route satisfying capability/risk/latency constraints, including native bypass.

### Cheapest architecture kill test

One held-out exact-source task, paired native vs typed-decision execution, plus a stale-dependency mutation.

Kill the architecture if any of the following occurs:

- parity loss,
- unsafe stale acceptance,
- model-generated glue/source inspection returns,
- receipt/reconstruction cost consumes the removable share,
- caller takes over a genuinely semantic decision.

## What Astra Medium 02 does **not** establish

It does not establish:

- new end-to-end native savings,
- monetary savings,
- independent replication of Sol/Astra/Luna results,
- completion of five separate independent research cells,
- a validated 75/75 or 80/80 architecture,
- that verification receipts will actually suppress Astra rechecking,
- that semantic-delta/continuation state will survive hidden dependencies.

Those remain falsifiable hypotheses for later council adjudication.

## Council relevance

This intake is valuable because it independently sharpens three recurring council concepts:

1. **semantic decision IR / computation placement**,
2. **dependency-aware continuations / prepared cognition**,
3. **scope-bearing verification receipts for Astra**.

It also contributes a particularly clean experimental recommendation: use a 2x2 Sol factorial to measure mechanism overlap directly rather than composing percentage savings arithmetically.
