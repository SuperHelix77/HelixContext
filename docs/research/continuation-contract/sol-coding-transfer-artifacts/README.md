# Exact Sol coding artifacts

All six implementations, original task sources and protected tests/settings from
the fresh Sol High coding transfer. Native counters are extracted, hash-bound
receipts; they are not independently authenticated provider attestations.

```sh
python3 docs/research/continuation-contract/sol-coding-transfer-artifacts/verify.py
```

The verifier checks hashes and native-source bindings, then reruns the frozen
public and independent behavioral checks in fresh processes. No model invocation
is required. The model-generated implementations are executable code; inspect
them before running outside a trusted research checkout.
