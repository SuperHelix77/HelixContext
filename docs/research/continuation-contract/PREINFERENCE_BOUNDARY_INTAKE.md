# P0: supported pre-inference candidate located, composition untested

2026-09-10. Installed client schema generated with experimental fields, no native
inference or production configuration change. Exact version/hashes in the
[intake receipt](PREINFERENCE_BOUNDARY_INTAKE.json).

## New evidence

**DOCUMENTED:** `UserPromptSubmit` receives the prompt before sending and supports
blocking. Common output can surface a UI warning; that is not an assistant answer
or durable successful task completion. Hook definitions require exact trust review.
See [official hooks](https://learn.chatgpt.com/docs/hooks).

**OBSERVED in installed schema:** `userPromptSubmit` appears in hook event names.
`thread/inject_items` accepts `threadId` and raw Responses items, with an explicit
description of appending model-visible history without starting a user turn.
This is schema evidence, not executed interoperability evidence.

**DOCUMENTED:** clients normally own `turn/start` and receive lifecycle notifications.
See [official app-server documentation](https://learn.chatgpt.com/docs/app-server).
Installed CLI also offers Unix/socket transports and a byte-forwarding `proxy`.
Proxy availability does not establish a supported desktop endpoint override.

Prior statements that the inspected integration had not established a pre-inference
hook remain historically accurate. The new specific candidate shrinks that unknown:
test `UserPromptSubmit`, not generic PostToolUse or skill interception.

## Ranked paths

1. **UserPromptSubmit + durable Engine completion + supported history/delivery.**
   Highest-priority candidate. Verify blocking actually prevents outgoing inference,
   then separately establish history and UI semantics. A block warning alone fails.
2. **Caller-owned app-server turn/start gate.** Already feasible in research callers;
   desktop routing to that caller remains unproved. Do not call it normal-app release.
3. **Plugin/MCP hook transport.** Potential carrier for a supported lifecycle hook;
   a model-issued tool call alone is too late. No broad registry needed.
4. **Thin proxy.** Consider only with an actual desktop connection setting and
   protocol-preserving completion. Do not synthesize native usage or model authorship.
5. **Maintained core patch.** Defer until the supported candidates are falsified.
6. **Skill-only.** Retain context/policy role; cannot decide whether its own first
   inference should exist.

The inspected ServerRequest methods expose approval/tool/time/auth requests, not a
general server-to-client semantic-gate callback. TurnStart fields include context
and trigger data but no demonstrated caller-supplied deterministic completion.
This is a bounded schema observation, not a proof about every internal entry point.

## Smallest offline runtime probe

Use an isolated Codex home, exact reviewed harmless hook, and a loopback provider
that counts requests and returns a fixed non-model response. No real credentials,
hosted calls, production hooks or broad trust bypass. Test one pass-through prompt
and one explicitly qualified synthetic passive event. The control must reach the
loopback endpoint; the block arm must execute its hook and reach zero requests.
Preserve hook input/output, terminal turn status, notifications and history.

Separately exercise `thread/inject_items` only in the disposable thread. Verify
exact history retention, clear Engine attribution, restart, duplicate identity and
whether it appears in normal UI/history APIs. It must not impersonate a generated
model answer. No live user thread should receive injected test messages.

Kill conditions: ignored/untrusted hook, any model request in the blocked arm,
permanent cancelled/failed task instead of required ACK workflow, missing history,
duplicate delivery, or race with an active inference. Do not solve ordering by
starting a second model call. If blocking works but completion does not, classify
only inhibition as verified and continue the delivery investigation.

## Authenticated append is not full cold-integrity verification

Hashing previous root plus new identity/binding/payload can authenticate an append
in constant work relative to history length. It cannot detect an arbitrary changed
old payload without reading that payload or relying on an independently enforced
immutability guarantee. Merkle roots do not change this limitation: proofs validate
the bytes supplied, not unread storage.

Keep separate contracts for append-chain validity, verified evidence reads and full
integrity audits. A fixed hash chain does not make mutable JSON trustworthy. Current
ledger checks old payloads on every ingestion; reducing that policy requires an
explicit fault-model change, not merely an implementation rewrite claimed equivalent.
The recent paired readback change removes duplicate reads but retains one full
snapshot scan; it does not provide O(1) appends or hostile-host custody.

**Decision:** prioritize the isolated pre-submit runtime probe over further ledger
optimization. No new Luna token sweep until a safe pre-inference/delivery boundary
is demonstrated. Current W50 and broader-task classifications stay unchanged.
