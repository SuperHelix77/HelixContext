# Pre-inference runtime result: inhibition works, completion still open

2026-09-10, installed Codex Desktop CLI 0.153.4. Separate disposable homes,
no production configuration edits, no copied credentials and no hosted model calls.
Public [receipt](PREINFERENCE_RUNTIME_RESULT.json) retains raw evidence hashes.

## Prompt blocking

A harmless UserPromptSubmit hook captured the synthetic prompt and returned a
blocking decision. Its exact definition was reviewed and trusted through the normal
CLI `/hooks` interface in the isolated home. No blanket hook-trust bypass was used.
An initial directory-trust screen pointing at the parent research repository was
declined; review proceeded in a new empty `/tmp` workspace instead.

Both arms used a custom no-auth loopback provider. The endpoint counted requests
and returned a fixed error; it did not generate a model response.

| Arm | Provider requests | CLI outcome |
|---|---:|---|
| No hook | 1 | Failed on intentional mock response |
| Trusted blocking hook | 0 | Completed; reported input/output/reasoning all zero |

**OBSERVED:** the hook ran, and the blocked CLI turn ended before a provider request.
This establishes inhibition in this installed CLI path, not merely schema support.
The blocked stdout contained no assistant ACK. Exit zero and zero usage do not
establish workflow equivalence or successful user-visible completion.

An unrelated unauthenticated plugin-cache request returned 401 in stderr. The
experiment claims zero hosted inference, not a network-isolated client process.

## History insertion

In a separate disposable app-server thread, `thread/inject_items` accepted an
explicitly Engine-labelled synthetic record. No `turn/start` was sent and the
loopback provider saw no requests. The exact text was persisted in the rollout.
However `thread/read(includeTurns=true)` returned an empty turn list. Insertion
therefore supplies a history primitive, not yet a normal completed-turn/UI primitive.
The probe source is `preinference_history_probe.py`; it is not a release adapter.

## Release consequence

The broad question “can this installed client stop before inference?” now has a
positive bounded answer. The next question is narrower: can Engine deliver a
truthful ACK/completion and preserve history/restart semantics through supported
interfaces, without invoking a model or impersonating model-generated output?

Test hook/app-server composition, event ordering, direct thread/item reads, restart,
duplicate delivery, failure visibility and normal desktop rendering before routing
real work. Keep injected evidence as attributed reference data. Do not make a
completed zero-token but answerless turn look like successful ACK handling in HUD.
Until those tests pass, do not label Luna released or generalize these zero counters
to model-task savings. W50 75/75 remains bounded; broader Luna economics still fail.
