# Prospective selection gate V2

The preceding renderer pilot had an evaluator coverage gap: approval and expiry did not vary across revisions within a group. An implementation that filtered eligibility before selecting the latest published revision could therefore produce the same answer. Its passing model results remain bounded by that limitation.

This replacement fixture makes the distinction observable. Groups include newly revoked approval, newly expired records and a string-valued approval on the latest revision. It also includes unpublished later revisions, string/integer publication flags, integer approval, the exact expiry boundary, unsorted input, mixed JSON whitespace, CRLF/LF and Unicode representations.

The expected IDs are fixed independently of the positive-control selector. The evaluator binds its original source to the frozen generated fixture, then requires exact selected bytes and unchanged input. It rejects substitution of a different original rather than silently accepting a changed contract.

## Verification

```sh
python3 -m pytest -q engine/selection-gate-v2/test_gate.py
python3 engine/selection-gate-v2/gate.py
```

**13 tests pass.** The reference selector matches the frozen IDs. Ten wrong implementation mutations are rejected, along with source mutation and substituted-original attacks. `mutation-results.json` records hashes and individual outcomes.

These are evaluator tests, not native model benchmarks. No prior model score has been upgraded or regraded using this fixture. The fixture and code are published, so future use is a transparent regression gate, not a secret holdout. A fresh held-out evaluation and all three requested task families still remain necessary.

Native interception testing remains separately pending temporary-observer approval. Nothing in this gate activates hooks, changes model settings or establishes 80% savings.
