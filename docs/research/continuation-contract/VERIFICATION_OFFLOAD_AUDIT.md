# Typed verification offload: zero-call cost falsifier

OBSERVED: extracted the exact semantic-test slice from Astra's final prepared-pair
command, retained its11cases, and replayed it independently against the frozen
proposal. All11pass. Removed regions perform receipt/source/snapshot/runtime
verification, preservation bookkeeping and combined reporting. This demonstrates
that those mechanics can be separated from these particular tests, not general
semantic equivalence or a complete replacement of review.

| o200k tokenizer proxy | Tokens |
|---|---:|
| Original Python body | 752 |
| Standalone semantic tests, imports and case assertion | 386 |
| Removed regions, tokenized separately | 380 |

Proxies are not native output attribution. Regions need not add under independent
tokenization; native output includes other text/reasoning. A replacement tool also
costs schema, invocation, result and possibly another model-context cycle.

## Admission decision

Matched native80%budgets:26,084.4input /411output.
CONDITIONAL: deleting the whole combined verification-and-semantic-test segment
while keeping others unchanged leaves66,169input /642output. This deliberately
optimistic sensitivity still misses both targets, and deletion would remove
useful tests. It is not an executable safe candidate or a measured counterfactual.

Even retaining only the observed final segment leaves26,469input /348output;
input slightly exceeds the26,084.4budget. This is NOT an irreducible lower bound:
the final context contains prior work and could change under another architecture.
It does show why preserving the old trajectory and trimming a single operation
cannot establish80/80.

**Do not launch a hash-verification-only80/80 pair or build a new generic tool API
on its behalf.** Reuse of deterministic verification may remain useful engineering,
but is not currently the primary route to the requested target.

## Research consequence

Three bounded modifications have now failed the target on supplied-patch review:
review timing, prepared tests, and (analytically under stated assumptions) isolated
hash offload. Stop this mechanism sequence on this fixture. Keep all negative
receipts and ordinary-tool/native fallback behavior.

The broader objective still includes representative tasks and native long-horizon
state preservation. Before further frontier calls, inventory that qualification
coverage and identify a workload where history/state reuse is an actual measured
cost. Do not inflate the control with needless repetition or call a larger easy
fixture universal success. A new mechanism needs a changed intervention boundary,
a matched control, adversarial retrieval/recovery and full creation/reuse costs.
No future experiment has been claimed successful or automatically admitted here.

Machine artifact:`VERIFICATION_OFFLOAD_AUDIT.json`.
Reproduce:
`python3 docs/research/continuation-contract/verification_offload_audit.py /path/to/native-prepared-pair-v1-20260909 /tmp/result.json`.
Script checks the frozen event hash and records exact extraction identities.
No native model calls; no frozen suites, inputs, implementation or policy changed.
