# Helix telemetry HUD v0

Local, read-only research instrument. No routine inference, model-generated
summaries or agent polling. It observes explicitly registered native status,
trace and result files every two seconds; unchanged file contents are cached.
File I/O and local CPU are additional costs, not free. Physical I/O is unmetered.

Run:

```sh
python3 engine/hud/server.py --config /absolute/config.json --journal /absolute/observations.jsonl --port 8769
```

Open `http://127.0.0.1:8769/`. The server binds only to loopback. No mutation or
arbitrary-file endpoint is exposed. Configuration is caller-controlled:

```json
{"experiments":[{"id":"example","name":"Integrated candidate","classification":"Fresh development pair","root":"/absolute/experiment","result":"results.json","manifest":"manifest.json","runs":[{"arm":"off","status":"receipts/off/status.json","events":"receipts/off/events.jsonl","cwd":"tasks/off"},{"arm":"on","status":"receipts/on/status.json","events":"receipts/on/events.jsonl","cwd":"tasks/on"}]}]}
```

## Telemetry contract

`/api/state` and `/api/events` expose `helix.hud.v1` snapshots. SSE transports
updates and observer heartbeats. Each observation journal entry has a unique
observer-instance/event identity, observation timestamp, source hashes and the
projected state. A restart creates a new observer identity; it does not pretend
that the old revision counter continued. This local append-only journal is not
an authenticated or crash-proof canonical Engine ledger.

Native execution events retain source order. Execution timestamps are shown only
when supplied by the source; observer time is not substituted. Token totals come
from native receipts, cross-checked with completed-turn usage when present. A
conflict withholds token figures. Partial files and absent measurements stay
unknown. A running status alone is not enough: PID command identity is checked
when a configured task cwd is available; otherwise the state is unverified.

Task checks are bound to the matching native trace hash. A previous result cannot
silently certify a new run. PASS refers only to finite artifact/source checks;
capability and workflow parity remain unproven.

Engine operations currently come from caller-completion receipts where available.
Other mechanism activation, glue/setup token attribution, exact model-visible
bytes, parent-chat cost and compaction ACK are not instrumented. Suspected Engine
reading is an explicit command-text heuristic over recorded output bytes; it is
neither exact source attribution nor a native input-token measurement.

Model Work Fraction stays **unmeasured**: no commensurate model/Engine cost unit is
available. Adding tokens to milliseconds or bytes would produce a meaningless
fraction. Total tokens in the header cover visible registered runs, including
both control and candidate; they are not a whole-project/research bill.

## Verification

Six backend tests check missing/invalid counts, stale/tampered evidence, event
counting, change-only journal publication, scoped HTTP reads and live SSE updates.
The complete prototype/output/HUD suite passed **185 tests**. A real Chromium
check passed filters, selected run, Engine-read signal, pause/resume, heartbeat,
receipt links, desktop/mobile layout and console checks. The desktop screenshot
was visually inspected. Test screenshots and local path configuration stay local.

Huashu Design informs restrained layout and hierarchy; this v0 deliberately omits
decorative graphs, external assets and inference-based analysis. The adapter is
independent of visual styling. Keeping this server open cannot launch benchmarks.
