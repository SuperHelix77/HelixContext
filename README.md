# Helix Context

**HELIX: Hierarchical Evidence Loading and Intelligent eXecution.**

Research toward the **maximum empirically safe compression frontier**, with capability, agentic execution and long-horizon workflow preservation first. Separate **80% input/output savings** remains the research objective; 95% is a stretch target. The user permits bounded candidate freezes at 75/75, which must not be described as 80/80 or general model parity.

## Current Engine milestone — 2026-09-10

A fresh Luna High coding pair with the frozen delegation kernel plus caller-owned preparation/checks/publication measured **86.17% input / 79.06% output / 62.04% uncached-input savings**. Both arms passed the original tests and finite independent oracle. This freezes a **bounded 75/75 development candidate**, not a general Luna release; 80/80 still fails on output. The exact portable kernel and caller requirements are [packaged here](engine/profiles/luna-coding-v1-75/README.md), and [receipts, failed earlier candidates, costs and limits are documented](docs/research/continuation-contract/LUNA_CODING_COMPOSITION_RESULT.md).

The live HUD now separates model/task-family medians from Engine-only exact retrieval, deduplicates reused receipts, and refreshes official tariff scenarios. Routine monitoring invokes no model. Broader Luna qualification, Sol/Astra qualification, normal Codex-app delivery and the full 80/80 objective remain open.

The static-skill experiment below is historical exploratory evidence, not the latest Engine result. Its source-copy fixture achieved 80.39% input / 78.44% output reduction; the earlier High-model evaluation is in [FRONTIER_REPORT.md](FRONTIER_REPORT.md).

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

Source-copy rendering requires an external caller. It is **not** automatic behavior of a desktop slash skill. It reduces native generated tokens, not the amount of information delivered in the rendered answer. The V3 prose skill is now packaged as `skills/helixcontext` and installed locally as **Helix Context**, invoked with `/helixcontext`. Caveman Astra remains available for compatibility. The prose skill does not itself install the experimental caller middleware or promise fixed savings.

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

After freezing the candidate and prespecified parity checks: run **Luna High, Sol High, and Astra High**, each on **three tasks without and with the skill** (at least 18 native runs). Each model must pass the same behavioral and agentic checks before savings are accepted. Add an adversarial 50-turn case where an early fact becomes decisive late. Estimate separate input/output savings and uncertainty; do not infer universal parity or a global maximum from finite tasks. The first High-model gate has run and exposed recurring-cost regressions. Subsequent frozen iterations are under evaluation; see `results/frontier-interim.json`.

## Research background

[OpenAI programmatic tool calling](https://developers.openai.com/api/docs/guides/tools-programmatic-tool-calling) and [Anthropic code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) motivate deterministic intermediate processing and selective context. Their example percentages are not evidence for this experiment's results.

The current objective is specified in `results/research-contract.json`. Resident context size, cumulative input tokens and semantic information are different quantities: a 95% token reduction does not establish that 95% of decision-relevant information was discarded. Cold evidence must remain recoverable, and actual successful retrieval must be tested.

## High-model iterations: rejected costs stay in the results

`results/frontier-interim.json` contains the first Luna/Sol/Astra High suite, clarified reasoning follow-ups, a 20-turn latent-future-relevance family, and subsequent iterations. `results/frontier-native-usage.json` publishes extracted per-call receipts with original trace commitments. `results/cost-audit.json` includes observed development tokens as a **lower bound**, including unsuccessful candidates. Unmetered coordinator usage prevents a complete whole-project break-even claim.

All three models recovered the decisive early evidence on the first 50-turn task and the delayed 20-turn Unicode/whitespace task. That did not make the policy efficient. Luna's 50-turn candidate used 2.39 times the input and 5.89 times the output of its control, and failed the strict acknowledgement-format check. Its 20-turn latent case used 2.76 times the input and 5.27 times the output. Sol and Astra also increased output on these long-horizon tasks. This version is rejected as a general efficiency policy.

V3 removes duplicate caller-owned bookkeeping and loads the full skill only for substantive decisions. Its five-turn diagnostic passed exact acknowledgements and caller-file integrity for every model and arm, but small-task costs remained mixed. Its reasoning and code-repair outcomes pass so far; the stronger file-reference reasoning control is sometimes cheaper than Helix. The full 50-turn V3 and held-out 40-turn latent checks are complete and pass all scored checks for all three models. Aggregate native input savings across Q4/A/W50/L40 are 25.28% Luna, 20.99% Sol and 17.11% Astra; output savings are 32.93%, 5.36% and -4.41%, respectively. See [the completed report](FRONTIER_REPORT.md) and `results/frontier-v3.json`. No universal no-loss or fixed-percentage claim follows.

The runner uses **a fresh native invocation for every turn**, reconstructing released context through an external caller. This evaluates caller plus skill, not a stock desktop persistent-session slash skill. No native calls are skipped. V3 A/W comparisons explicitly reuse original same-model, same-task controls; its Q and L40 controls are newly run. Future events are omitted from prompts, but there is no OS-enforced filesystem isolation from evaluator files.

[LongMemEval](https://arxiv.org/abs/2410.10813) motivates testing updates, temporal reasoning and abstention in addition to extraction. [Anthropic's context-engineering guidance](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) motivates selective retrieval and context management. Neither source establishes Helix's savings or parity. These synthetic delayed-relevance tests remain narrower than sustained dependent-action workflows.

## Next extension

Durable active-skill restoration after compaction and event-driven peer status are being developed separately. The next middleware candidate will archive raw command evidence before emitting typed compact packets, with exact retrieval and measured overhead. These extensions are not included in V3 model-performance claims.
