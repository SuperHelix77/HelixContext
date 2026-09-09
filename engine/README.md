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
python3 -m pytest -q engine/prototype/test_evidence.py engine/prototype/test_verification.py engine/prototype/test_line_index.py
```

Observed: **25 tests passed**. These include corrupt metadata, altered numeric evidence, omitted diagnostics/counts, invalid spans, stale publication, byte corruption, timeout and nonzero process exits. They are infrastructure tests, not model capability evidence.

## Costs and unresolved limits

- Default range retrieval reads and hashes the entire object. An opt-in immutable line index now supports authenticated chunk retrieval; index construction includes full reconstruction verification and duplicates raw storage. It is not automatically enabled.
- Both staging and content-addressed raw copies are retained. Storage duplication is real, not free.
- Metrics expose application object/staging bytes and projection parsing. Physical disk/cache traffic, filesystem metadata, watched-file hashing, SQLite publication I/O, full CPU, retention and monetary costs are not fully measured.
- stdout/stderr cross-stream interleaving is not recorded. The environment label is not environment attestation. A hash proves identity, not truth, authority or semantic sufficiency.
- The verifier checks the declared supported structural projection; it cannot certify unknown log formats or future decision relevance. Exact originals remain necessary.
- Active context compilation, complete canonical peer packets, index admission/retention policy and prospective native model middleware benchmarks remain pending.
- No automatic interception of every Codex model input is claimed. This prototype only mediates commands explicitly routed through it.

## Separate native runtime findings

A separate installed runtime restored an active skill entrypoint and selected mode in one actual Sol High native compaction probe, with a verification nonce introduced only after the pre-compaction turn. This is one bounded restoration result, not proof that every skill or referenced resource survives every compaction.

A native peer-event probe delivered the correct blocker, but acknowledgement failed because the model shell could not write the protected runtime state directory. It is a failed end-to-end coordination test. The integration must be corrected and retested within its intended permissions before claiming workflow parity. Repeated undelivered acknowledgements and hook-process latency must count as overhead.

These extensions are not included in the completed V3 performance measurements in `../FRONTIER_REPORT.md`. Those scored outcomes passed, but aggregate native input savings were approximately 25.3% Luna, 21.0% Sol and 17.1% Astra. General intelligence parity and 95% net savings remain unestablished.

## Optional indexed retrieval experiment

`line_index.build(store, source_sha256)` creates and verifies an immutable index. `Store.retrieve(..., index=index_sha256)` binds it to the receipt's selected stream. Ordinary retrieval remains available. Both projection and retrieval now use the same byte-line convention, including text containing Unicode paragraph separators.

Reproduce with `python3 engine/prototype/benchmark_ranges.py`. The committed `range-results.json` records a deterministic 4,400,000-byte synthetic source, exact query sequence and all application byte counters. All queried bytes matched.

| Lookups | Application read + write savings, including build and verification | Ordinary wall time | Indexed total wall time |
|---:|---:|---:|---:|
| 1 | -202.05% | 0.005 s | 0.074 s |
| 5 | 39.21% | 0.023 s | 0.072 s |
| 20 | 84.45% | 0.085 s | 0.077 s |
| 40 | 91.99% | 0.169 s | 0.078 s |

The extra index objects occupy 4,434,674 logical file bytes. Both arms start with one identical raw object; the index arm includes construction, verification and lookups. These timings are single local observations with OS caching, not confidence intervals. The ordinary arm is the existing full-hash range reader; an efficient seek-based ordinary control is still needed for a broader systems comparison. Very long individual lines can exceed the target chunk size. Memory peak, physical disk activity and monetary cost are unmeasured. **This is not a model benchmark or a token-savings result.**

The one-lookup loss and five-lookup latency loss prohibit enabling this indiscriminately. A future admission policy must account for expected reuse and fail open to ordinary exact retrieval.
