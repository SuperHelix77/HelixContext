# Helix skill, engine and HUD direction

Status: user requirements captured; telemetry contract and HUD implementation pending.

Related: [Helix Memory and Reducers roadmap](2026-09-09-memory-and-reducers-roadmap.md), extending the shared evidence store and accounting contract.

## Two coordinated fronts

Helix Context is the user-facing skill and engine entry point. Keep its resident instructions small: select sufficient evidence, preserve workflow obligations, and invoke applicable engine capabilities through a versioned interface. Engine availability and interface compatibility must be checked; a missing or inapplicable engine preserves native execution. Skill activation alone must not be presented as proof that engine interception or compaction restoration is working.

The engine owns deterministic evidence storage/retrieval, checked named plans, dependency validation, receipts and accounting. The skill retains semantic applicability and task-correctness decisions. Measure skill-only and skill-plus-engine interventions against the same native baseline, including bootstrap and recurring overhead. Separate savings cannot be added or multiplied without a joint measurement.

## HUD design brief

Apply Huashu Design to the visual direction, information hierarchy and interactive prototype. Build the production data adapter separately from the design skill. Start from repository evidence and available brand assets; do not invent results or create decorative statistics.

The first screen answers: **What did Helix save, what did it cost, and what did it change?**

Priority views:
- Native baseline versus Helix input/output, absolute deltas, sample counts and confidence class.
- Cost components with explicit units: tokens, latency, tool calls, preprocessing, read/retrieved bytes and retained storage.
- Model-specific policy and bypass decisions with supporting receipt references.
- Hot/cold evidence, retrieval amplification, immutable references and stale/tampered states.
- Named-plan attempts, individual step outcomes, reuse and measured break-even status.
- Peer transitions and dependencies, compaction restoration/ACK health, and actionable alerts.
- Efficiency frontier with comparable cost units, task success and uncertainty. Do not display universal capability parity from bounded tests.

Unknown, unmeasured, stale, contaminated and failed states must remain visibly distinct from zero and success. Every measured summary should drill down to its authoritative receipt. Plan execution success must remain distinct from semantic task success.

## Architecture and release order

1. Complete and verify the named-plan execution and accounting contract.
2. Freeze a versioned telemetry contract: event identity/cursor, producer, timestamps, model/policy identity where known, evidence references, outcome, units and measurement provenance. Define replay, duplicate handling, missing data and schema compatibility.
3. Connect the skill through a small documented engine interface; test fallback and restoration behavior without overstating platform coverage.
4. Produce a Huashu HUD prototype using a deterministic projection of authoritative events; label any fixtures explicitly.
5. Verify visual layout, keyboard access, interactions, source drill-down and stale/disconnected states before production wiring.

Engine → append-only telemetry → deterministic HUD. Opening or refreshing the HUD uses zero inference calls and never asks agents for status. Reading an event stream may incur ordinary I/O, which remains part of accounting. Routine rendering cannot trigger the optional model-based Analyze action.

Read-only by default. Later controls such as invalidating a plan, activating a strategy or retrying retrieval require explicit user action, scoped authorization and a durable provenance-bearing result. Do not implement mutation controls before their engine contract exists.

Telemetry semantics are determined by execution and scientific accounting needs. UI requirements must not weaken or reshape the research gates.
