# Actual generated test coverage: a counterexample to suite equivalence

**OBSERVED offline replay; not counterfactual model verdicts.** No new native calls.

The valid-pair arms accepted the same correct source. Their generated supplemental
tests were not identical. This audit extracts the native arm's actual fileChange
addition and the candidate's actual semantic command slice from hash-verified raw
receipts. Candidate path/import adaptation is documented in the machine result;
mechanical receipt/hash checks are excluded from the semantic slice.

| Source | Common checker | Native supplemental | Helix supplemental |
|---|---|---|---|
| Correct reference | PASS | PASS | PASS |
| Shared initial storage across instances | PASS | FAIL | PASS |
| Stale cursor after alias mutation | FAIL | FAIL | FAIL |
| Self-alias batch incorrectly ignored | PASS | FAIL | FAIL |
| Bool incorrectly accepted | FAIL | PASS | PASS |

All variants are post-hoc development probes, not a sealed mutation holdout.
The shared-storage defect has a contract witness independent of test content:
construct queue A, append [7], construct queue B; B incorrectly begins with [7].
The public contract says new queues begin empty. The common state-transition
checker constructs only one queue per freshly loaded source, so it misses this
cross-instance behavior. The native supplemental suite explicitly checks distinct
initial storage; the candidate suite does not exercise two simultaneous queues.

**Consequence:** the 50.20% output saving cannot be described as established
verification-coverage parity. This does not establish that Astra would accept the
mutant during a fresh source review; no model saw that mutant in this audit.
The original valid-pair usage, correct-artifact PASS and final ACCEPT judgments
remain unchanged. No retrospective regrade is applied.

A separate prospective checker, `check_queue_independence_v1.py`, now verifies
1,000 three-action interleavings / 3,000 transitions over two live queues, with
fresh-instance checks after each action. Correct reference passes; shared-storage
mutant fails. It does not replace or amend any frozen checker, claim exhaustive
Python correctness, or certify model intelligence. Future experiments must bind
its version and provide equivalent evidence/check availability to both arms.

Machine results: `SUPPLEMENTAL_COVERAGE_RESULT.json`. Replay script:
`supplemental_coverage_audit.py`. No model token was spent to discover this gap.
