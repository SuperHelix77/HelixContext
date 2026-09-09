# Continuation evaluator: alias-safe state and exact cold recovery

**OBSERVED, offline only.** This new task preserves the public-alias failure found
by Astra and makes state ownership explicit. It does not change the stopped
pilot's contract, control, grade or result. No new native calls, Engine code,
runtime settings, skill instructions or production routes were changed.

`CONTRACT.md` expressly permits between-call alias mutations. Successful calls
synchronize the cursor to actual list length; failed calls preserve even a stale
entry cursor. Empty batches synchronize without appending. Iteration may observe
entry state, so eagerly mutating while consuming input is invalid. Reentrant or
concurrent mutation is explicitly outside this new synchronous task's domain.

## Evaluator checks

The independent transition oracle covers **2,745 sequences / 8,282 transitions**:
all length-three sequences from 14 actions plus one delayed 50-action trajectory.
It separately maintains expected list content and last successful count. The
reference implementation passes. Eight mutants are rejected: stale cursor,
bool/subclass acceptance, reversed order, list replacement, double consumption,
empty-batch failure to synchronize, eager mutation and wrapped iteration errors.
The test distinguishes actual `__iter__` entry failure from failure in `__next__`.
Concrete mutation witnesses and hashes are in `RESULT.json`.

This is finite offline evaluator qualification—not proof of all Python behavior,
not 2,745 model tasks, and not the required adversarial 50-turn model-memory test.
The small reference implementation is checker qualification data. It must not be
secretly supplied only to a Helix arm in a future repair benchmark.

## Existing memory integration

`memory_preflight.py` uses the current Engine Memory/Epoch modules without edits:

1. Record contract v1 plus 39 intervening observations and freeze their exact root.
2. Introduce a later batch-size constraint and freeze a distinct version.
3. Delete the complete mutable search/events index.
4. Recover both contracts byte-for-byte from their respective pinned roots.
5. Reject a later record requested through the older epoch; do not silently rebuild
   the index or label the old contract current.

All five assertions passed. Reading the original **2,190-byte** contract required
**12,247 logical object bytes** across three object reads: about **5.59×** read
amplification. Initial old/new freezes additionally read 35,885 / 41,246 bytes and
wrote 9,805 / 10,050 bytes. These costs remain charged; physical/SQLite I/O and
coordinator inference are not fully measured. This fixture cannot establish an
improvement over the prior 18.68× result because its object sizes differ.

The delayed version reference is selected by the caller in this test. Automatic
model relevance discovery, semantic invalidation, native recovery behavior,
compaction-skill restoration and production transactionality remain untested.
A hash difference exposes changed authority; it does not decide its semantic
meaning. The existing epoch is an evidence mechanism, not a semantic decision cache.

## Reproduce and next gate

```sh
python3 docs/research/continuation-contract/audit.py /tmp/continuation-audit.json
python3 docs/research/continuation-contract/memory_preflight.py /tmp/new-continuation-store
```

The memory script requires a new store directory. Its result is written beside the
script; do not overwrite published measurement files when collecting later runs.
`RESULT.json` and `MEMORY_RESULT.json` retain current measurements and implementation
hashes. Preparation is not free and must be included in any amortized benchmark.

Before another native launch, define a matched continuation sequence, how exact
state/evidence reaches each arm, a common semantic output contract, and the minimal
caller action that replaces measured discovery/binding work. Keep current tools
and Astra High. Charge initial preparation and each continuation/recovery. Do not
inflate the native baseline with forced separate calls that native batching could
avoid. Do not present repeatable deterministic fixture checks as intelligence
parity. The 80% input AND output objective and representative three-model/long-
horizon gates remain open.
