# Luna coding V1: frozen candidate

This exports the exact client-base kernel and caller requirements used by the
fresh measured candidate: **86.17% input / 79.06% output / 62.04% uncached input
savings** on one known allocation-repair task. Both arms passed the finite checks.
It is not a general coding release or a standalone production caller.

`profile.json` binds `base.md` and lists the mandatory caller contract. A future
adapter may supply this file through the thread-local `model_instructions_file`
setting. Do not install it globally or assume the skill alone reproduces the
result: caller preflight, exact source preparation, checks and publication were
part of the measured system. Unsupported operations keep ordinary semantic
execution inside Engine. Ordinary tools and needed probes remain available.

The source-only research reference is
[luna_coding_decision_v2.py](../../../docs/research/continuation-contract/luna_coding_decision_v2.py),
with task-bound preflight in V3 and thread-local kernel composition in
[luna_coding_composed_v1.py](../../../docs/research/continuation-contract/luna_coding_composed_v1.py).
Those runners contain fixture-specific preparation and grading; they are not the
production API. Exact public evidence and remaining gates are in the
[freeze receipt](../../../docs/research/continuation-contract/LUNA_CODING_V1_75_FREEZE.json).

The explicit 80/80 objective remains open: this fresh output result is 79.06%.
Further same-fixture tuning stops at the user's accepted 75/75 candidate threshold.
Prospective varied-task qualification, W50 closure and application delivery are
still required before a model-wide release.
