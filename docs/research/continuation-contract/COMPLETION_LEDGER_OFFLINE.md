# Completion ledger: correctness slice, not economic qualification

Implemented separately from frozen W50 drivers in
`engine/prototype/completion_ledger.py`. Uses existing Memory SQLite connection and
CAS objects. No installed skill, production routing, model prompt or benchmark
implementation changed. No automatic semantic gate or execution capability added.

The caller provides its expected state head. Completion identity, immutable receipt
and current head commit transactionally; exact duplicate delivery returns the
original receipt plus the latest head. Conflicting bytes, stale head, changed cold
payload or inconsistent index reject before a new authoritative commit. Index-free
recovery reads exact history from the caller-held root. Stored semantic obligations
and pending steps remain opaque data; ingestion does not interpret or execute them.

**OBSERVED:** 29 focused tests passed (5 ledger, existing memory and epoch tests).
The ledger tests cover restart/retry, late duplicate, conflicting identity, stale
binding, scope, mutable-index rollback, interrupted publication, raw instruction
non-execution and tampered prior payload. These are simulated failures, not a
physical power-loss or concurrent-worker certification.

**OBSERVED:** all 49 W50 event/ACK payloads recovered exactly after reopening the
ledger. Local append time was 0.153 seconds, payload 17,236 bytes, CAS writes 28,604
bytes, and ingest CAS reads **1,403,484 bytes** (about 81.4× payload). Stored files
occupied 94,140 logical bytes. See [receipt](COMPLETION_LEDGER_OFFLINE.json).

The high read amplification is explicit: this conservative version checks the full
chain before ingestion and again before publishing its new head. It therefore has
quadratic cumulative history traffic. It fixes a tested correctness gap but is not
admitted as an efficient long-running implementation. No savings are inferred from
the short local latency; SQLite/physical I/O, host caching and invocation integration
cost remain unmeasured. Zero native calls were made by this test.

Trust and durability boundaries: the expected head must survive independently of
the mutable catalog. A caller retrying with the original parent can recover a lost
ACK, but cannot detect a later rollback it never learned about. Same-user hostile
control over all trusted roots is outside this mechanism. CAS file fsync and SQLite
FULL synchronization do not constitute a power-loss proof for the filesystem;
directory persistence and multi-process delivery need separate testing. Interrupted
operations can leave unreferenced CAS objects, which remain charged storage.

Next economic work must address repeated chain validation without treating mutable
indexes as trusted authority or silently weakening exact recovery. Candidate changes
need a declared fault model and measured validation frequency. Do not activate this
ledger on every model turn or spend a native benchmark merely to validate ingestion.
The 80/80 plus capability/workflow goal remains open.
