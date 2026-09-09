# Named-plan overhead falsifier

This is an offline command benchmark, not a model-token benchmark. The workload
hashes a fixed input using the same Python script in both arms. Ordinary execution
uses the existing checked executor; plans add dependency checks and snapshots.
Both arms capture exact output and exit status. Seven repetitions alternate arm
order. No model calls occur.

## Retained-evidence run

| Input | Ordinary median | Plan median | Additional latency | Retained ordinary / plan |
|---|---:|---:|---:|---:|
| 256 B | 28.00 ms | 29.46 ms | 1.46 ms | 11,049 / 57,376 B |
| 1 MiB | 30.50 ms | 38.18 ms | 7.68 ms | 11,108 / 7,395,764 B |

All 28 command outputs matched exactly and exited zero. Creation is included in
the report's total times, not the per-execution medians. On these observed medians
there is no finite latency break-even: recurring plan execution is more costly.
Storage includes repeated snapshots and receipts; it is logical file size, not
physical disk traffic. The control provides weaker dependency isolation, so this
measures the incremental infrastructure cost of the plan guarantees.

`named-plan-overhead-results.json` contains individual samples, source hashes,
creation costs, byte counters and a retained-artifact hash manifest. Reproduce:

```sh
python3 engine/prototype/benchmark_named_plans.py \
  --output /tmp/helix-plan-results.json \
  --artifacts /tmp/helix-plan-new-artifacts
```

Use a fresh artifact directory. Caches are uncontrolled and no confidence interval
is claimed. The initial exploratory run discarded raw temporary artifacts; it is
superseded by this retained-evidence run, not pooled with it.

## Failed Documents-directory run must also count

A separate run under the project Documents directory stopped on a failed plan
attempt. Inspection found identical SHA-256, inode, size, mtime and mode, with
changed ctime. Three plan attempts had succeeded before one was rejected. The
source of the metadata change is unknown. Exact receipts remain under the path
in `named-plan-metadata-rejection.json`.

The later temporary-directory success does not erase this workflow failure or
prove directory placement caused it. Strict ctime binding detects write/restore
but can also invalidate unchanged content. Do not remove the check without an
alternative that passes the already-required write/restore falsifier.

## Decision

Automatic plan admission remains closed. Native token costs are unknown; any
future reduction in command generation must pay for these measured costs plus
creation, validation, storage and recovery. Next design work must address benign
metadata invalidation and snapshot retention before claiming workflow parity.
No 80% input/output or intelligence-preservation result follows from this test.
