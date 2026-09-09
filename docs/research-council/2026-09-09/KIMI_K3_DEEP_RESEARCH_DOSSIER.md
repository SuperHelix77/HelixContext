# HELIX — Kimi K3 deep research dossier (frozen intake)

**Purpose:** preserve Kimi's repository-grounded Helix research findings as an independent council input before Arena/Astra cross-pollination.

**Researcher:** Kimi / K3 research lane  
**Evidence cut stated by researcher:** 2026-09-09, `Helix-Output` at `f0ab4aa`, with `helix/named-plans-v1` and `main` history  
**Imported source:** user-supplied `.webarchive`  
**Source SHA-256:** `dd36901a18b573063afcfd5e13784252bd39f5e80bf51e26c18e1210ce880509`  
**Clean Markdown extraction SHA-256:** `a7cde22516be38516ef5ada48a5ad1dad0d28ea7fbb21f3675991f4de550d5f7`

> This is a **frozen research dossier**, not a Helix decision. The claims below preserve Kimi's findings and labels. Later Astra/Helix adjudication must compare them against current repository receipts, including any results produced after this evidence cut.

---

## 1. Executive verdict

**INFERRED / OBSERVED-backed:** Helix's binding constraint is increasingly **computation placement**, not context representation alone.

Kimi identifies three recurring structural reasons why large local byte/payload reductions fail to convert into native end-to-end savings:

1. **The model reconstructs what Helix removes.** Luna's cold named-plan regression spent additional budget reading Engine source, regenerating integration glue, transcribing results, and re-verifying. The memory follow-up reduced input but induced additional terminal/reconstruction work and output.
2. **Short workloads have hard floors.** The repository's fixed-first-call analysis conditionally caps savings when the intervention happens only after the first call; output can also be floor-limited by reported reasoning tokens.
3. **The bill is not the bytes.** Tool-result compression and wrapper virtualization can be huge at the byte level while native model-token savings remain small or negative.

Kimi's preferred framing is therefore:

```text
MODEL
  -> novel semantic judgment

HELIX ENGINE
  -> deterministic execution
  -> exact copying / assembly
  -> bookkeeping / state
  -> hashing / provenance
  -> already-proved mechanical verification
```

The key principle is: **make the model think once; do not make it mechanically reproduce the same solution repeatedly.**

Kimi does **not** treat 80/80 as a universal target. Its recommended economic objective is to dominate native execution on workload classes where semantic work can be separated from deterministic mechanics.

---

## 2. Repository state reconstructed by Kimi

**OBSERVED, as of the stated evidence cut:**

- Evidence core: exact stdout/stderr capture, SHA-256 content-addressed objects, typed packet verification, transactional publication, exact-range retrieval, optional line indexes.
- Reducers: generic/pytest/compiler projections, intentionally partial, preserving omission references and raw evidence.
- Renderer: hash-bound copy plans and deterministic assembly.
- Caller completion: model returns semantic record IDs; caller validates and assembles the exact artifact.
- Named plans: immutable identity/version/hash, declared-input binding, TOCTOU checks, per-step receipts, stop-on-failure.
- Workflow memory: project-scoped lexical search, session labels, timeline fallback, exact retrieval, shared provenance.
- Interception adapter: hook/projection experiments with unresolved native-model delivery semantics.
- Skill contract: model should use supplied Engine results rather than inventing setup/registration work.
- HUD: read-only telemetry; no inference required.
- Accounting contract: model I/O, retrieval, preprocessing, storage, recovery and coordination should be counted; unknowns remain unknown.

Kimi explicitly notes that parent/coordinator usage, physical I/O and money pricing were not fully measured in the evidence cut.

---

## 3. Failure-history synthesis

Kimi verified the following reported Helix results against repository receipts available at its evidence cut:

| Mechanism / model | Result | Kimi status |
|---|---:|---|
| Sol request-conditioned exact evidence | ~49.6% input / ~50.0% output saved | **VERIFIED / OBSERVED** |
| Sol caller-side deterministic completion | ~67.3% input / ~71.9% output saved | **VERIFIED / OBSERVED** |
| Luna cold named plan | ~62.4% more input / ~43.9% more output | **VERIFIED / OBSERVED** |
| Luna memory/selective history | ~39.7% input saved / ~15% output regression | **VERIFIED / OBSERVED** |
| Astra exact evidence | ~25.7% input / ~38.6% output saved | **VERIFIED / OBSERVED** |
| Memory selective-payload fixture | ~98.5% payload-token reduction | **VERIFIED local result; not native savings** |
| Wrapper capture | 9.2 MB exact evidence -> ~2 KB packet | **VERIFIED offline; native mapping unresolved** |
| Named-plan execution overhead | millisecond-scale, but no favorable local latency break-even on medians | **VERIFIED with qualification** |

