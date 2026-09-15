# Helix conversation-stuck P0 handoff

Date: 2026-09-15 (Europe/Istanbul)

## Scope

P0 only: repair the Helix conversation-stuck path. This investigation does not change QLoRA,
Goal/Plan, computer use, packaging, DFlare, Q38, or unrelated features.

The source checkout being repaired is `/home/user/unsloth-full`, from
`SuperHelix77/unsloth`, branch `codex/unsloth-helix-27b-harness`, revision
`1d8a3aa1fe73f41e02a18629d0a0641c58b71b56`. The durable publication branch remains separate from
this handoff checkout.

## Evidence preservation and runtime limitation

The reported runtime evidence is expected at:

- `/Users/mert/.unsloth/studio/studio.db`
- the corresponding Helix backend/frontend logs beside that installation

Those paths are not mounted in this environment. A search under `/home/user` found no Helix
runtime database, and no backend, frontend, llama.cpp, or live model process was running when the
checkout was validated. Therefore:

- the newest stuck thread has **not** been identified here;
- no DB or log evidence has been mutated or represented as a substitute;
- no claim is made that the actual stuck thread has been recovered;
- the first incomplete stage of a real failed Send cannot be named from this checkout alone;
- the required non-empty response and restart proof remain runtime acceptance steps, not unit-test
  results.

Before mutating the user's installation, collect read-only copies and hashes, for example:

```text
studio.db -> studio.db.pre-p0.sqlite3
backend/frontend logs -> logs.pre-p0/
sha256sum studio.db.pre-p0.sqlite3 logs.pre-p0/* > evidence.sha256
```

Then record the newest thread and its latest assistant/run rows in this document or an adjacent
private evidence file. Do not put the user's private DB or logs in the Git repository.

## Implementation in the source checkout

The repair is fail-open at the optional integration boundaries and conservative at persistence:

1. **Learning/Mem0/Hermes context**
   - `/studio/frontend/src/features/chat/api/learning-api.ts` bounds the complete authenticated
     context request, including auth refresh/JSON parsing, with a four-second `AbortController`
     timeout.
   - `/studio/frontend/src/features/chat/api/chat-adapter.ts` converts timeout, 404, auth, HTTP,
     and unexpected context errors to disabled context and continues core chat. It emits memory
     start/end/timeout/error events without making those events part of the send critical path.

2. **Busy ownership and terminal cleanup**
   - A per-`AbortSignal` ownership record is registered before the first pre-stream `await`.
   - The outer adapter wrapper releases ownership on every resolve/reject/abort path, including
     document extraction, initialization, prompt construction, memory resolution, run admission,
     and backend request failures.
   - Partial text, reasoning, tool payload, and deliberate stop markers are preserved; only a
     truly empty assistant placeholder with no server run is eligible for cleanup.

3. **Lifecycle tracing**
   - The adapter records `send.received`, `memory.start`, `memory.end`,
     `memory.timeout`/`memory.error`, `prompt.start`, `prompt.end`, `persistence.start`,
     `persistence.end`, `run.created`, `backend.request`, `backend.first_token`,
     `backend.complete`, `run.finalized`, and `ui.terminal`.
   - Records include thread ID, run/cancel ID, estimated prompt token count, unresolved tool-call
     count, and elapsed milliseconds. Tracing is best-effort and cannot fail a send.

4. **Empty optimistic assistant cleanup**
   - Backend storage has a single `BEGIN IMMEDIATE` guarded deletion operation that accepts only
     an empty assistant row with no attachments and no active or associated generation run.
   - `DELETE /api/chat/threads/{thread_id}/messages/{message_id}` is authenticated and returns
     conflict for non-empty, non-assistant, active, or managed rows.
   - The frontend deletes its IndexedDB shadow after the guarded backend delete succeeds, or when the
     backend confirms the row is already missing; protected/managed conflicts remain for recovery.

5. **Tool-history replay**
   - Existing replay serialization drops assistant tool calls that do not have a matching tool
     result and never emits a dangling tool result. The adapter now traces the unresolved count so
     malformed history is visible instead of silently blocking reconstruction.

## Validation completed

All commands below ran against `/home/user/unsloth-full`:

- `python3 -m compileall -q studio/backend/routes/chat_history.py studio/backend/storage/studio_db.py studio/backend/tests/test_chat_generation_runs.py` — passed.
- `git diff --check` — passed.
- `node --experimental-strip-types --test tests/chat-adapter-scan-cost.test.ts tests/cancelled-turn-history-prune.test.ts tests/chat-generation-reconnect.test.ts tests/chat-run-checkpoint.test.ts tests/learning-context-timeout.test.ts` — **45 passed**.
- `npm run typecheck -- --pretty false` — passed (production and test TypeScript projects).
- `python -m pytest -q studio/backend/tests/test_chat_generation_runs.py` — **57 passed**.
- `python -m pytest -q studio/backend/tests/test_chat_history_storage.py` — **62 passed**.

The targeted ESLint command still reports pre-existing restrictions and unused symbols in the
large `chat-adapter.ts` file; it did not report an error in the new learning API, placeholder API,
or timeout test. Do not broaden this P0 into an unrelated lint cleanup.

## Required runtime acceptance procedure

Run this only after preserving the real DB/log evidence and starting the user's normal Helix
backend/frontend/model stack without lowering context length:

1. Identify the newest stuck thread from the preserved DB and logs.
2. Capture one failed Send with a unique test marker. Correlate the lifecycle records in order and
   name the first missing transition:
   `send.received -> memory -> prompt -> run.created -> backend.request -> backend.first_token ->
   stream -> persistence -> ui.terminal`.
3. Verify optional learning/Mem0/Hermes failure, 404, and timeout paths still produce an ordinary
   model response.
4. Verify a failed/cancelled/interrupted run leaves no unmanaged empty assistant row and leaves the
   UI busy state false.
5. Use the guarded cleanup only for the actual empty unmanaged placeholder, then replay the same
   existing thread. Verify a real non-empty assistant response and record its run ID.
6. Restart Helix without changing context length. Replay the same thread again and record a second
   non-empty response/run ID.
7. Append timestamps, thread ID, run IDs, response excerpts or hashes, and relevant trace lines to
   a private evidence file outside Git. Do not publish the private DB/logs.

The source repair must not be declared runtime-complete until those steps are performed against
an actual Helix installation.

## Publication status

The repair is committed in the source checkout as `40773d2` (`fix studio chat stuck-send recovery`).
The attempted creation of `SuperHelix77/unsloth-helix-stuck-p0` failed with GitHub
`Resource not accessible by integration (createRepository)` before any push. No changes were
pushed to the original public `SuperHelix77/unsloth` repository. A GitHub connection with
permission to create a private repository under the requested owner is required to finish
publication.
