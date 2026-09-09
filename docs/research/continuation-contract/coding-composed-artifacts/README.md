# Exact coding artifacts

`off/` is the fresh native implementation; `on/` is the exact Helix candidate.
The synthetic task, original files and protected files are supplied. Source hashes
match the published native-pair report. Private raw transcripts are not included.

With a repository checkout, run:

```sh
python3 docs/research/continuation-contract/coding-composed-artifacts/verify.py
```

The verifier uses only the Python standard library and pinned existing auditors.
It checks source hashes, four public tests, the 4,433-case oracle, 1,213 additional
large-integer/container cases and 18 invalid cases per implementation. It invokes
no model or service and stages all execution/results in a temporary directory.
Frozen source and report files are not rewritten.

This reproduces code behavior, not provider usage or general intelligence/workflow
parity. Additional domain checks were developed post hoc.