Additional preserved negative evidence cited by Kimi includes:

- invalid-grader/native-pilot failures;
- Sol/Astra render-pilot regressions;
- long-horizon policies where output increased substantially despite context compression;
- interception bridge failures under upstream truncation / null schemas;
- peer-event ACK failures;
- plan invalidation caused by metadata/ctime behavior.

**INFERRED synthesis:** the common failure skeleton is not "compression is impossible" but "the interface causes the model to reconstruct semantics, integration steps or confidence that Helix tried to omit."

---

## 4. Cost anatomy

Kimi refines Helix accounting into directly observable versus latent/bounded terms.

### Directly observable / measurable from receipts

- fixed platform / first-call context where receipt data exposes it;
- source/tool transit;
- Helix bootstrap, plan registration, preprocessing and validation;
- deterministic verification work when it appears explicitly in traces;
- storage / object traffic where measured.

### Latent or only conditionally identifiable

- semantic reasoning;
- reconstruction;
- procedural regeneration;
- confidence repair / re-verification motivation;
- coordination reasoning.

Kimi explicitly cites the repository's own non-identifiability logic: aggregate token counters do not uniquely identify latent internal causes.

A defensible Helix objective therefore has the form:

```text
achievable saving
    <= removable native-cost share
       - Helix overhead
       - reconstruction cost
```

with the intervention boundary always stated.

---

## 5. Why local savings disappear

**INFERRED from multiple observed failures:**

- representation reduction can trigger model-side reconstruction;
- generic interfaces can make models inspect Engine implementation details;
- compact evidence can cause extra discovery/verification if the model does not trust or understand the abstraction;
- reducers may save bytes that the native runtime would already truncate;
- first-call and reasoning floors can dominate short tasks;
- different models pay different "repair taxes" when the interface mismatches their behavior.

Kimi's model-specific reading:

- **Luna:** especially vulnerable to transcription, helper discovery, interface reconstruction and verification loops.
- **Sol:** responds well when semantic selection stays model-side and deterministic completion becomes caller-owned.
- **Astra:** likely pays disproportionately for provenance checking, source inspection and re-audit; this remains a phenotype hypothesis requiring a direct falsifier.

---

## 6. Strongest mechanisms Kimi recommends preserving

### 6.1 Semantic decision IR

The model emits only unresolved semantic decisions in a tiny typed representation. The Engine converts that IR into deterministic actions.

Examples of conceptual opcodes:

```text
SELECT
RETRIEVE
APPLY
VERIFY
CONTINUE
EMIT
```

**Targeted cost:** integration glue, mechanical completion, repeated procedure generation.

### 6.2 Prepared cognition

Store an externally auditable semantic artifact containing:

- assumptions;
- dependencies;
- invariants;
- deterministic steps;
- unresolved semantic decisions.

On reuse, supply only changed inputs, invalidated assumptions and new unresolved decisions.

Kimi explicitly rejects storing hidden chain-of-thought as the reusable unit.

### 6.3 State-diff / semantic-delta memory

Instead of replaying full task state:

```text
verified state N
+ delta
+ unresolved decisions
```

This is intended to attack both first-call history cost and repeated state reconstruction while preserving exact cold evidence.

### 6.4 Verification / provenance certificates

Especially for Astra, Kimi proposes compact receipts carrying mechanically checkable claims such as:

```text
input_hashes
artifact_hash
procedure_hash
dependency_set
checked_invariants
verification_scope
verifier_identity
supersedes
status
exact_source_refs
```

These certificates do **not** prove high-level semantic correctness. Their purpose is to give a strong model sufficient evidence not to reperform already-certified mechanical verification.

### 6.5 Model/task-specific ABI

The model should not need to inspect Engine source or generate glue. Different model phenotypes may need different surface forms over the same Engine semantics.

### 6.6 Caller-owned continuation state

Caller/Engine owns bookkeeping, progress, exact continuation identity, completed work and unresolved dependencies; the model sees only information requiring semantic judgment.

### 6.7 Semantic decision cache with content-addressed invalidation

Cache externally auditable decisions only while their dependency fingerprints remain valid. Stale dependencies invalidate reuse rather than silently reusing a decision.

### 6.8 Deterministic answer rendering

For fixed-schema / extract-copy-transform work, the Engine should emit the exact artifact from the model's semantic decision rather than asking the model to regenerate deterministic bytes.

---

## 7. Mechanisms Kimi deprioritizes

### Reducer expansion

Reducers remain useful infrastructure but are likely close to saturation as a primary native-token lever once tool bytes and generated command bytes are already heavily reduced.

### Generic cold named plans

