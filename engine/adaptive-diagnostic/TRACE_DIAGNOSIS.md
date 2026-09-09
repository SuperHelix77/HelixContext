# Trace diagnosis and stop decision

All 18 existing terminal diagnosis calls were read back and hash/usage checked. No new native calls were made.

| Model | Mechanism | Commands off → on | Input saved | Output saved |
|---|---|---:|---:|---:|
| luna | typed_terminal | 3 → 2 | -6.9% | -76.1% |
| sol | typed_terminal | 3 → 1 | 53.9% | 18.8% |
| astra | typed_terminal | 2 → 1 | 31.8% | 33.8% |
| luna | literal_query_v1 | 3 → 2 | 22.3% | 26.7% |
| sol | literal_query_v1 | 1 → 1 | -2.3% | 21.6% |
| astra | literal_query_v1 | 2 → 1 | 26.6% | 34.9% |
| luna | literal_query_v2 | 1 → 1 | -3.5% | -0.2% |
| sol | literal_query_v2 | 3 → 1 | 49.6% | 50.0% |
| astra | literal_query_v2 | 2 → 1 | 25.7% | 38.6% |

## What changes the next action

Every equal-command-count pair regressed in input in these observations. Pairs with fewer commands usually improved input, but Luna typed projection is a counterexample. Thus fewer commands is a useful diagnostic signal, not a causal proof or sufficient admission rule. CLI command counts are not counts of model inferences.

Astra consistently moved from two commands to one across these three candidates; input savings stayed around 26–32%. Sol varied between one and three control commands; its approximately 50% wins coincide with three-command controls, while the one-command control beats query V1 on input. Luna varied similarly and did not gain from V2 when its control already used one command. These results do not establish a stable model-specific advantage for every candidate.

The compound-token fix increased selected evidence coverage but did not remove the final source check. Further lexical tuning is not currently supported as a route to the requested 80% joint target. Stop this short-log candidate sweep.

## Composition requirements

Keep model/task routing, but distinguish a candidate from a validated policy. Astra query projection is the most consistent diagnostic candidate here; Sol projection and Luna renderer need stronger confirmation in their respective workloads. Do not combine multiple log projections: they target overlapping costs and would duplicate evidence. Exact retrieval batching and source-copy belong only in workflows that actually require multiple spans or copying.

The next useful joint test must exercise sustained workflow state, evidence retrieval and exact artifact output in the same episode, with an efficient control allowed the same ordinary batching/copying. First implement or verify the relevant interface and offline capability checks. Do not spend on another microtask matrix expecting its percentages to compound.

Per-inference context delivery remains unobserved in these CLI traces. Native interception is Spark-owned. Do not change hooks or claim a causal token decomposition from these receipts. All public results remain bounded development evidence, with the 80% and capability-parity goals unestablished.
