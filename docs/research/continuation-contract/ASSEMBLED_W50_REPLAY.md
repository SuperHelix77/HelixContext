# Assembled continuation: exact offline compatibility

`engine/prototype/passive_workflow.py` combines caller-bound passive-event scope,
exact completion storage, transactional sequence/idempotency checks and attributed
receipt offering. Engine stays active when it returns `semantic_required` for a
changed or unknown request. It does not launch a model or claim semantic resolution.

The explicit record-and-ACK request contract, not arbitrary message resemblance,
qualifies the passive path. Incoming raw bytes are preserved even when the event
needs semantics. A caller-supplied authority digest namespaces the workflow;
changing it prevents reuse of the old root. This digest does not independently
establish authority: admission remains the caller's responsibility.

**OBSERVED:** 17 focused passive/delivery/ledger/execution checks passed. Real W50
events produce all 49 exact ACKs, survive reopening and preserve byte-exact incoming
JSON. The final request and cancellation take the semantic path. Conflicting
duplicate bytes, sequence gaps, duplicate JSON keys and wrong-authority roots do
not silently execute a new passive transition.

**OBSERVED:** replaying the original recorded V7 decision over recovered events
produces the exact original final artifact and passes its independent negative
reason check. No new inference occurred. [Receipt](ASSEMBLED_W50_REPLAY.json) binds
source hashes and original native trace; `assembled_w50_replay.py` reproduces this.

Current replay: 1,213,344 logical object bytes read, 61,587 written, 0.116 seconds
on this host. Sequence checking now occurs inside the ledger transaction rather
than requiring an extra outer full-history read. Validation remains quadratic;
physical/SQLite traffic and statistical latency are unmeasured. Exact raw payloads
are duplicated in evidence/completion encoding and their cost remains charged.

This is assembled offline compatibility, not fresh model behavior, normal-app
delivery, a capability holdout or a 75/75 release. The older W50 native counters are
not reassigned to this implementation. Positive authorization, unfamiliar amendment
scopes and other semantic decisions still need a qualified model/re-entry path.

Next: freeze a runner using this lifecycle and ordinary semantic execution, preserve
tool/effort settings, and qualify exact event delivery plus final decisions with a
fresh control/candidate comparison. Include varied and hostile authority cases and
report medians by task family. Engine must remain active in all candidate tasks;
unresolved semantics invoke a model, not an Engine-off bypass.
