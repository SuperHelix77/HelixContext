# Named-plan development status — 2026-09-09

Implemented in the isolated named-plans branch, not installed or native-model-qualified.

`named_plans.register` freezes a manifest under `(plan_id, plan_version, plan_hash)`;
`invoke` checks declared dependencies, snapshots files, captures each required step,
stops after failure and publishes the accepted-success pointer transactionally.
`creation_cost` and returned invocation/publication fields expose partial costs.
`plan_costs.break_even` computes the first strictly profitable integer reuse count
for one cost unit with constant recurring costs; unknowns remain unknown.

Verification: `python3 -m pytest -q engine/prototype` — 103 passed. New tests first
failed for absent cost arithmetic, noncanonical paths, unclosed DB connections,
registration closure races and changes during attempt archival. Fixes passed the
full suite. These are infrastructure tests, not intelligence or token benchmarks.

Two newly reproduced invalid-success cases were corrected: a source change while
archiving a manifest now rejects registration; a source change while archiving an
attempt now creates a failed receipt and preserves the previous success pointer.

## Unresolved gates

- [Explicit snapshot release](NAMED_PLAN_RELEASE.md) now preserves archived source
  bytes while reducing repeated large-input retention after caller-confirmed
  workspace completion. Full suite: 109 passed. Latency still regresses; this is
  not a native token-saving result.

- [Offline overhead falsifier](NAMED_PLAN_OVERHEAD.md): both tested workloads
  incurred positive latency/storage overhead; a separate retained run rejected
  unchanged content after a ctime-only change. Automatic admission remains closed.

- Source checking and SQLite commit cannot be atomic with noncooperating filesystem
  writers. Snapshots protect declared file inputs but execution is not a sandbox;
  executables, undeclared host reads, libraries and external side effects remain
  outside full isolation. The strong general TOCTOU requirement is not established.
- Creation accounting omits final registration commit; repeated registrations,
  failed registrations and all SQLite/physical I/O are not fully metered. Final
  publication timing/validation is returned separately, not durably self-included
  in the attempt hash. Keep total cost and native token savings unverified.
- An [explicit CLI/skill bridge](PLAN_CLI.md) now passes subprocess checks; full
  suite: 113 passed. Installed activation, durable complete telemetry and
  adversarial independent review remain pending. Do not enable automatic reuse.
- No native model calls were made in this increment. The 80% input/output target
  and general capability/workflow parity remain unproven.

Next: close accounting and execution-isolation boundaries before freezing a
bounded native paired plan-reuse benchmark. Preserve ordinary agents' access to
equally efficient scripts/copy tools; include creation costs in both arms.
