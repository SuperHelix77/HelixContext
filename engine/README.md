# Helix Engine: experimental middleware

HELIX means **Hierarchical Evidence Loading and Intelligent eXecution**.

This prototype applies the Q38-derived design principles of explicit state, exact copying, cold evidence, version-bound references, transactional publication and complete accounting. Q38 measurements do not establish Helix performance. No learned component or fixed artifact-size target is assumed.

The contract is in `CONTRACT.json`. The priority is capability and workflow parity, then net efficiency; 95% is aspirational.

## Implemented

- Command capture preserves separate stdout/stderr bytes, exit/signal status, timeout, timestamps, caller-supplied environment label and explicitly watched file changes.
- SHA-256 objects bind raw evidence and receipts. Retrieval verifies byte identity and supports exact line ranges, with base64 for invalid UTF-8.
- Generic, pytest and compiler reducers emit bounded, explicitly partial projections. Large projections request retrieval rather than truncating JSON or numeric evidence.
- An independent verifier checks source text, hashes, exit status, line counts, summary evidence, diagnostic omission counts and failure spans. It does not call the reducer to validate its own output.
- `verification.publish(store, name, candidate, expected_revision)` verifies before publishing a transactional SQLite pointer. Rejected or stale updates leave accepted state unchanged. Orphan cold objects can remain after failed publication.

The command wrapper emits a candidate. Acceptance is an explicit separate operation through `publish`; successful command execution is not automatically a verified publication.

## Reproduce the structural tests

```sh
python3 -m pytest -q engine/prototype/test_evidence.py engine/prototype/test_verification.py
```

Observed: **15 tests passed**. These include corrupt metadata, altered numeric evidence, omitted diagnostics/counts, invalid spans, stale publication, byte corruption, timeout and nonzero process exits. They are infrastructure tests, not model capability evidence.

## Costs and unresolved limits

- Range retrieval currently reads and hashes the entire raw object. A test deliberately records at least 50,000 object bytes read to retrieve 5 useful bytes. Efficient authenticated ranges remain unfinished.
- Both staging and content-addressed raw copies are retained. Storage duplication is real, not free.
- Metrics expose application object/staging bytes and projection parsing. Physical disk/cache traffic, filesystem metadata, watched-file hashing, SQLite publication I/O, full CPU, retention and monetary costs are not fully measured.
- stdout/stderr cross-stream interleaving is not recorded. The environment label is not environment attestation. A hash proves identity, not truth, authority or semantic sufficiency.
- The verifier checks the declared supported structural projection; it cannot certify unknown log formats or future decision relevance. Exact originals remain necessary.
- Active context compilation, complete canonical peer packets, efficient exact ranges and prospective native model middleware benchmarks remain pending.
- No automatic interception of every Codex model input is claimed. This prototype only mediates commands explicitly routed through it.

## Separate native runtime findings

A separate installed runtime restored an active skill entrypoint and selected mode in one actual Sol High native compaction probe, with a verification nonce introduced only after the pre-compaction turn. This is one bounded restoration result, not proof that every skill or referenced resource survives every compaction.

A native peer-event probe delivered the correct blocker, but acknowledgement failed because the model shell could not write the protected runtime state directory. It is a failed end-to-end coordination test. The integration must be corrected and retested within its intended permissions before claiming workflow parity. Repeated undelivered acknowledgements and hook-process latency must count as overhead.

These extensions are not included in the completed V3 performance measurements in `../FRONTIER_REPORT.md`. Those scored outcomes passed, but aggregate native input savings were approximately 25.3% Luna, 21.0% Sol and 17.1% Astra. General intelligence parity and 95% net savings remain unestablished.
