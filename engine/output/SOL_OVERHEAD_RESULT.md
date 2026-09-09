# Sol overhead attack: smaller metadata costs more output

**Do not promote the JSON-table transport over frozen V3.** Four fresh Sol High
runs (V3/table/table/V3) show a small native input win and an output regression.
All four exact artifacts/source-preservation checks passed; all used one reported
usage segment and zero commands. High and normal tools were unchanged.

| Sum of two runs per variant | V3 | JSON table | Savings |
|---|---:|---:|---:|
| Native input | 39,736 | 38,810 | 2.33% |
| Cached input subset | 16,384 | 16,384 | — |
| Uncached input | 23,352 | 22,426 | 3.97% |
| Native output | 498 | 592 | -18.88% |
| Reported reasoning subset | 424 | 518 | -22.17% |

The transport removed exactly 463 native input tokens per call, matching its
local tokenizer-proxy reduction. The two comparison blocks had identical cached
counts within each block: 10,368 each for V3/table, then 6,016 each for table/V3.
No cache state was forced or assumed; this equality was observed after execution.
All 94 additional output tokens were in reported reasoning, while final selected
ID output stayed at 37 tokens per call. This is evidence of an output-cost tradeoff,
not access to private cognition or a general causal theorem from two repetitions.

The experiment consumed 78,546 native input and 1,090 native output tokens. Store
preparation/completion I/O and wall time are retained per run in the
[machine-readable result](SOL_OVERHEAD_RESULT.json) and raw manifest. Caller fixture
copying, full SQLite/physical I/O, parent research and complete billing remain
outside those counters. Candidate preparation includes extra projection validation;
it is not cost-free. The result is a comparison of two Helix candidates, **not a
new native-off/on benchmark**. Do not combine it with the old control to publish
an improved headline percentage.

The monetary tradeoff is conditional, not automatically negative: with identical
cache charges and ignoring additional Engine cost, the two-run change saves
`926 * uncached_input_price - 94 * output_price`. Break-even is an output/input
unit-price ratio of about 9.85. Additional Engine cost lowers that threshold.
No actual billing rates or complete bills were measured here, so this is not a
net monetary saving claim. The separate input/output objectives still prevent
silently substituting a weighted cost score for the requested metrics.

## What the original discrepancy means

Frozen Sol V3 removed 88.10% total input but 65.10% uncached input. Control processed
39,759 uncached tokens; candidate processed 13,877. Much of the eliminated repeated
input was cached in control. One control segment alone contributed 15,878 uncached
tokens after a sharp observed cache-reuse drop. Its cause is unproven. Therefore
neither the metric gap nor all 13,877 candidate uncached tokens can be labeled
Helix Engine overhead. See the [segment and prompt audit](SOL_UNCACHED_AUDIT.md).

The overhead attack remains switchable/experimental. Frozen V3 and its 16 source
bindings are untouched. The admission dispatcher introduced separately in this
turn does not install a global hook and does not make bypass an 80% result.

Next intervention should target measured caller/platform admission or cache-prefix
stability, where the interface actually permits it. Do not replace ordinary JSON
with more decoding machinery or manipulate cache warming to advertise savings.
243 engineering tests passed; native checks remain finite task evidence, not
intelligence/agentic/long-horizon parity certification.