The Luna evidence shows that a reusable abstraction can be economically disastrous when the model must discover, understand or integrate it during the task.

### Numeric alias/codebook recoding

Local syntax reduction can be overwhelmed by the codebook/input tax.

### Learned summarization / retrieval by default

Kimi recommends adding learned memory mechanisms only when a measured native-cost need justifies them; otherwise deterministic exact-source-backed memory remains the safer baseline.

### Automatic workflow caching without an initiation/invalidation rule

Reuse should be admitted only where the workload class and dependency state make reuse economically and semantically valid.

---

## 8. Conditional bounds / theorems highlighted by Kimi

1. **Targetable-share bound** — savings cannot exceed the native cost share actually reachable by the intervention after its own overhead.
2. **Fixed-first-call bound** — on the recorded post-first-call-only posture, 80% input/output was impossible because too much cost had already been spent before Helix could intervene.
3. **Reasoning-floor bound** — with reasoning output held fixed, visible-text compression alone cannot cross an output target below that reasoning floor. Kimi notes that reasoning tokens themselves can fall indirectly when evidence/mechanical work is reduced, so the bound is conditional rather than absolute.
4. **Joint-boundary rule** — independently measured component savings cannot be added or multiplied without accounting for overlap and interaction.
5. **Dual-budget amortization** — input and output must each amortize setup/validation overhead; winning one dimension does not certify the other.
6. **Delivery rule** — producing a compact packet has no value if the packet is not actually the model-visible representation used for inference.
7. **Memory first-call rule** — external memory reduces first-call input only when it replaces injected history rather than being added on top.
8. **Payload != native rule** — bytes, bytes/4 estimates and serialized-request token counts are not native receipt savings.

---

## 9. Hostile findings that survive

Kimi deliberately attacks the project and leaves several live threats:

- single-pair numbers may reflect baseline variance;
- caller-side completion may not preserve open-ended late discovery/recovery behavior;
- parent research, physical I/O and some deterministic CPU work remain outside a fully priced monetary boundary;
- model-specific phenotypes are development hypotheses, not production profiles;
- memory economics remain unresolved on long-horizon latent-relevance workloads;
- Engine integration can exceed savings when the interface forces model discovery;
- 80/80 remains structurally implausible for novel reasoning-heavy single-episode workloads under narrow/post-hoc intervention boundaries.

What Kimi says survives the hostile audit:

1. the **computation-placement thesis**;
2. the **fixed-first-call / reasoning-floor arithmetic** as conditional bounds;
3. the **Sol caller-completion direction** because savings, artifact correctness, latency and mechanism attribution aligned in that pair;
4. Helix's accounting discipline: preserved failures, explicit unknowns and refusal to equate payload reduction with native savings.

---

## 10. Kimi's recommended Sol experiment

**Name:** Sol Combined Pair

### Control

Ordinary Sol High with efficient scripting on a fresh fixture containing:

- latest-revision-per-group selection;
- supersession edges;
- strict-boolean eligibility;
- expiry edge;
- one stale-source event;
- one correction/recovery turn;
- exact-byte artifact + provenance obligations.

### Candidate

Same task with independently switchable components:

- A: request-conditioned evidence compiler;
- B: caller-side completion with original IDs;
- C: memory-statistics/caller ledger;
- cold named plans OFF.

### Measure

- native input/output/reasoning receipts;
- command counts and generated bytes;
- artifact exactness;
- source preservation;
- recovery-turn cost;
- elapsed time;
- caller-side compute/overhead.

### Success rule

Kimi recommends pre-registering success as **>=75% input AND >=75% output with all parity checks green**. A 70–75% knife-edge may justify one replication, but not an open-ended tuning loop.

### Economic decision

If Sol crosses the economic threshold with clean parity, **freeze Sol** and move serious research effort to Astra instead of chasing 80/80 for symmetry.

---

## 11. Kimi's recommended Astra experiment

**Name:** Astra Certified Receipts

### Hypothesis

Astra may repeat mechanical source/provenance verification because the current Engine interface provides insufficiently authoritative evidence.

### Control

Ordinary Astra High on a fresh diagnosis/repair task with efficient native tools and exact-answer obligations.

### Candidate

Same task, but every Engine-produced artifact carries a compact certificate including:

- artifact hash;
- input/source hashes;
- verification scope;
- checked invariants;
- verifier identity;
- supersedence / freshness state.

No Engine source is exposed for ordinary use. The caller revalidates digests deterministically. Missing/out-of-scope certificates force normal verification rather than trust.

### Primary phenotype measurement

Count commands/tool actions that re-read or re-audit already-certified material.

### Falsification

If Astra still performs the same mechanical re-audit within certificate scope and input cost regresses materially, the "mechanical trust anchor" hypothesis is weakened and richer semantic evidence may be required.

