# Helix Memory and Reducers

Status: partially implemented research roadmap, 2026-09-09. The prototype implements portions below; this document does not qualify their performance or production integration. Continue the approved named-plan work; do not start another native sweep merely because the roadmap expanded.

## Source findings

- [RTK upstream README](https://github.com/rtk-ai/rtk#readme) describes command-specific output filtering, up to 90% Bash-output reduction, and bytes/4 token estimates. That is neither tokenizer measurement nor whole-task billing evidence. Its integration table lists Claude Code PreToolUse hooks but Codex AGENTS.md/RTK.md instructions. Do not infer a working Codex interception point from another host's integration. Small-output bypass is a Helix requirement here, not a verified claim about every RTK adapter.
- [Claude-Mem upstream README](https://github.com/thedotmack/claude-mem#readme) describes persistent observations/summaries, AI compression, SQLite/search and progressive disclosure: compact search results, neighboring timeline, selected full observations. Its observation references do not establish Helix's proposed exact-raw-byte guarantee. This review does not establish that Claude-Mem lacks other provenance mechanisms.

These are upstream documentation observations, not an implementation/security audit. Build native equivalents around Helix's existing store; no upstream installation, dependency or source copying is proposed. The coordinator's workload savings ranges remain hypotheses, not forecasts supported by Helix measurements.

## Current local gap analysis

`engine/prototype/evidence.py` already captures raw streams and produces bounded generic/pytest/compiler projections. `verification.py` independently checks declared structural invariants. `line_index.py` and batched retrieval support exact expansion. Extend these surfaces instead of introducing another archive.

`workflow_memory.py` now provides project-scoped lexical search, session-labelled events, timeline, exact retrieval and exhaustive replay. `frozen_search.py` provides an explicitly pinned immutable literal-search generation. `jsonl_extract.py` extracts verified matching text lines without exposing whole matching JSONL records. These are explicit caller APIs, not automatic interception or a complete request-conditioned history compiler. Named plans provide immutable registration, checked execution and explicit input rebinding under a new version.

Remaining gaps include automatic authorized observation capture, branch/authority/supersession semantics, verified compaction restoration, a conservative command-adapter registry, and measured admission policies. Session labels alone do not establish session access isolation. Existing infrastructure does not establish universal recoverability in practice or semantic sufficiency of projections.

## Current evidence and next integration gate

The prototype suite was re-run at code commit `589c438`: **154 passed**. These are infrastructure tests, not model capability certification.

- The [native memory follow-up](../../../engine/prototype/MEMORY_NATIVE_FOLLOWUP.md) reduced input 39.73% but increased output 15.01% against its retained control. Both task artifacts passed exact checks; this exploratory comparison failed the joint savings objective.
- [Frozen search](../../../engine/prototype/FROZEN_SEARCH.md) lowered measured application object traffic over repeated fixture queries after including index construction. It still reads the index/catalog, incurs rebuild cost and does not demonstrate native-token savings.
- Plans preserve declared workflow steps but measured local execution overhead remains positive. Creation, validation, recovery and reuse must be charged before promotion.

Integrate through a caller-owned Helix Context capability packet: available API/schema versions, project scope, evidence generation, active plan reference and current obligations. Only advertise capabilities the caller actually supplied. A model searching for nonexistent helpers adds cost and is not successful integration.

Use one durable evidence store for Memory, Reducers and Plans. A command runs once; reducers operate on that captured result. Memory indexes its receipt and exact source references. A later retrieval must be charged both for engine work and any model-visible expansion. Output retained in future conversation history is shared between mechanisms: savings attribution requires ablations, not summed percentages.

Before another native experiment, freeze a bounded workflow with an equally efficient ordinary-tool control, deterministic exact checks, required tool obligations, late relevance and recovery cases, and explicit startup/reuse boundaries. Count all model calls, skill/bootstrap tokens, retries and generated setup. Report input and output separately, with cached categories kept separate from billing claims. Unknown costs remain unknown. Only then expand a qualifying policy to the requested Luna/Sol/Astra task matrix.

## Helix Memory contract

Use the same immutable evidence objects with a rebuildable deterministic index. Start with lexical/structured search; add embeddings or generated summaries only after measured benefit covers their creation and maintenance cost.

Records bind project identity, session/branch scope, event ID, source hash and exact range, event type, observed time, producer, authority class and supersession links. Distinguish observations, accepted decisions, unresolved hypotheses and rejected hypotheses. A failed hypothesis needs its tested scope and falsifier; it is not a permanent universal prohibition.

Expose compact search, neighboring events and batched exact retrieval. Index summaries are navigation aids. Validate original evidence before consequential reuse. Missing/corrupt evidence is an explicit failed retrieval, never an empty successful result. Search misses mean no match found, not proof a fact never occurred. Preserve an exhaustive source/timeline fallback so lexical mismatch cannot silently erase latent relevance.

Capture only authorized workflow surfaces. Project filters are enforced before results are returned; cross-project reuse requires explicit scope. Retrieved text remains source data, not new instructions. Retention exclusions or deletion must be visible and invalidate recoverability claims for the affected range.

For compaction recovery, publish a small versioned capsule containing objective, active constraints, unresolved obligations, active skill identities/hashes, evidence cursor and references. Restore and validate against current authority and files; acknowledge the restored version. Do not re-inject every skill body or treat a stored ACK as proof a new instance loaded it. Capability detection must distinguish automatic host support from an explicit skill bootstrap.

**First-call boundary:** external memory saves initial input only where the caller can omit the corresponding historical text before inference. A search performed after the model has already received that history does not recover the sunk input cost. Platform-supplied context outside Helix's control stays in the fixed-cost term.

## Helix Reducers contract

Select adapters by parsed argv, supported options, executable/format version and environment assumptions. Never rewrite arbitrary shell strings by regex. Unknown syntax, compound commands, unsupported formats or insufficient expected gain use native execution. A presentation wrapper should preserve the command's behavior and raw output; changing flags or substituting a command is a separate equivalence obligation.

Execute once. Archive stdout/stderr exactly and retain exit/signal/timeout status. Reducer failure falls back to the captured raw result or explicit exact retrieval; it must never rerun a possibly side-effecting command to obtain native output.

Candidate adapters: git status with machine-readable parsing, git diff with hunk/source provenance, rg structured matches, then stronger pytest/compiler parsing. Preserve unusual filenames, renames, binary evidence, Unicode and invalid bytes. Counts must identify whether they cover all records or only a projected subset. Preserve omission references and mark malformed/unknown records explicitly.

Use independent checks of source spans, counts and statuses before accepting a packet. Small-output admission compares complete visible packet plus retrieval overhead against native output. A byte comparison is an initial screen, not proof of token savings. Keep unknown cost unknown and bypass where evidence does not justify activation.

## Shared integration and accounting

Helix Context remains the entry point for Memory, Reducers and Plans, with a compact capability/version handshake and native fallback. Reuse caller-owned ledgers and archives. HUD rendering consumes the same append-only events; it neither queries agents nor invokes a model routinely.

Account separately for input/output tokens (including cache categories where supplied), indexing/summarization, storage duplication, reads/hashing, retries, restoration, hooks, tool calls and latency. Compare cold-start and amortized runs. Do not sum time, bytes and tokens into one cost without explicit conversion rates. Mechanisms overlap through future history; attribute by measured ablations rather than adding percentages.

## Gates and sequence

1. Complete named-plan correctness/accounting and freeze shared receipt/event identities.
2. Add memory index and retrieval contracts plus scoped restoration fixtures; extend existing reducers with conservative adapter dispatch. Work can be isolated by module after the shared contracts settle.
3. Offline falsifiers: turn-1 random detail becomes decisive at turn 40/50; query uses an alias absent from the original; conflicting/superseded decisions; branch collisions; missing/tampered sources; crash/restart and duplicate events; failed ACK; unsupported command format; rare filenames; nonzero exit; failed reduction with exactly one underlying execution.
4. Test projection completeness for each declared schema and exact source recovery independently. A fixture pass qualifies infrastructure only.
5. Freeze model-specific policies and a bounded paired experiment before any new native calls. Compare native, skill-only, each mechanism and combined behavior on matched tasks; use offline evidence to limit unnecessary arms. Keep development selection separate from fresh held-out evaluation. Include short bypass tasks, repeated workloads and latent-future-relevance cases, three tasks per model at minimum as requested; three pairs alone cannot establish universal parity.
6. Promote only when task correctness, tool obligations, recovery and workflow state are preserved within stated measurement uncertainty and complete costs improve. Report regressions and uncertainty; no forced 80/95% pass threshold.
7. Build the Huashu HUD over the frozen telemetry projection, with unmeasured values and confidence visibly distinguished.

No savings estimate in this roadmap is a new Helix result. Raw availability is necessary for recovery, but successful discovery and use of the right evidence must also be measured.
