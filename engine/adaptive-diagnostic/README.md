# Diagnose before spending more native tokens

This replaces the sequence of ad hoc one-pair trials with model-and-task-specific candidate selection and direct composition tests. It does not deploy a winning policy based on one favorable result.

## What the existing receipts support

- Luna: renderer-assisted exact assembly is a candidate worth confirming. Typed terminal projection regressed; it should not be assumed beneficial merely because Sol improved.
- Sol: typed terminal projection is a candidate, but the same task's ordinary control varied substantially across runs. Renderer-assisted assembly regressed and should not be included indiscriminately.
- Astra: request-conditioned exact evidence is a candidate for diagnosis. Exact renderer assembly regressed. These results support different investigation priorities, not universal model personality claims.

`results.json` preserves every included comparison and source hash. Same-task control ranges are descriptive across development runs; they are not randomized variance estimates or confidence intervals.

## Structural diagnosis

The V1 query compiler missed compound identifiers. V2 fixes this, but the completed V2 models still inspect the source. Improving coverage did not eliminate source verification. Therefore a smaller packet or better lexical recall is insufficient evidence that a model round trip was removed.

A packet can add cost when the agent performs its ordinary check anyway. A renderer can add planning/setup cost when ordinary scripting already copies the exact bytes efficiently. A full-source range lookup can reread the source repeatedly; batch retrieval addresses that I/O cost, but its token benefit remains unmeasured. Each is a distinct mechanism and should be diagnosed separately before being combined.

## Concrete change in method

1. Reuse existing traces and deterministic tests to reject implausible mechanisms before launching models.
2. Select by both model and workload. Unknown tasks use ordinary execution. No extra model call for routing.
3. Keep candidate selection separate from independent validation. Do not optimize and certify against the same exposed task.
4. Test combinations directly against a matched efficient baseline. Savings do not compose arithmetically; interactions, repeated verification and fallback can erase them.
5. Predeclare a bounded experiment and stop rule. Do not launch a full three-model matrix after every code edit.

`POLICY.json` records the prospective policy and launch gates. Existing positive results remain exploratory. The 80% native input/output target and general capability parity remain unestablished. No hooks or installed skills are changed.
