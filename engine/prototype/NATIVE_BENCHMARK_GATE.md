# Native benchmark accounting gate

The six latest query-V2 native traces were reread and their SHA-256 values matched
the published result rows. Each contained exactly one completed-turn usage record,
matching both its result row and local status receipt. Recorded model/High effort
were checked. `NATIVE_RECEIPT_RECHECK.json` retains the numerical comparison.
This rechecks existing development evidence; it is not a fresh experiment.

| Model, High | Input saved | Output saved | Both ≥80% |
|---|---:|---:|---|
| Luna | -3.54% | -0.19% | No |
| Sol | 49.57% | 50.00% | No |
| Astra | 25.67% | 38.63% | No |

The historical common runner uses zero defaults for absent optional usage fields
in multi-turn summaries and does not compare requested model/effort on its cached
resume branch. Neither issue changed these six rows: their checked optional
fields were present and recorded identities matched. The historical runner was
not modified or re-executed.

`native_usage.py` supplies validation for the next runner: missing required input
or output rejects accounting; optional missing categories remain null; cached
resume requires completed status, matching model/High effort and exact prompt.
Five new tests passed; full suite: 128 tests. Future runner integration is still
required. A helper existing on disk does not mean legacy launches use it.

Before another launch, freeze a concrete candidate and fresh fixture/checker,
include skill/bootstrap and fallback costs, and enforce the validator in the
runner. Limit the first diagnostic to one model and one paired task (two calls),
with a predeclared token/time budget and no automatic expansion. A favorable pair
would authorize consideration of the requested larger three-model/three-task
comparison, not establish capability parity. Previous experiments must not be
relabelled as tests of the newly implemented memory or named-plan engine.
