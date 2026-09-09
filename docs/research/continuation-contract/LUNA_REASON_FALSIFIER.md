# Luna reason-code interface: hostile adjudication

OBSERVED: the frozen W50 grader accepts a semantically false explanation.
With the exact correct historical fields, `WRONG_GROUP` renders a claim that the
requested group differs from violet. E50 explicitly requests violet, so this
claim is false. The frozen grader nevertheless passes it because it checks only
nonempty explanation text alongside factual fields. See the reproducible JSON.

This is an offline adversarial checker test, **not an observed model error**.
The actual V3 recovery selected `INSUFFICIENT_APPROVERS`: one is less than two,
so it survives this additional obligation check. The earlier finite-result claim
is retained; any stronger conclusion that the interface was fully validated is
unsupported. No native traces, frozen drivers or graders were modified.

Added `reason_obligation_check.py` as a separate prospective research gate.
Nine tests cover true/false rejection reasons, changed request count/group,
new unsupported obligations, invalid boolean-as-count data, positive authorization
and unsupported reason codes. Positive authorization stays unresolved because
count/group checks alone cannot prove that all authorization requirements hold.
The checker assumes caller-validated request/policy bindings; it does not establish
source authority or dependency completeness. It is not yet wired into a native
runner or production. First test collection failed on pytest's reserved argument
name `request`; renamed the test parameter and all nine checks passed.

No additional native call was spent. The next experiment must freeze the exact-ID
adapter plus this independent reason gate before inference. Another wording-only
attempt is not supported by the observed188reasoning/40otheroutput decomposition.
Safe semantic reuse would need fresh changed-request, changed-policy, and
latent-relevance cases with exact dependency invalidation, plus full creation and
recovery costs. It cannot be assumed from this receipt-only fixture.
