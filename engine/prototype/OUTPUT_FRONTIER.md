# Output bottleneck: conditional frontier from native receipts

This is arithmetic on existing native counters, not another model run or a proof
that less reasoning necessarily means lower capability. OpenAI documents that
[reasoning counts toward output usage](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them).
The native runner's flattened counter mapping was not independently traced here;
the bounds below explicitly assume that same inclusion convention.

For baseline output B, an 80% reduction requires integer output at most floor(B/5).
If R reasoning tokens remain fixed, even eliminating every other generated token
leaves output at least R. Therefore maximum savings under that fixed-R assumption
are 1-R/B. This is an optimistic bound: real tasks still need other output.

| Case | Baseline output B | Fixed reported R | 80% maximum output | Maximum saving if R stays fixed |
|---|---:|---:|---:|---:|
| Memory control | 1,659 | 674 | 331 | 59.37% |
| Memory candidate vs same control | 1,659 | 852 | 331 | 48.64% |
| Query V2 Luna control | 532 | 289 | 106 | 45.68% |
| Query V2 Sol control | 820 | 388 | 164 | 52.68% |
| Query V2 Astra control | 277 | 0 | 55 | No informative reasoning floor |

For the memory candidate, reaching the target would require at least 521 fewer
reasoning tokens even if all other generation disappeared. This is a necessary
condition under the assumption, not a proposed token quota. Reasoning settings,
required verification and recovery remain intact. No hidden reasoning content is
inferred from these totals.

## Consequence for the next experiment

More source/terminal compression alone is not sufficient evidence to predict 80%
output savings. It may indirectly reduce model work, but the last measured memory
candidate increased both reasoning and total output. The new typed reader and
skill bootstrap rule are unqualified candidates; their smaller payloads do not
reverse that measured result.

Prioritize a reusable checked workflow that removes repeated procedural model
work, including setup amortization, and compare it with an equally capable
ordinary scripted control. Preserve individual failure checks and later recovery.
Require a demonstrated reduction in native generation before expanding to the
requested three-model/three-task matrix. Do not repeat memory-only sweeps, lower
effort, hide failures, or inflate baseline history merely to manufacture 80%.

`OUTPUT_FRONTIER.json` pins the source reports and exact calculations. The full
goal remains open: there is no established joint 80% native result and no general
intelligence/workflow-parity certification.
