# Centaur intake: a lifecycle boundary, not another model interface

Status: architectural proposal; no production policy activated; no new native inference.

## Verdict

**INFERRED:** take the separation of durable control from agent execution. Add a
Helix-specific, mechanically qualified transition gate **before optional context
construction**. A resolved ACK must not pay for retrieval, curation, or inference.
The gate must not attempt to infer semantic sufficiency from prose. Unknown cases
retain ordinary model execution and tools.

**OBSERVED:** Luna's W50 caller-state path removes 49 passive model turns. The
latest caller-coding attempt exposes a different problem: two pending caller steps
were placed in an `unresolved` array and the caller stopped before executing them.
An explicit recovery completed the exact artifact without another model call.
These are concrete reasons for a lifecycle contract. Neither establishes a safe
general-purpose semantic gate or normal-Codex-app deployment.

## Source boundary

Read first: [external-work ledger](EXTERNAL_WORK_LEDGER_20260909.md).
Pinned sources, inspected as external documentation, not execution replication:

* [Centaur README](https://github.com/paradigmxyz/centaur/blob/93c43ed87ce12f3b23df2816a97e24ef47509290/README.md).
  **EXTERNAL:** thin harnesses surrounded by durable workflows, execution and
  delivery state. Its team deployment and credential infrastructure solve a
  broader problem than this one-user Mac release.
* [Context README](https://github.com/bradwmorris/centaur-context/blob/fad460f10c280870b3b7629006ac37a2f8ed46d8/README.md).
  **EXTERNAL:** a separate companion application, not a built-in Helix component.
* [Context architecture](https://github.com/bradwmorris/centaur-context/blob/fad460f10c280870b3b7629006ac37a2f8ed46d8/docs/architecture.md).
  **EXTERNAL:** separate Curator and Context Builder, canonical objects with
  revision/provenance, immutable change events, and compensating updates. This
  suggests separating write-time state derivation from read-time context selection.
* [Context integration](https://github.com/bradwmorris/centaur-context/blob/fad460f10c280870b3b7629006ac37a2f8ed46d8/docs/centaur-integration.md).
  **EXTERNAL:** completed-interaction sink and pre-execution context hooks were
  tested in a maintainer fork, not untouched upstream at this cut. Curation has a
  separate model transport dependency. Optional context is reference data and
  fails open. This is not proof that equivalent callbacks exist in stock Codex.

No external project was installed or copied into Engine. Convergence is not
capability evidence, economic evidence, or proof of independent empirical replication.

## Measured residuals

| ID | Current native evidence | What it supports and does not support |
|---|---|---|
| L1 | [W50 V7](continuation-contract/LUNA_KERNEL_V7_RESULT.md): 1,082,542 → 15,905 input; 641 → 156 output; 49 ACKs preserved; one candidate segment | Caller-owned passive transitions are valuable on this fixture. Output savings 75.66%, not 80%; original control reused. |
| L2 | [Three-task suite](continuation-contract/LUNA_CAPABILITY_V1_RESULT.md): output savings −0.11%, −161.98%, −62.30% | General delegation kernel/skill is unqualified. Coding repeated registration; selection did not. No universal setup explanation. |
| L3 | [Caller coding](continuation-contract/LUNA_CALLER_CODING_RESULT.md): 73,074 input / 5,361 output, 4 segments; exact recovery without another call | Distinguish semantic obligations from mechanical steps. Registration rediscovery absent here, yet output regressed 52.09%. |
| S1 | [Council synthesis](EXTERNAL_COUNCIL_SYNTHESIS_20260909.md), Sol integrated V3: 88.10% input / 88.98% output; zero issued commands; uncached saving 65.10% | Caller mechanics can work. Headline is cache-sensitive; not generalized economics. |
| A1 | [Astra clause audit](continuation-contract/ASTRA_KERNEL_CLAUSE_HYPOTHESES.md): valid kernel arm added probes and cost; defective arm retained detection | Do not tell Astra to increase skepticism or erase semantic checks. Clause causation is unproved. |
| M1 | [Memory/reducer audit](continuation-contract/MEMORY_REDUCER_PARITY_AUDIT.md): exact memory recovery and typed reducers, incomplete functional parity | Preserve exact recovery; 18.68× historical recovery amplification is not an economic win. |

L1–L3 were reread for this adjudication. S1 and the recovery-amplification figure
are prior recorded findings, not independently rerun here. No hidden reasoning
contents or causal per-token semantic attribution are claimed.

## TAKE / DEFER / REJECT

TAKE means a design requirement, not permission to activate an unqualified policy.

| Mechanism | Verdict | Exact residual attacked; acceptance condition |
|---|---|---|
| Thin deterministic control plane | TAKE | L1 passive turns; L3 pending mechanics. Must eliminate resolved transitions without hiding semantic work. |
| Explicit completed-interaction sink | TAKE | L2 repeated registration/reconstruction risk. Stable completion facts must survive restart without model bookkeeping; native savings remain unmeasured. |
| Pre-inference Context Builder | TAKE conditionally | Repeated evidence loading in L2/L3. Run only after model route; no claim that extra retrieval reduces the existing four coding segments. |
| Semantic-transition gate | TAKE, research qualification only | L1's 49 turns; L3's false semantic stop. Only registered exact transitions; unknown or semantic cases invoke model. |
| Separate Curator/write and Builder/read | TAKE | Avoid paying history reconstruction every read; M1 recovery traffic. Deterministic curation first; no routine extra LLM call. |
| Durable state/replay | TAKE | L1 continuity and L3 caller obligations. Replay must recover committed steps, not regenerate them or duplicate effects. |
| Immutable events/compensation | TAKE | Existing epoch/CAS invalidation correctness; stale replay could erase savings through recovery or corrupt workflow. No new measured token delta attributed. |
| Idempotent ingestion | TAKE | Re-delivery must not duplicate registration/state, grow context, or rerun L3 publication. This is a correctness precondition, not measured savings by itself. |
| Optional-context fail-open / execution fail-closed | TAKE | Avoid converting M1 retrieval failure into model setup work while retaining semantic authority. Required evidence failure is not optional-context failure. |
| Small provider-neutral contract | TAKE at schema level | Avoid per-model infrastructure discovery seen in L2. Implement only verified Codex adapter first; other harness adapters DEFER. |
| Automatic semantic Curator | DEFER | No measured amortization against saved turns; adds inference and invalidation burden. |
| Embeddings/graph ontology/new memory service | DEFER | No dominant residual requiring them. Existing deterministic exact retrieval remains available. |
| Credential/sandbox orchestration | DEFER | No demonstrated reduction of present model work; retain current permissions. |
| Broad tool registry/team/Slack/deployment parity | REJECT for v1 | No relevant measured residual; integration tax would increase. |
| Mandatory Kubernetes/Postgres/full Centaur deployment | REJECT for v1 | Local SQLite and content-addressed files suffice for proposed slice. |
| Fixed external packet limits | REJECT | Model/task economics and required evidence determine loading; do not truncate necessary evidence to fit arbitrary bounds. |

## Minimal proposed lifecycle API

One local library/service contract; names are proposed, not new model-facing tools.
All requests include schema version, task ID, event ID, policy release, expected
state root and authorization scope. Receipts include implementation/checker IDs,
exact input/output roots, checked predicates, unresolved obligations, and costs.

```text
prepare(event, expected_state) -> bound_state | stale | unavailable
route(bound_state, event, qualified_transition) -> ENGINE | MODEL | NATIVE | HOLD
build_context(bound_state, unresolved_request, budget) -> packet | optional_failure
execute(transition_id, bindings, authorization, idempotency_key) -> receipt | delta
complete(interaction_id, payload_hash, exact_evidence_refs) -> committed_state
recover(task_id, expected_epoch) -> verified_state | refresh_required
```

`route` is a finite contract check, not a semantic classifier. It consults existing
admission before optimization preparation. Current `engine/prototype/admission.py`
defaults production to native and validates exact research cells; do not silently
broaden that qualification to similarity matching or arbitrary tasks.

`complete` records observed outcomes even when tasks fail. It never labels failed
execution successful. Same identity + same payload returns the existing receipt;
same identity + different payload is a conflict. A stable identity includes harness,
thread, turn and interaction revision; task-local random IDs alone cannot dedupe
redelivery across restart. Use an explicit revision for a correction.

## Transition state machine

```text
INGRESS -> ADMISSION
  unqualified -> NATIVE (no Helix preparation)
  qualified -> BIND
BIND
  unavailable optional memory -> continue without optional packet
  stale/conflicting authority or missing required evidence -> REFRESH/HOLD
  bound -> GATE
GATE
  unknown event / unresolved semantic obligation -> CONTEXT -> MODEL
  authorized, exact registered transition, no semantic obligation -> ENGINE
  fully completed, delivery pending -> OUTBOX DELIVERY
ENGINE
  dependency change before effect -> REFRESH/HOLD (no effect)
  expected checked outcome -> COMMIT -> GATE or DELIVERY
  failure / unexpected delta / uncovered obligation -> MODEL with exact delta
  uncertain external effect -> RECONCILE (never blind replay)
MODEL
  decision + artifact + explicit obligations -> BIND -> ENGINE or MODEL/HOLD
DELIVERY -> idempotent COMPLETION SINK -> durable state
```

The “no semantic obligation” predicate must come from a qualified workflow contract
and the model's explicit authorized decision, not merely an empty JSON field or
successful tests. Silence is not authorization. Free-form user input is semantic
by default. Even an ACK-looking message may revoke consent or add a constraint;
only an authenticated typed passive event in a frozen workflow can use the ACK path.

Task state separates `semantic_obligations[]` from `pending_engine_steps[]`.
The latter names preauthorized typed operations with inputs and expected outcomes.
Never mechanically reinterpret arbitrary natural-language obligations, as the
one-off L3 recovery did for that particular receipt. Mechanical PASS does not prove
the patch solves the task, the tests are adequate, or the dependency list complete.

## State, memory and invalidation

Keep existing `workflow_memory.py` exact event storage/FTS retrieval and
`memory_epoch.py` immutable coverage manifests. Add no second canonical database.
Proposed task-state revisions reference those exact records plus their parent root.

| Category | Write-time Curator | Read-time Builder | Invalidation/recovery |
|---|---|---|---|
| Raw episodic evidence | Archive exact received bytes and provenance | Exact references/ranges | Corruption blocks exact-use claim; epoch recovery, no summary substitute |
| Procedure/progress | Deterministically reduce committed events | Pending steps and receipts | Procedure/executor version change invalidates applicability |
| Semantic conclusions | Record explicit model decision as a claim, with dependencies and open obligations | Only currently applicable claims, marked as claims | Changed dependencies/contradictions mark stale; model refresh, not automatic reaffirmation |
| Unresolved questions | Preserve explicit open/closed events | Supply relevant unresolved decisions | Closing needs authority/evidence; silence cannot close |

No chain-of-thought storage or regeneration. No inferred personal knowledge written
as fact. Curation is deterministic projection of explicit outputs initially; an
optional future learned curator would require separate cost and correctness gates.

Reuse invalidates on task/contract, authority, repo inputs, skill/policy, executor,
checker, dependency version, permissions or epoch changes relevant to the step.
Unknown dependency closure means not reusable. Bind input snapshots or use atomic
CAS checks at publication; a preflight hash alone is not TOCTOU protection.

Append-only events have sequence, previous root, payload root and revision. Update
materialized views transactionally. A failed index/reducer must not partially
publish workflow state. Compensating events preserve history; they do not undo
external effects magically. Prepared/committed records plus an outbox permit
restart recovery, but exactly-once external side effects need idempotent targets
or explicit reconciliation. Existing record dedupe is not an exactly-once executor.

Existing FTS validation and cold recovery can read substantial archived bytes.
Measure indexing, validation and recovery separately; do not optimize away exactness
to hide amplification. Optimize that path only when actual workload cost dominates.

## Normal Codex app boundary

**UNKNOWN:** the current inspected implementation does not establish a supported
stock-app callback that can suppress a user-triggered model invocation, finish its
transition and deliver the result with zero inference. The research `Session`
caller can do this because it owns invocation; a skill cannot claim that authority.

Current [interception evidence](../../engine/interception/README.md) includes native
truncation, failed end-to-end packet recognition and prototype hooks. It does not
demonstrate a pre-inference semantic gate. A memory lead pointing to a separate
native interception audit was not present in this checkout and is not used to
upgrade the result. Post-tool observation is already too late to remove that call.

Deployment contract: caller adapter handles ingress/authorization/registration and
capability discovery once; Helix Context supplies task-specific model policy and
evidence semantics; Engine owns exact mechanics/state. Astra/Luna/Sol see relevant
task evidence, pending semantic questions and compact results, retain ordinary
tools and may request exact evidence. They do not inspect Engine source or repair
registration. Avoid telling them to increase or decrease normal semantic scrutiny.

For the ordinary app, first verify a supported completion/observation adapter with
stable identities and user-approved hook configuration. If no pre-inference gate
exists, leave native invocation intact and display that limitation in HUD. A future
supported ingress/continuation callback is required for automatic turn suppression.
Do not substitute a special caller, credential proxy, binary patch or global prompt
change and label it normal-app integration.

## One smallest production slice

**RECOMMENDATION: idempotent task-local completion ingestion and state projection.**
Reuse current exact store to record thread-bound registration, completed operations,
pending typed caller steps and unresolved semantic obligations independently. Start
with passive observed records; no inference, automatic decisions or changed tool
outputs. Surface ingestion conflicts, replay and unverified delivery in HUD.

This directly addresses L3's contract confusion and L2's registration uncertainty.
The latest caller-registration receipt avoided rediscovery in L3, but did not save
output overall. Therefore this slice is a correctness/integration prerequisite with
**unproven net savings**, not an 80% production release. If attaching its state
does not remove repeated model work, keep it off the hot prompt. Production wiring
requires the verified completion boundary above; do not invent it. Do not implement
the whole proposed state machine before this slice passes its offline gates.

## Offline falsifiers before any native call

1. Replay all 49 authenticated W50 passive events: no model route; same ACK/state
   order. Insert a new constraint/revocation in otherwise similar text: model/hold,
   never deterministic ACK. Unknown event types must not use inference suppression.
2. Replay L3 with semantic obligations separate from assigned checks/publication:
   checks run before publish, failures hold publication, exact source unchanged.
   An actual semantic obligation must still request the model. This cannot repair
   the already-spent 5,361 output tokens.
3. Deliver completion twice, then restart and deliver again: one committed revision
   and one effect. Same ID/different bytes must conflict with no authoritative edit.
4. Crash before commit, after commit and before delivery ACK: replay reconstructs
   status, never repeats an uncertain external effect. No claim of exactly-once
   effects from local transaction success alone.
5. Mutate dependency after preparation and before publication: reject publication;
   stale epoch, changed policy and revoked permission similarly prevent execution.
6. Lose optional index: ordinary context path remains usable. Lose required exact
   evidence: retrieve verified epoch or hold. No guessed recovery from summaries.
7. Correct hashes with semantically inadequate patch: no gate may call that semantic
   PASS from checks alone. Preserve model decision/re-entry authority.
8. Measure instrumentation-only overhead, payload growth, logical reads/writes,
   storage, validation/recovery time and failed attempts before enabling hot state.

These are specified falsifiers, **not tests reported as passed in this intake**.
Existing L1 and L3 receipts supply replay cases, not proof of the general machine.
No expensive run is justified just to validate field names. The first later model
experiment must test a concrete removed-work prediction against a frozen control,
with semantic traps and all overhead charged.

## Migration and stops

* Luna: retain W50 V5/V7 as bounded research candidates. The broader three-task
  suite and caller coding fail economics; native bypass remains the default.
  Fixing obligation representation is useful, but not evidence for another output
  optimization lottery. See [Luna closeout](continuation-contract/LUNA_PHASE_CLOSEOUT_20260910.md).
* Sol: preserve V3 and its cache/fixture limits. Map its existing caller completion
  to lifecycle events without altering frozen prompts or retroactively rerating it.
* Astra: preserve semantic probes, including additional checks on valid tasks.
  No new kernel based on a claimed causal clause effect. Event receipts may remove
  established mechanics, never automatically close semantic adequacy questions.

Stop deployment on stale binding, duplicate effect, lost evidence, new out-of-scope
access, extra bootstrap/model turn, or capability regression. Stop optimization on
negative full-task economics. Unsupported cells bypass before preparation, whereas
already-started effects reconcile rather than restart natively. Include instruction,
model input/cached input/output, tool calls, CPU/latency, I/O, storage, recovery and
research/failed-attempt costs separately; unknown monetary conversions stay unknown.

**Answer:** Centaur's separation is a useful architectural precedent. Helix's
additional value would be deciding, under explicit mechanically qualified authority,
whether a call exists at all. W50 supports that on one workflow. The normal-app
ingress boundary and general capability/economic qualification remain unestablished.
