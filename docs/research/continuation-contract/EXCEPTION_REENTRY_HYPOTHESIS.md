# Semantic self-review plus exception-driven re-entry: next falsifier

Status: **HYPOTHESIS ONLY. No automatic-completion policy activated.**
User steering proposes preserving semantic review before execution and waking the
model afterwards only when execution changes the semantic problem.

## Evidence correction

The 80.29% input / 65.90% output caller-patch pair generated a repair from broken
source. The 13.42% / 50.20% pair reviewed a supplied valid proposal with different
prompts and mechanics. They are not a matched ablation of review timing. The latter
candidate had one native user turn containing five model segments, not an extra
separate user turn. A matched timing test is needed for causal attribution.

The safety challenge establishes rejection during a post-execution review of a
known defective proposal. It does not establish that pre-execution self-review
would fail or succeed. The new generated-suite coverage gap further rules out
using common-check PASS as a substitute for testing semantic reconsideration.

## Responsibility boundary to test

- Caller binds task, source, checker, environment scope, state revision and allowed
  operations before inference; capabilities are already attached.
- Helix Context preserves the objective, exact-evidence access and semantic
  responsibilities. It does not teach a new opcode language or require bookkeeping.
- Astra assesses the proposed patch and explicitly states acceptance/rejection,
  assumptions, expected check outcomes and unresolved obligations. These are
  externally auditable commitments, never private reasoning traces.
- Engine applies only the authorized exact proposal in isolated state and checks
  the declared predicates. It records exact outcome/delta and side-effect status.
- Caller may close only within a prospectively qualified task/policy cell when
  commitments are complete, state still binds, all mandatory checks were actually
  executed, actual outcomes match expectations, and no obligation remains.
- Otherwise retain exact evidence and re-enter Astra with changed facts and the
  unresolved question. An unqualified cell keeps ordinary review/native bypass.

“New semantic information” is a model-facing description, not a general property
that deterministic code can decide. Engine can compare declared expectations and
tracked dependencies. It cannot prove that all relevant assumptions/dependencies
were declared, or infer that no semantic defect remains because bytes match.
Unexpected absence of required evidence also triggers re-entry; a missing check is
not an expected PASS. Failed or uncertain side effects require reconciliation,
not blind rerun. A version change invalidates reuse even if bytes later revert
unless a fresh authority revision explicitly permits it.

## Minimal timing comparison

Use the same supplied proposals, contract, allowed tools, declared checker set,
source evidence and requested final assessment in both timing arms. Keep High
reasoning. Compare pre-execution semantic review + authorized mechanical closure
against execution + semantic review, with exact retained evidence in both. Do not
reuse old unrelated controls or inflate control commands.

Before economics, challenge both timing policies on a mechanically passing
semantic defect without embedding the expected verdict in paths/prompt. Include
cross-instance storage as well as alias-state semantics; those known probes are
development, not holdout. Independent semantic grading must assess the actual
counterexample/commitment, not just an ACCEPT/REJECT string.

Separately inject an authority amendment after initial review but before execution,
and an unexpected actual check outcome. Correct behavior is refuse stale execution
or request semantic re-entry, preserving the entire earlier evidence and counting
recovery costs. A simulated wake flag alone does not prove agentic recovery: a
native continuation must actually receive and resolve the changed obligation.

All actual model segments, setup, checks, snapshots, retrieval and recovery costs
belong to the arm. No output cap or narrower reasoning request. Adverse cases must
not be used as savings denominators. If pre-review misses a semantic defect caught
by the matched post-review arm, reject closure for that cell. If re-entry is lost,
state is stale, evidence unavailable or effects duplicated, reject the design.

A successful development pair is still not broad no-loss evidence. Next would be
fresh held-out repair and long-horizon cases, including latent future relevance,
with the requested model/task matrix. Those requirements remain unfulfilled.

## Immediate engineering prerequisite

Use the existing runner's live thread for true re-entry; it currently closes after
one turn. First verify continuation cumulative-token accounting and failure
persistence without inference. Do not claim a second fresh isolated thread is
state-preserving recovery, and do not launch a timing benchmark with a fake
continuation. This is the specific next implementation investigation, not authority
to build a broad router, learned summarizer or certificate framework.
