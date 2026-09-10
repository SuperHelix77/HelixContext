# Helix telemetry HUD v0

Live native streams validate the exact JSONL prefix pinned by the last status
receipt, then expose later monotonic native counters as **provisional** while the
matching app-server PID and working directory are live. A growing stream is not a
completed receipt. Closed/dead writers, mutated prefixes or mismatched sealed
counters do not receive this exception. Final receipts still require the full
native hash. Live rows never inherit finite artifact PASS or enter completed-pair
medians. Runtime observation is local; it does not authenticate a hostile host.

## Scoped statistics and Engine-only execution

`cohorts` declares exact experiment membership, model, effort and evidence scope.
Medians and ratio-of-totals stay separate. Regressions remain included; missing
pairs, duplicate threads and mismatched effort are explicit exclusions. No
descriptive statistic automatically qualifies a release.

`audit_reports` pins finite-check reports and matches exact native stream hashes.
`engine_replays` separately pins offline source/answer/state artifacts; tampering
withdraws verification. Zero-inference replay never enters native-model medians.
Headline totals deduplicate native threads. Pricing includes metered closed and
failed sessions. Unchanged native-trace parsing is cached; scan duration and logical
reads are visible. See the
[current evidence and limits](../../docs/research/continuation-contract/BOUND_RETRIEVAL_AND_LUNA_STATUS_20260910.md).

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

## Current-price comparison

The observer fetches the official OpenAI pricing Markdown over verified HTTPS on
startup and every two minutes. It parses only the Standard table with an exact
column schema; Batch/Flex prices cannot silently substitute. Quotes expire after
five minutes. Fetch/schema errors are visible; expired or missing prices suppress
dollar estimates, including when browser telemetry disconnects. This is periodic
freshness, not a guarantee of instantaneous provider updates.

The HUD prices only completed, raw-native-verified counters with explicit input,
cache-read, cache-write and output counts. Cache subsets are subtracted before
pricing ordinary input; reported reasoning is not added to output again. It
shows both short- and long-context **tariff scenarios**, since service/context
billing tier is not established by these receipts. These are current-price USD
API-equivalent estimates, not historical charges or Codex subscription costs.
Full effective cost remains unknown until Engine, storage, recovery, coordination
and parent-chat costs have a comparable accounting basis.

Each row compares its own registered control/candidate task. The overhead trials
use V3 as their control, not native bypass. Rows are not pooled into a cross-model
ranking. No matching Luna XHigh or Terra receipts were found; their absence is
shown explicitly, without relabeling Luna High or repricing another model's run.

Validation for this change: 13 HUD/pricing tests passed. Chromium verified live
pricing, paired dollars, missing-model labels, filters, mobile overflow, expiry
after telemetry disconnect, and absence of JavaScript errors. Official quote
retrieved during verification had SHA256
`244b537c06fb94e4d7214ba7f076f2bd18cace4ad165d30ad5da77cbaaad36c6`.
