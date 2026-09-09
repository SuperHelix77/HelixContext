# Helix Context

**HELIX: Hierarchical Evidence Loading and Intelligent eXecution.**

Research toward the **maximum empirically safe compression frontier**, with capability, agentic execution and long-horizon workflow preservation first. **95% input/output savings is aspirational, not an absolute requirement.** The earlier separate 80% target is retained below as historical benchmark context. The current highest output reduction is 78.44% on an adaptively developed synthetic suite, with 80.39% input reduction in that run. This is not a universal no-loss claim or a finished skill release.

## Benchmark results

Same model: `gpt-6-astra`, medium reasoning. Each candidate completes four retained workload types in one batch: six short questions, extraction from 240 records, diagnosis of an 805-line log, and a weighted-mean repair with tests. Two control batches execute the tasks separately. Their mean native usage is **173,411 input and 1,131.5 output tokens**. The separate 80% gates are therefore at most **34,682.2 input and 226.3 output tokens** per candidate batch.

| Candidate | Input | Output | Input reduction | Output reduction | Task checks |
|---|---:|---:|---:|---:|---|
| compact | 36,738 | 712 | 78.81% | 37.07% | Passed |
| helper | 32,990 | 488 | 80.98% | 56.87% | Passed |
| helper-repeat | 33,008 | 496 | 80.97% | 56.16% | Passed |
| helper-stale | 93,762 | 883 | 45.93% | 21.96% | Passed |
| source-copy | 33,379 | 413 | 80.75% | 63.5% | Passed |
| source-copy-v2 | 33,684 | 336 | 80.58% | 70.3% | Passed |
| source-copy-v3 | 33,857 | 271 | 80.48% | 76.05% | Passed |
| source-copy-insert | 34,008 | 244 | 80.39% | 78.44% | Passed |
| source-copy-final | 34,140 | 246 | 80.31% | 78.26% | Passed |

All generated model output, including tool arguments, is counted by the native receipt. Cached tokens are included within input, not subtracted. Research/development and parent-conversation overhead are outside these task-run comparisons. The stale-source run includes its recovery usage; it has no identically injected control, so its reduction is only a comparison with normal controls.

## What changed

- Share repeated context across compatible, authorized tasks; keep separate acceptance checks.
- Prepare sufficient evidence locally. Preserve original data, exact types and number spellings, hashes and diagnostics.
- Use a general guarded edit/test helper to avoid regenerating command boilerplate. Stale sources require rereading and failures require normal recovery.
- In source-copy experiments, the model selects references to exact source entries. A deterministic caller renders them into complete answers; no hidden model generates the copied text. Every source row is eligible, not just correct answers. Raw model templates and rendered answers are both published.
- Later experiments support compact lists/ranges, insertion of new code without regenerating unchanged code, and a short entrypoint to the same helper.

Source-copy rendering requires an external caller. It is **not** automatic behavior of a desktop slash skill. It reduces native generated tokens, not the amount of information delivered in the rendered answer. No new skill version has been installed from these experiments. The existing local Caveman Astra installation is unchanged; the requested finished skill name is Helix Context.

The per-run skill catalog budget was 512 tokens; the runtime reported retaining all skills with shorter descriptions. Skill-discovery equivalence was not evaluated. No global configuration or model reasoning setting was reduced. The filesystem guard is best effort, not atomic compare-and-swap against uncooperative writers.

## Evidence and limits

`results/native-usage.json` publishes native usage fields with SHA256 commitments to the original local traces. Full traces contain private environment/memory context and are retained locally, not published. Published usage fields are extracted receipts, not independently authenticated provider attestations. `results/benchmarks.json` contains per-case behavioral checks. `results/<candidate>/` includes answers, edited code, and raw templates where applicable.

The suite was reused adaptively; controls and candidates were not randomized concurrently. These are exploratory observations, not a held-out confirmation. Passing finite task checks does not establish general intelligence equivalence, and prior clean-run savings did not survive unchanged during recovery. The checks include exact failure identifiers, types and values, uncertainty, exactly three explanatory sentences, executable mean behavior, weighted-mean value/rejection checks, and the reported existing tests.

## Local verification

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q experiments
python3 experiments/check_results.py
```

The current helper suite has 50 passing tests. These local tests verify helper mechanics, not model intelligence or end-to-end savings. Fixtures and results are provided for inspection; this repository is not yet a portable one-command rerun harness for the original native environment.

## Pending final model gate

After freezing the candidate and prespecified parity checks: run **Luna High, Sol High, and Astra High**, each on **three tasks without and with the skill** (at least 18 native runs). Each model must pass the same behavioral and agentic checks before savings are accepted. Add an adversarial 50-turn case where an early fact becomes decisive late. Estimate separate input/output savings and uncertainty; do not infer universal parity or a global maximum from finite tasks. This gate is **not run**. See `results/final-validation-plan.json`.

## Research background

[OpenAI programmatic tool calling](https://developers.openai.com/api/docs/guides/tools-programmatic-tool-calling) and [Anthropic code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) motivate deterministic intermediate processing and selective context. Their example percentages are not evidence for this experiment's results.

The current objective is specified in `results/research-contract.json`. Resident context size, cumulative input tokens and semantic information are different quantities: a 95% token reduction does not establish that 95% of decision-relevant information was discarded. Cold evidence must remain recoverable, and actual successful retrieval must be tested.