If Astra accepts an invalid/stale certificate, reject the mechanism immediately.

---

## 12. Stop / freeze criteria recommended by Kimi

- **Freeze Sol** after a clean >=75/75 paired result; a 70–75% result may be acceptable only after replication and explicit parity closure.
- **Stop Luna cold-interface research** once Sol becomes economically dominant for the same workload class; retain Luna only where latency/cost behavior gives it a real advantage.
- **Stop reducer expansion** unless a new adapter targets a measured native-token cost.
- **Stop native pairs** at pre-registered failure/overrun gates; preserve all negative receipts.
- **Promote to broader matrices** only after a single-model mechanism survives its smallest falsifier.
- **Do not treat 80/80 as universal** for novel reasoning-heavy workloads; route by workload class and effective cost instead.

---

## 13. Kimi's 48-hour execution order

1. **Freeze accounting, fixtures and Sol composition switches** without model calls.
2. **Run one Sol combined falsifier** and publish all component/ablation signs regardless of outcome.
3. **Build the Astra certificate layer** using existing provenance/verification primitives; offline-test tamper, stale scope, withheld-cert and fallback behavior.
4. **Run one Astra certified-receipt pair** with re-audit count as the phenotype variable.
5. **Freeze / redirect:**
   - Sol >=75/75 + parity -> freeze Sol and move frontier quota to Astra;
   - Sol 70–75 -> at most one replication;
   - Sol <70 or parity failure -> use attribution to identify the interfering boundary; no mechanism spree;
   - Astra directional success -> prioritize Helix-Astra as the recursive research-cost multiplier.

Kimi explicitly recommends **not** spending the window on new Luna mechanisms, more reducers, learned memory summarization, numeric aliases or a full 3-model matrix.

---

## 14. Terminal architecture recommendation

Kimi's preferred end state is an **aggressive placement router with conservative native bypass**:

```text
verified external state
+ semantic delta
+ unresolved decisions
        |
        v
      MODEL
  (novel semantic work)
        |
        v
semantic decision IR
        |
        v
 HELIX ENGINE
 (deterministic execution,
  exact evidence,
  verification,
  state continuation)
        |
        v
certified result / exact artifact
```

The system should optimize **where work executes**, not merely how many characters are present in context.

The economic target becomes:

> make the stronger model cheap enough that downgrading to a weaker model is unnecessary on validated workload classes.

---

## 15. Primary repository/external sources cited by Kimi

Kimi's dossier cites, among others:

- `README.md`, `FRONTIER_REPORT.md`
- `engine/CONTRACT.json`, `engine/README.md`
- `engine/LUNA_REGRESSION_ANALYSIS.json`
- `engine/output/SOL_CALLER_COMPLETION_RESULT.md`
- `engine/output/LUNA_COLD_PLAN_RESULT.json`
- `engine/prototype/MEMORY_NATIVE_FOLLOWUP.md`
- `engine/prototype/MEMORY_PAYLOAD_RESULTS.md`
- `engine/prototype/NAMED_PLAN_OVERHEAD.md`
- `engine/prototype/OUTPUT_FRONTIER.md`
- `engine/native-pilots/README.md`
- `engine/query-pilot-v2/README.md`
- `engine/render-pilot/README.md`
- `engine/interface-feasibility/RESEARCH.md`
- `engine/call-budget/RESULT.json`
- `engine/interception/README.md`
- `engine/behavior-study/THEOREMS.md`
- `engine/accounting/RATE_INDEPENDENT_AUDIT.json`
- memory/reducer and named-plan design/plan documents
- `skills/helixcontext/SKILL.md`

External research cited by Kimi includes RTK / JetBrains RTK evaluation, Claude-Mem documentation, MemGPT, hierarchical RL/options literature, SWE-agent, CodeAct, LongMemEval and Anthropic tool/code-execution engineering notes.

Kimi explicitly marks as **UNKNOWN / incomplete**: raw native traces retained only locally, some detailed result artifacts not fully visible in its working context, pre-publication development history, monetary pricing, physical I/O and parent/coordinator token totals.

---

## 16. Intake note for later council adjudication

This dossier predates later Helix results unless they are explicitly present in Kimi's evidence cut. In particular, later Sol Integrated V2/V3 findings must be treated as **new evidence**, not retroactively attributed to Kimi.

When Arena, the second Kimi lane and Astra dossiers arrive, the next step is **not** to merge recommendations. Build a disagreement matrix and identify:

- independently rediscovered mechanisms;
- direct contradictions;
- intervention-boundary disagreements;
- claims invalidated by newer receipts;
- the one or two falsifiers with the highest expected information gain per frontier-model token.
