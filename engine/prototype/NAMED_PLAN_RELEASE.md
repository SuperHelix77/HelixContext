# Explicit snapshot release: measured development increment

Declared input/script/schema/config bytes are now archived at registration in the
existing content-addressed store. A manifest's source hash therefore resolves to
exact bytes even after the original file is removed. Deduplication does not avoid
the cost of reading and verifying an existing object; store counters include it.

`release_inputs(store, ref, attempt_hash)` is an explicit lifecycle operation,
never automatic after command success. The caller must have exclusive ownership
and establish that all consumers of the workspace input paths have finished.
Generated outputs can refer to those paths, so automatic removal could break a
workflow even when the command has exited zero.

The operation requires an accepted successful attempt, validates all archived
sources and input snapshots before deletion, and preserves task-created outputs,
source objects and process evidence. Failed attempts or changed snapshots are not
released. OS deletion failure can produce partial cleanup, explicitly recorded in
a separate receipt; it does not rewrite execution success. Cleanup is not a
transactional filesystem primitive and is not safe against hostile concurrent
writers. This limitation is distinct from plan publication's transactional DB.

## Retained-evidence measurement

`named-plan-release-results.json` reports seven repeats per workload. Its script
produces only stdout; exact comparison completes the last workspace consumer.
Plan timings include release cost. Source creation/archival is included in total
costs, and release receipts report their own reads and validation.

| Input | Ordinary median | Plan + release median | Ordinary retained | Plan retained |
|---|---:|---:|---:|---:|
| 256 B | 27.81 ms | 30.93 ms | 11,035 B | 59,753 B |
| 1 MiB | 27.65 ms | 38.42 ms | 11,093 B | 1,108,329 B |

Relative to the earlier plan implementation's 7,395,764 retained bytes on the
large case, this increment retains about 85% fewer bytes after seven completed
uses. This is a development before/after logical-storage observation, not a
token-saving percentage or a latency claim. Small-case storage increased because
archival and cleanup receipts cost more than the tiny snapshots they replace.
Neither case has a finite latency break-even on its measured medians.

All 28 command outputs matched the expected exact hash and exited zero. The full
prototype suite passed 109 tests, including recovery after original deletion,
output preservation, changed/corrupt evidence rejection and partial cleanup.
These tests do not establish intelligence parity. The ctime-only invalidation
from the prior experiment remains unresolved and was not waived.

Reproduce with a fresh artifacts directory:

```sh
python3 engine/prototype/benchmark_named_plans.py \
  --output /tmp/helix-plan-release-results.json \
  --artifacts /tmp/helix-plan-release-new-artifacts --release-inputs
```

Automatic admission remains closed. Native input/output savings, model creation
costs, universal TOCTOU isolation and complete physical I/O accounting remain
unverified. The next gate is a model-visible invocation interface and a bounded
paired experiment that measures command-generation savings against these costs;
the storage result alone is not a reason to promote a policy.
