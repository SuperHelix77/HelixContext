# V2: reviewable mechanics, unchanged semantic authority

This is a small interface correction justified by the audited V1 maintenance
traces, not a released model profile. Original V1 scripts, prompts, receipts and
failures remain intact. **No V2 native inference has been run.**

Two independently selectable presentation changes:

1. `source_presentation=literal_blocks_v1`: show the same exact UTF-8 task files in
   bound literal blocks instead of JSON-escaped source strings. Filename/version/
   length/hash remain explicit. Closing fences cannot collide with source content;
   any display-only final newline is declared. No source selection or summarization.
2. `review_receipt=bound_diff_v1`: retain the V1 internal tool and exact matching,
   checks, publication and recovery. Add a deterministic diff of the immutable
   before/after sources to its actual result. Small diffs are complete; larger
   diffs carry an exact cold object reference and an explicit incomplete-view flag.
   The same final answer remains model-written after execution.

Neither change grants semantic authority to the Engine or suppresses ordinary
tools/probes. The diff is review evidence, not a certificate of adequate tests.
The caller still binds code, task, state, checker and protected dependencies before
execution. Failed, uncertain or stale execution cannot become a success receipt.
The review adapter extends the frozen V1 lifecycle rather than inventing another
plan API. Production policy must bind the adapter's version in the caller manifest.

## Offline falsifier results

`OFFLINE.json` replays the **original V1 proposals unchanged**. Both final source
artifacts remain byte-identical to V1 and pass the same 23+94 finite checks. Applying
the returned diff to the original bytes independently reproduces each publication.
Sol's original over-escaped large selector still fails before publication: there
is no automatic escape repair or substituted model decision. Whether the clearer
source display prevents that model mistake in a new run remains a hypothesis.

Eleven focused tests pass for exact source recovery (backslashes, fence collisions,
CRLF, Unicode, missing terminal newlines), bad inputs, native-style duplicate/restart,
failed selector, large diff cold storage, and interrupted diff archival after the
publication effect. Recovery of that last case closes the retained publication
without rerunning the checker or applying the edit again.

This is **not literal compression on the fixture**: the source presentation grows
from28,345 to28,482 bytes. The intended benefit is clearer exact transmission.
The receipt grows from349 to1,798 bytes for Astra and1,860 bytes for Sol. Full diffs
are1,058 and1,119 bytes. Those are real recurring input costs and are not hidden.

Offline logical store reads are63,140/73,120 bytes and post-constructor writes
17,505/20,204 bytes; each constructor additionally writes/hashes the10,027-byte
initial source. The offline replay takes approximately0.662/0.620 seconds including
checks/diff application. These boundaries differ from native whole-run timing;
staging/SQLite/physical I/O remains incompletely metered. No monetary or quota saving
is established by a byte count or by these offline timings.

## Adjudicated next experiment

One newly frozen fresh Sol High pair on the same known maintenance contract can
test the correction with ordinary model-written final answers. Keep the current
model/effort, checker, source, protected scope, tool authority and ordinary tools.
Enable only the two switches above; do not add a new kernel, compact final schema,
probe suppression or hidden helper. Controls are fresh; V1 stays reported.

Primary mechanistic falsifier: does Sol still create a separate diff/source/scope
inspection segment, or generate an incorrect long selector and repair segment?
If so, the anticipated removed work did not materialize and the extra receipt must
be charged as overhead. If it does not, compare full native input/output/uncached,
final-answer completeness, task checks and all attempts. Do not score a predicted
missing segment as a native token saving. A 75/75 maintenance result is desirable,
but only a full fixed cohort can meet the user's **median** release gate.

Stop on any capability/content/scope regression, broken source/authority binding,
unexplained native counters, or config drift. Preserve interrupted state; do not
retry inference to repair instrumentation. If the policy just adds bytes and does
not remove observed work, reject it as an economic policy. If it safely removes
work but misses the per-area target, retain the measured result and complete the
predefined cohort rather than retune this same fixture indefinitely.

Astra's semantic probes remain valuable and outside the deletion hypothesis.
Its next research question is whether model-authored probes can accompany the
initial edit and execute before publication, preserving their semantic content
while avoiding another context cycle. That extension is **not implemented here**;
first establish whether this smaller interface correction improves Sol.
