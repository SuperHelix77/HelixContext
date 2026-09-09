# Ledger readback comparison and stop decision

Compared commit `7e7f5c7` with the revised ledger on the same 49 exact W50
completion payloads in separate temporary stores. The revised code verifies the
existing chain once per transaction, then reads back only the two new CAS objects.
It does not reread the entire prefix a second time.

| Metric | Before | After |
|---|---:|---:|
| Ingest object bytes read | 1,403,484 | 716,044 |
| Read operations | 4,802 | 2,450 |
| Object bytes written | 28,604 | 28,604 |
| One observed elapsed time | 0.139 s | 0.090 s |

OBSERVED: 48.98% fewer logical object reads. Both arms produced the same final
root and exact recovered payloads. All 29 ledger/memory/epoch tests passed.
The [receipt](COMPLETION_LEDGER_READBACK_PAIR.json) binds both source hashes.
This is neither a native-token benchmark nor statistically established latency.

The integrity claim is snapshot validation under the tested fault model. Existing
payload tampering before ingestion is rejected. The SQLite transaction serializes
ledger writers; it does not prevent an unrelated process from changing CAS files
during commit. Removing the second scan changes that race window; neither version
provided hostile concurrent-writer protection. Such protection needs separate
custody/snapshot guarantees, not an arbitrary number of repeated scans.

Remaining read amplification is about 41.5× payload; cumulative chain verification
remains quadratic. SQLite and physical traffic are not included in these counters.
Research-only status remains unchanged. No model invocation, production activation
or frozen benchmark amendment occurred.

**Stop further ledger optimization for now.** This removes measured infrastructure
overhead but cannot reduce the observed Luna 156-token semantic response to the
128.2-token 80% budget. It likewise cannot erase 5,361 tokens already spent in the
coding attempt. The next native experiment requires an independently supported
intervention on model-visible work, with preserved semantic checks; ledger-only
changes do not justify a paid rerun. The full three-model capability/agentic and
80/80 qualification objective remains open.
