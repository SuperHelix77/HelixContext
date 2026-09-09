# Helix external-work ledger — 2026-09-09

This ledger records external systems/research artifacts that may inform Helix. It does **not** promote external claims to Helix evidence. External systems are treated as architectural precedent or falsifier sources unless independently reproduced in Helix.

Labels used below:
- **EXTERNAL** — claim or implementation observed in another project.
- **OBSERVED** — directly inspected in the cited public repository at the pinned commit.
- **INFERRED** — Helix interpretation of the external evidence.
- **HYPOTHESIS** — proposed transfer that still needs a Helix falsifier.
- **DO NOT IMPORT YET** — not justified for current Helix release.

## 2026-09-09 — Centaur / Centaur Context

### Provenance

- `paradigmxyz/centaur` main pinned at `93c43ed87ce12f3b23df2816a97e24ef47509290`.
- `bradwmorris/centaur-context` main pinned at `fad460f10c280870b3b7629006ac37a2f8ed46d8`.
- Files inspected: Centaur `README.md`; Centaur Context `README.md`, `docs/architecture.md`, and `docs/centaur-integration.md`.
- No Helix code was changed from these repositories. No native model call was spent on this intake.

### External architecture observed

**OBSERVED / EXTERNAL:** Centaur is a self-hosted agent control plane. It keeps the agent harness thin and places durable state, workflows, sandbox lifecycle, credentials, replay, tools, and execution in a deterministic system around the harness. Existing harnesses such as Codex, Claude Code, and Amp can run inside isolated sandboxes rather than being replaced.

**OBSERVED / EXTERNAL:** Centaur stores messages, executions, events, and delivery state durably; supports long-running workflows that can sleep/resume; isolates credentials through a proxy; and treats each conversation as a controlled execution environment.

**OBSERVED / EXTERNAL:** Centaur Context is a separate shared-knowledge service beside Centaur. Its loop is:

`completed interaction -> Curator -> structured store -> Context Builder -> bounded relevant packet -> future agent`

The Context schema separates canonical objects, relations, provenance, artifacts, runs, and immutable change events. Retrieval combines text/optional semantic search and returns a bounded hot packet while exact source material remains retrievable.

**OBSERVED / EXTERNAL:** The proposed Centaur integration contract asks core for only two generic lifecycle hooks:
1. a completed-interaction sink; and
2. a pre-execution context provider.

The context packet is explicitly treated as untrusted reference data rather than reconstructed conversation history. Context failure is designed to fail open so ordinary agent execution remains available.

### Convergence with Helix

**INFERRED:** Centaur independently supports Helix's emerging separation:

`model = unresolved semantics`

`system = deterministic state / execution / credentials / persistence`

This is architectural convergence, not Helix benchmark evidence.

**INFERRED:** Centaur Context's Curator/Context-Builder separation resembles Helix's distinction between durable memory construction and active retrieval. Its hot bounded packet + cold exact source material is compatible with Helix's hot/cold evidence model.

**INFERRED:** Centaur's immutable event/provenance model is compatible with Helix's version-bound evidence, CAS publication, exact recovery, and fail-closed state transitions.

### Helix-specific distinction

**INFERRED:** Centaur decides how agent work is controlled; Helix additionally decides whether a frontier-model inference should exist at all.

Centaur's current lifecycle hooks answer:
- what to persist after an interaction; and
- what context to supply before an execution.

Helix requires a third conceptual boundary:

`semantic-transition gate(state, event)`

- If the transition is deterministic and fully bound, Engine performs it without inference.
- If there is unresolved/new semantic information, invoke the model.

This is the mechanism implicated by Luna's large savings from removing passive ACK/state-transition inference. A context layer alone would not remove those calls.

### Candidate transfers to Helix

**HYPOTHESIS — high priority architectural transfer, no dependency required:**
- Keep the harness thin; put durable orchestration above the model.
- Separate post-interaction curation from pre-inference retrieval.
- Keep exact evidence/provenance cold and recoverable while presenting a bounded active packet.
- Preserve explicit run/change history instead of silently rewriting state.
- Keep Helix bypassable for unqualified model/task/policy cells.

**HYPOTHESIS — future integration:** A Centaur-like control plane could eventually host Helix Engine as a cognition-placement layer and Helix Context as a memory/evidence layer, while continuing to use stock Codex/Claude harnesses.

### Do not import yet

**DO NOT IMPORT YET:** Kubernetes, Postgres, Slack ingress, team credential infrastructure, or Centaur itself as a mandatory Helix dependency. These solve team/control-plane problems but would materially increase the first Helix release's installation and operational surface.

**DO NOT IMPORT YET:** Centaur Context's fixed packet limits (for example its current object/character bounds) as Helix constants. Helix limits must be determined by measured model/task economics and capability tests.

**DO NOT IMPORT YET:** automatic curation/model calls unless their full setup, inference, retrieval, storage, and recovery cost is measured against saved model work.

### Research consequence

**INFERRED:** External convergence strengthens the direction but does not alter Helix qualification gates. Current priority remains:
1. finish and qualify the Luna phenotype;
2. characterize Sol/Astra from native traces rather than assuming a universal policy;
3. reproduce savings in the normal Codex app/runtime;
4. only then consider broader control-plane packaging or external-platform adapters.

### Verdict

**KEEP AS ARCHITECTURAL PRECEDENT. DO NOT MERGE OR DEPEND ON IT FOR THE FIRST RELEASE.**

Centaur is evidence that a deterministic control plane above existing agent harnesses is a practical design direction. Helix's distinct research contribution remains cognition placement: minimizing unnecessary model calls, context replay, mechanical reasoning, and output while preserving semantic authority and recovery.
