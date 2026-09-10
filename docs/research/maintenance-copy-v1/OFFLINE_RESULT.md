# Maintenance coding: offline gate passed, native economics unmeasured

The earlier coding candidates had no remaining tools/continuations to remove and
had to implement almost all behavior from tiny stubs. This experiment instead uses
the real 10,027-byte Helix Memory module, frozen at `e578dcd` before defining the
new search-mode change. Both arms will have the same original implementation,
dependencies and public tests. This family cannot replace the failed coding cells.

**OBSERVED, offline:** calibration passes 23 existing/public tests and 94 independent
query/validation/recovery cases on the reference. The original implementation and
seven wrong variants are rejected: always-AND, always-OR, absent mode validation,
cross-project leakage, wrong ordering, skipped integrity checks and raw FTS syntax.
Exact reference code stays in the private calibration directory, outside both
future model workspaces. This is investigator-authored development, not a holdout.

The initial proposed method-copy recipe was larger than necessary:

| Representation of investigator reference | Bytes |
|---|---:|
| Complete replacement source | 10,208 |
| Method copy recipe | 1,146 |
| Standard unified diff | 1,042 |
| Exact old/new edits | 518 |

**DECISION:** use the small `literal_edits` adapter over the existing renderer.
The model provides every semantic edit. Engine locates unique original byte spans,
rejects overlaps, and assembles untouched bytes with new literals. No fuzzy matching,
cascading substitutions, automatic code repair, model-supplied paths or execution.
The same primitive can replace the entire file when broader changes are needed.

**34 focused tests pass**, covering literal edits, the existing renderer and code
reuse authority boundaries. These include duplicate JSON keys, overlapping matches
(including overlapping occurrences within one anchor), stale/corrupted source,
Unicode and exact untouched bytes, full replacement/deletion, output-size rejection,
changed authority and interrupted publication. The calibrated reference assembled
byte-identically; its copied/literal bytes, retrieval traffic and assembly time are
in [the receipt](OFFLINE_CALIBRATION.json). Total calibration took 1.578 seconds on
this run, excluding investigator development; no model call occurred.

No 80/80 prediction is made. Native already has efficient editing tools; familiar
old/new edits may still increase model integration/reasoning or repair cost. The
[prospective protocol](PREREG.md) requires one fresh randomized Astra High pair,
frozen concrete prompts/runner/configuration before launch, and all attempt costs.
The concrete runner and independent receipt auditor are now written. **38 focused
tests pass**, adding actual baseline grading, protected/untracked-file rejection,
stale-source versus malformed-edit recovery separation, and checker mutation.
Global model/config defaults and earlier frozen benchmark implementations remain
unchanged; the new search feature is not installed in the Engine.
