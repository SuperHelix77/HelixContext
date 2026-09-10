# Exact closed-retrieval artifacts

Complete synthetic sources and answers from [the paired result](../LUNA_RESOLVED_RETRIEVAL_RESULT.md).
Private memory, configuration and raw native conversations are excluded.

From the repository root:

```sh
python3 docs/research/continuation-contract/resolved-retrieval-artifacts/verify.py
```

Checks file/implementation hashes, reopens the exact evidence store, replays
the bound operation with inference forbidden, and compares both saved answers
with the frozen independent SQL/index oracle. This verifies artifacts and
deterministic behavior, not provider-counter authenticity or general capability.
