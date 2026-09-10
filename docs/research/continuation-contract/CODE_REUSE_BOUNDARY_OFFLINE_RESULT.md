# Code reuse boundary: three lifecycle failures repaired

**OBSERVED, offline engineering evidence.** Composing existing exact code-copy
handles with `semantic_execution` exposed three failures before any new native
experiment was launched:

1. A final step changed the bound request, but execution returned
   `MECHANICS_COMPLETED`.
2. Bound state became unavailable after the final effect, but execution still
   returned `MECHANICS_COMPLETED`.
3. A binding callback raised between effects; the exception escaped instead of
   returning the completed-step receipts for reconciliation.

The original 10-case falsifier produced seven passes and these three failures.
The [before/after source and test receipts](CODE_REUSE_BOUNDARY_OFFLINE_RESULT.json)
retain exact hashes. The original source is also available at commit `b1a5293`.

## Repair

`helix.semantic-execution.v2` checks authority at entry, between steps, and after
the final step. Initial unavailable/stale authority returns `HOLD` without effects.
Changed or unavailable authority after recorded effects returns `RECONCILE`,
preserving receipts and never automatically retrying effects or invoking a model.
This changes the former between-step stale-state disposition from `HOLD` to
`RECONCILE`; adopters must handle that explicit partial-execution state.

The duplicate check immediately before step zero moved to final closure. A
successful N-step path still uses **N+1 binding callbacks**. This avoids introducing
an additional whole-state read for the repair. Actual binding time and callback
count are exposed; bytes and physical I/O depend on the caller and remain separate.

The full targeted set passes **38 tests**: code reuse, execution state and exact
copy handles. Coverage includes changed source/request/dependency/epoch, a
correctly hashed but behaviorally wrong artifact, interruption after an effect,
state loss, unchanged successful reuse and binding-read count. The two added
post-repair cases check initial unavailable state and unchanged read-count cost.
No test invokes a model. The wrong-code test executes only a hard-coded local
fixture; this is not a new API for executing untrusted model-supplied commands.

```sh
python3 -m pytest -q engine/prototype/test_code_reuse_boundary.py \
  engine/prototype/test_semantic_execution.py engine/prototype/test_copy_handles.py
```

## Scope and remaining gate

The closing check detects observed authority drift. It does **not** undo an
already completed external effect, provide a filesystem transaction, detect
every transient change-and-revert, or isolate uncooperative concurrent writers.
Publication callbacks still own their atomic state binding and durable receipts.
The supplied binding must exclude outputs legitimately modified by the operation.

Exact hashes do not establish dependency completeness or semantic adequacy.
This synthetic world enumerates its dependencies explicitly. Discovering omitted
dependencies in arbitrary repositories remains caller/model work; an opaque
manifest cannot certify its own completeness. Finite checks catch the constructed
wrong-code witness, not all semantic errors.

The repair is shared infrastructure for Luna/Sol/Astra. Frozen native benchmark
drivers do not automatically adopt it; their hashes, metrics and failed output
qualifications are unchanged. It fixes a necessary workflow-preservation condition,
not the 75/75 or 80/80 economics. No new named-plan interface, cache, reducer or
native experiment was introduced.

Before a reuse experiment, identify substantial correct code that existed before
the changed requirement and is equally available to control. Do not manufacture
cache hits or preload the solved coding fixtures. The prior exact-request census
found zero hits; it remains a reason not to build that cache for these workloads.
