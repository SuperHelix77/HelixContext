# Helix integrated runtime V1

`integrated_runtime.Runtime` connects existing exact evidence, persistent Memory,
Reducers and caller completion in one caller-owned store. `Policy` is immutable;
its hash includes each component's source hash. Memory selection, reducer
presentation and caller completion are independently switchable. Cold plans are
rejected in V1. No model calls, automatic command retries or source discovery.

Memory captures exact scoped observations across sessions in SQLite with durable
transactions. Literal search verifies its index against cold originals. Search
is partial: misses retain exhaustive caller-pinned history references for exact
recovery. `working_set` replaces repeated history when enabled; disabling it
returns all supplied history. Durable capture is retained in either mode.
Project/branch namespaces are logical scope, not filesystem security. Coordinated
catalog deletion is not detected. Search validation currently reads the whole
scope; its amplification is charged, not hidden.

`checkpoint` archives exact objective, decisions, source references and skill
bodies. `restore` verifies scope, policy version and every source before returning
them to a caller for reinjection. This is explicit restart/compaction support,
not an interception hook for Codex's private compaction state. Changed skill or
component versions require a new checkpoint. Historical source text never gains
instruction authority merely by being restored.

Reducers capture a command exactly once, archive stdout/stderr and exit status,
then independently verify a bounded typed projection. Pytest and text compiler
diagnostics are supported. Unknown commands, shell wrappers, unsupported output
formats, short output and insufficient byte gains bypass reduction. A caller may
bind a known producer format explicitly. Git, rg and other command-specific
adapters remain native passthrough; this is not full RTK command coverage.
Failure after capture returns captured native output rather than rerunning a
side-effecting command. Invalid admission policy is rejected before execution.
Raw corruption fails closed. Exact retrieval uses the existing evidence APIs.
Byte admission is a cheap gate, not a guarantee of native token savings.

Caller completion takes original IDs, uses a pinned exact-copy catalog and
atomically publishes only verified bytes. Existing destinations require their
expected hash. Semantic selection remains the model's responsibility. Successful
execution does not establish semantic correctness. Noncooperating external
writers remain outside the cooperative-lock TOCTOU guarantee.

Every successful runtime operation publishes a hash-bound immutable receipt and
an append-only, fsynced timestamped event. The HUD consumes these without model
calls. Cold command receipts survive presentation failure. State/evidence is
published before its observation event; a crash between them can omit an event,
so the event stream is observability, not a complete transactional state catalog.
Failed completion raises while preserving the previous destination; caller must
record the failure. No automatic retry or claimed exactly-once execution across
process crashes.

Accounting separates native input/output from local preprocessing seconds,
logical store reads/writes/hashing, index input and validation bytes, retained
file lengths and emitted prompt bytes. Counters are per Runtime instance and
must be aggregated across restarts (the integrated benchmark does this in its
preparation and final receipts). Snapshots are cumulative within each instance;
do not add overlapping snapshots. Physical disk traffic, SQLite traffic, parent
research tokens and money remain unmeasured. Do not call this a full billing win.

Validation covers failed reduction without duplicate command side effects,
invalid-policy rejection, binary/raw recovery, explicit skill restoration,
latent-fact retrieval after 50 stored events, policy/scope invalidation, memory
bypass and exact-copy failure preservation. These are deterministic engineering
tests, not model intelligence or long-horizon workflow parity results.
