# Interface research and a feasibility gate

## Primary evidence and its limits

SWE-agent studies agent-computer interfaces with action and feedback ablations. In its reported Lite experiments, a 100-line viewer outperformed both 30-line and full-file variants. The paper also describes reducing repetitive navigation and edit mechanics. These results motivate testing interface contracts and feedback, but do not establish a universally optimal context size, savings rate, or transfer to current Helix models. [Yang et al., SWE-agent, 2024, Tables 2–3 and Section 5](https://arxiv.org/html/2405.15793v3)

Anthropic describes loading tool definitions on demand and executing data filtering, transfer and control flow in code before returning results to the model. Its example reports 150,000 to 2,000 tokens, while also noting execution-environment overhead. That example targets specific tool-definition and intermediate-data costs; it is not a capability-parity benchmark for Helix, nor evidence that Helix controls the same fraction of its native context. [Anthropic, Code execution with MCP, November 4, 2025](https://www.anthropic.com/engineering/code-execution-with-mcp)

## Conditional proposition: targetable-share bound

This is an application of elementary cost decomposition, not a novelty claim.

For either native input or output separately, let baseline C = U + M, where U is cost left unchanged by a proposed intervention and M is the entire cost it can remove. Let the candidate cost be C' = U + T + H, with T >= 0 remaining targeted cost and H >= 0 added overhead within this same accounting boundary.

Then R = 1 - C'/C = (M - T - H)/C <= (M-H)/C <= M/C, for C>0.

Proof follows by substitution and nonnegativity. To achieve R >= r, necessarily M >= r*C + H. Apply this independently to input and output; an input win cannot satisfy the output constraint. If the intervention changes U, that component was not truly unaffected and the decomposition must be revised. This is a conditional bound, not an empirically identified ceiling for Helix.

## Audit against current evidence

The existing wrapper preserved 9.2 MB while emitting about 2 KB, but the native audit's next-call context was far smaller than its 1 MB command event. Therefore raw command-event bytes cannot identify M. Native truncation or other processing changes the model-facing stream. The CLI pilot totals also lack per-inference context attribution. We cannot assign all input to log content, all output to copied data, or treat hidden context as measured fixed overhead.

This invalidates a tempting shortcut: using the wrapper byte ratio as a forecast of cumulative native savings. The opposite shortcut is also invalid: calling 80% impossible merely because current short-task pairs miss it.

## Decision before implementation

Do not add another reducer or rerun a three-model microtask sweep based on packet size. The next instrumented test must establish actual complete-turn usage, per-inference usage where available, exact tool-return bytes, command counts, source/retrieval/renderer overhead, and correctness of delivered artifacts. Keep platform-controlled context unallocated if it cannot be observed. Clearly separate measured quantities from assumptions about U and M.

A bounded matched experiment can compare ordinary execution with a stable wrapper interface on the same fresh task. First specify the cost removed, an expected effect large enough to justify measurement expense, and a stop rule. Include required source checks, repair, and discovery costs. If the targeted share remains unidentified, report that uncertainty instead of manufacturing a budget allocation.

Model/task candidates remain Luna exact-copy verification, Sol duplicate-discovery reduction, and Astra low-discovery-cost evidence access. Those hypotheses come from Helix traces, not the external papers. Test distinct mechanisms jointly; preserve an efficient ordinary baseline. No new model calls, hook changes, or production policy changes were made by this research step.
