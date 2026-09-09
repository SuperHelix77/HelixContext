# Existing W50 dispatcher: lifecycle falsifier

OBSERVED, 2026-09-10. Ran `python3
docs/research/continuation-contract/lifecycle_boundary_falsifier.py` offline.
No native calls, no edits to frozen benchmark implementation or original receipts.

| Probe | Observed result |
|---|---|
| 49 original passive events, then final request | Exact ACKs/history; final routes out of dispatcher |
| Changed action, cancellation or appended instruction in request | No ACK and no file effect |
| Duplicate delivery | Safe rejection, not idempotent resume |
| Prior policy changed to different valid JSON, next event delivered | Next ACK accepted; prior-state integrity not established |
| Partial trailing JSON after interrupted append | Safe parsing stop, no automatic recovery |

The tampering case changes the recorded minimum approver count before the next
dispatch. Existing code checks identity duplication and sequence length, but does
not compare the previously committed archive with an independently retained root.
A fresh hash of already-changed data would not repair this binding.

This does not demonstrate actual corruption in the original W50 run or falsify
its measured counters. It falsifies treating this frozen dispatcher as a generally
restart-safe, provenance-bound lifecycle gate. Same-user malicious modification of
both data and every trusted root requires a stronger trust boundary; no local hash
scheme alone solves that. The test covers a changed archive with the original
authority presumed independently available, not adversarial control of the host.

Next implementation should reuse exact memory/epoch machinery with an explicitly
held expected state root, stable delivery identity, and transactional completion.
Same event/same payload must return its committed ACK; conflicting payload must
stop. Recovery must distinguish committed delivery from uncommitted/uncertain
effects. Unknown requests must retain the semantic path. Do not modify frozen
drivers and retroactively apply new results to their native benchmarks.

No new model call is justified by these findings alone. They identify correctness
work required before transferring the successful call-elimination mechanism beyond
its original fixture. They do not predict an additional output-token reduction.

Exact source/fixture hashes and results: [receipt](LIFECYCLE_BOUNDARY_FALSIFIER.json).
This is simulated file interruption, not a physical crash or concurrency test.
