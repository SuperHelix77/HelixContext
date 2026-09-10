# W50 with genuine semantic checkpoints

**HYPOTHESIS:** resolved event handling can fund several ordinary Astra semantic
checkpoints while retaining substantial input and effective-cost savings. It does
not make novel semantics free. This is a separate harder workload, not a replacement
for the frozen seven-cell cohort or a way to inflate its median.

## Evidence and the remaining question

**OBSERVED:** the full-final Astra High W50 V2 pair saved98.32% input but49.62%
output with50native turns versus one. The fresh [cold recovery pair](cold-native-final-v1/RESULT.md)
saved78.29% input/61.75% output with four segments versus one, ordinary tools and
complete model-written finals. The latter delegated exact extraction before
inference; it did not emulate unresolved reasoning.

**OBSERVED:** resident code-review evidence still produced four Astra XHigh
segments. Semantic probing and mechanics coexist in those traces. Four user
checkpoints therefore cannot be assumed to mean four inference segments.

**INFERRED conditional accounting:** let A be native output for resolved transitions,
S native output for the real semantic work, S' the candidate's corresponding output,
and H additional candidate setup/reporting output. Then

    output saving = 1 - (S' + H) / (A + S).

If semantic work is unchanged, this is `(A-H)/(A+S)`. For80% output saving,
`S' + H <= .2(A+S)`. Adding useful semantic work increases the retained denominator
share; output savings need a separate mechanism/evidence, not ACK arithmetic.
The accounting includes reported reasoning in output; it never budgets away
required judgment or changes final-answer shape.

Illustration only:46ACKs at7output tokens each gives A=322. Four300-token semantic
answers give S=1200. With no added overhead and identical semantics, ACK removal
saves21.16% output. This is not a forecast or measured mixed-W50 result.

For model segments, assuming the same s segments at each of four checkpoints:

| Segments per checkpoint | Ordinary total:46+4s | Candidate:4s | Segment reduction |
|---:|---:|---:|---:|
| 1 | 50 | 4 | 92.00% |
| 2 | 54 | 8 | 85.19% |
| 3 | 58 | 12 | 79.31% |
| 4 | 62 | 16 | 74.19% |

These are call counts under stated assumptions, not token or quota savings.
State size, accumulated history, caches, preparation and retries change economics.
The native run must measure every internal segment and all final responses.

## A concrete stronger task, not four artificial ACKs

Use50ordered events with semantic checkpoints at12,25,38,50. Both arms receive
the same event sequence, authority, source and user requests. Proposed checkpoint
content is: resolve an actual ambiguous requirement and ask a necessary question;
implement a bounded coding change after the clarification; reconsider a previous
decision when a later fact makes an early detail relevant; assess the completed
artifact after actual execution and explain remaining obligations. Exact code,
graders and authority updates must be frozen before inference. No model-generated
answer to one checkpoint may be supplied to the other arm.

The46other events have the exact authorized record-and-ACK contract. Their contents
remain cold evidence and cannot rewrite authority, execute tools or decide a future
question. Contradictions stay recoverable; when relevance changes, the model can
retrieve the exact older evidence. Tools, effort, clarification, probes and ordinary
complete model-written answers remain available at every semantic checkpoint.

## Integration finding: current ACK adapter cannot simply skip checkpoints

**OBSERVED offline:** `PassiveWorkflow.accept` binds `event.turn` to the completion
ordinal. If E01 is acknowledged, E02 routes to semantics without being committed,
and E03 is passed back to the passive adapter, E03 correctly raises a sequence-gap
error. See [the replay](w50-mixed-offline-v1/RESULT.json). That is a guard preserving
the old contract, not a reason to renumber events or weaken the sequence check.

The existing lower-level CompletionLedger can preserve an interleaved stream of
completed data and reject conflicts/recover exact bytes. Its payloads are evidence,
not executable instructions or inferred semantic authority. A scripted replay of
that property is infrastructure evidence only; it is not a model/capability result.

**Smallest proposed integration:** one ordered completed-interaction stream for
both passive events and semantic checkpoint results. Each record preserves the
original event ordinal/id, event bytes/root, bound pre-state, operation and release,
original answer bytes, answer owner, native receipt when applicable and resulting
state identity. Delivery transport ownership and model answer authorship must be
distinct. Do not store a model answer under the passive-ACK schema.

Persist these state fields separately:

    unresolved_semantic_obligations
    pending_authorized_mechanics
    model_final_response_pending
    authority_version / source_roots / ledger_head

The response field matters under the user's current contract. A model-written
final after relevant execution evidence cannot be replaced by a mechanical receipt
merely because the semantic decision was made earlier. That continuation is charged.

Gate ordering:

1. Stale/conflicting/unrecoverable authority: hold execution and recover exactly;
   re-enter the model if unresolved judgment remains. Never apply with stale state.
2. Unresolved semantics or unknown/free-form transition: invoke the ordinary model.
3. Bound, authorized pending mechanics: execute deterministically, preserve evidence
   and update state transactionally; unexpected results become semantic deltas.
4. Required model final not yet written after relevant evidence: retain model
   continuation, even if that costs another segment.
5. Otherwise publish the already-authored response or exact authorized ACK through
   idempotent delivery. Never invent a semantic answer in the caller.

A data-only record cannot claim it belongs to the deterministic route. Admission
comes from the caller-bound exact contract. No separate LLM classifier is added.
Engine remains active on ordinary-model routes. Only optional context retrieval
fails open; unknown authority and effects fail closed.

## Offline gates before another native pair

- Mixed order retains all50events, all four model-authored responses and exact
  original ordinals. Pending mechanics do not create another semantic question.
- Duplicate same event/result is idempotent; changed payload or pre-state conflicts.
- Crash/restart preserves the externally pinned head; failed/interrupted publication
  cannot make an uncommitted semantic result authoritative or duplicate an effect.
- Changed requirement invalidates dependent conclusions. Unrelated historical
  evidence remains retrievable; a new query cannot be answered from stale decisions.
- Ambiguity, unknown events and contradictory execution wake the model. A valid
  machine check does not waive a semantic obligation or required final response.
- An initially unimportant early detail becomes decisive after checkpoint38.
  Test exact recovery and behavioral outcome, not summary similarity.
- Account for admission, bindings, memory, setup, recovery, storage, captures and
  all failed attempts. Cold-pair validation exposed1.55GB of logical executable
  binding reads during its pair: do not hide that behind a1.9ms lookup metric.

The native run remains **NOT LAUNCHED**. The next engineering slice is the mixed
completion adapter and its hostile offline tests, using the existing ledger. No
general semantic emulator, new model kernel, weakened verifier, mandatory database
service, new classifier or full production router is justified by this proposal.
Normal Codex-app pre-inference interception remains a separate deployment gate.
