# Differential obligations: offline admission before inference

2026-09-10. This is a bounded research adapter, not a new model-facing API,
semantic cache or production policy. No native experiment is authorized by this
file alone. The user has authorized experiments after research and offline gates.

## Measured cost and hypothesis

In native-final V1, Astra XHigh generated and executed a new semantic-probe program
in a segment costing1,187 output tokens. In the later exact-regression-reuse review,
both arms generated a12-record old/new comparison that found a default-limit
regression missed by the supplied tests. Those whole segments are mixed; none of
their total cost may be relabeled removable mechanics.

The task explicitly requires existing calls and search behavior to remain intact.
That permits a caller to compare declared unchanged behavior with the pre-change
implementation on enumerated inputs. It does not permit a caller to decide that
every old behavior is desirable, every difference is wrong, or every pass proves
the new implementation correct.

Hypothesis: compile already-explicit relations into deterministic checks, provide
their exact cases/results before Astra would have to generate the same probe, and
retain Astra's authority to challenge the relations or add probes. The final
answer remains entirely model-written after execution evidence. New semantic
obligations remain with Astra.

## Research precedent, not Helix economics

McKeeman describes differential testing as comparing comparable programs on
generated inputs; disagreements expose candidate bugs. Test generation still
requires domain knowledge, and legitimate differences must be distinguished from
faults. This supports the mechanism, not a universal equivalence claim or token
prediction. [Differential Testing for Software,1998,pp.101–102](https://www.cs.tufts.edu/comp/150FP/archive/bill-mckeeman/DifferentailTesting.pdf)

Metamorphic testing evaluates relations between multiple executions, derived from
the specification. The relation must be justified; finite agreement is not full
correctness. [Liu et al.,2014,§§I–II](https://vuir.vu.edu.au/33046/8/TSEmt.pdf)

The1998 original metamorphic report was located but its extracted PDF text was
garbled; this review relies on the readable2014 primary paper for that description.

## Frozen relation scope

- Legacy calls: baseline and candidate return equal ordered records or equal
  exception type/message, on the same exact generated input/state.
- Explicit `all`: equals the existing literal AND search on valid inputs.
- `any`: equals the union of baseline single-literal-word queries, ordered by the
  existing ordinal rule and then limited. The bounded corpus stays below the
  baseline100-result ceiling; this relation is not applied outside that bound.
- Invalid new modes: must raise ValueError even for an empty query, per TASK.md.
- Search observations must leave event/index tables unchanged.
- Corruption outside the returned limit still triggers the legacy integrity error;
  unrelated project state is not promoted to current project authority.

Generator parameters come from the baseline signature and the task's existing
validation bounds. Corpus includes sizes around the default limit, two projects,
literal operator words, Unicode, punctuation, blank queries and invalid arguments.
No candidate expected answers, generated patch, model assessment, private reasoning
or previous solution enters the generator. It uses the actual before implementation
as a compatibility oracle only for the explicitly preserved behavior.

## Offline falsifiers and controls, declared before execution

Run on the already exposed valid source and known default-limit defect, then
constructed variants: reversed ordering, wrong default mode, missing integrity
check, wrong default alone on `any`, invalid-mode validation after empty return,
and a query-specific defect outside this finite corpus. The last must survive
these cases and remain a documented coverage hole; do not add its trigger after
seeing that it survives. These constructed variants are development calibration,
not holdout evidence or independent replication.

Require stale source/task bindings to reject before candidate execution, changed
bindings during execution to prevent a valid receipt, exact full outcome recovery,
explicit differences without automatic acceptance/rejection or patching, a
read-only source check, and a measured bounded process cost. Failures/unknowns may
not become a pass. The adapter runs trusted local research modules in disposable
stores; it does not establish hostile-code sandbox isolation.

## Native admission remains separate

Before any native call, inspect which actual observed commands/results the packet
can replace and account for generator setup, reads, storage, callback/schema and
additional model-review costs. Do not remove a whole mixed segment or reuse an old
control as a measured denominator. No80/80 or65/65 prediction follows from passing
this offline suite. If the remaining ordinary full final and semantic work dominate,
do not spend a new pair merely to celebrate better test coverage.
