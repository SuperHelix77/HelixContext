# Native Engine delivery: durable execution items without inference

**OBSERVED, 2026-09-10:** the installed Codex app-server recorded an explicitly
Engine-attributed ACK as a `commandExecution` item with `source=userShell`.
The exact item/output survived terminating the server and resuming in a new
process. A second harmless command intentionally failed with exit 1; its failed
item also survived. No `turn/start` was sent and the no-model loopback provider
received no request. The two-command/start/restart experiment took **0.370 s**.

| Operation | Turn status | Execution status | Exit | Exact item after restart |
|---|---|---|---:|---|
| Print attributed Engine ACK | completed | completed | 0 | Yes |
| Intentional `/usr/bin/false` | completed | failed | 1 | Yes |

**A completed turn does not establish successful execution.** Any delivery
adapter must inspect the bound command item, exit status, exact output and its
own remaining obligations. The failure case kills a turn-status-only success rule.

The earlier `thread/inject_items` experiment retained raw context but returned no
visible item through the thread item/turn APIs. This experiment supplies the
missing native **execution-history** primitive, without impersonating a model
assistant message. See [extracted receipts](NATIVE_ENGINE_DELIVERY_RESULT.json)
and the [offline auditor](native_engine_delivery_audit.py). Full synthetic wire
records remain in the local experiment directory, bound by hashes in the report.

## Authority and deployment boundary

The official [app-server documentation](https://learn.chatgpt.com/docs/app-server)
describes `thread/shellCommand` as a user-initiated command path that starts a
standalone turn when idle. It runs **outside the thread sandbox** and is intended
for explicit user commands. Those conditions are material. This test used only
two literal harmless commands in a disposable workspace/home with no copied
credentials; the production configuration hash was unchanged.

**CONDITIONAL:** this can be a delivery adapter for an explicitly authorized
Engine command, not a general route for silently converting arbitrary chat or
untrusted events into unsandboxed shell execution. Optional hooks, ordinary
model tools and a model's own execution policy must retain their existing
permission boundaries. Merely activating the Helix skill is not such a route.

**UNKNOWN:** automatic pre-submit composition, duplicate delivery, crash between
command completion and receipt acknowledgement, and normal desktop rendering.
The experiment started a new app-server process for restart, not just an in-memory
resume. It did not open the isolated thread in the production app or prove that
its UI renders the item. No provider usage update arrived; null counters are not
fabricated zero-token billing receipts.

## Smallest follow-on integration

Keep the Engine completion ledger as the authority for transition identity and
bound state. Define an explicit user-command delivery port that executes an
already-authorized, fixed Engine entrypoint and reconciles its native item ID.
Let the Engine expose exact output as Engine output. Keep an unknown outcome
pending until reconciled; do not rerun an effect merely because its ACK was lost.
Preserve the semantic gate: unresolved judgments still require Luna/Sol/Astra.

Before deployment, offline falsifiers must prove: a lost ACK does not cause
duplicate execution; the native item belongs to the expected thread/operation;
stale state prevents effects; failed execution cannot commit success; and a
background model turn is not accidentally created. A forged receipt or a generic
completed-turn event must not satisfy delivery. Desktop rendering then needs a
separate actual-app check. No additional inference is needed for these tests.

This advances the integration boundary; it does **not** change Luna's corrected
coding median of 86.29% input / 64.04% output savings or qualify a 75/75 release.
