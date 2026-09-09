# Cache-adjusted and price-weighted cost ledger

Deterministic recomputation over **existing repository receipts only**. No native model calls were
made to produce these numbers. Run offline:

```sh
python3 research/cache-adjusted-ledger/ledger.py    # gross vs uncached-input savings, Sol composition
python3 research/cache-adjusted-ledger/dollar.py    # conditional dollar ledger, price sensitivity
```

## Provenance of inputs (all verbatim from repository receipts)

| Input | Source |
|---|---|
| Query-V2 six traces | `engine/prototype/NATIVE_RECEIPT_RECHECK.json` (SHA-256 verified by the repository) |
| Sol caller-completion pair | `engine/output/SOL_CALLER_COMPLETION_RESULT.json` |
| Luna cold-plan pair | `engine/output/LUNA_COLD_PLAN_RESULT.json` |
| Memory follow-up vs retained control | `engine/prototype/MEMORY_NATIVE_FOLLOWUP.json` |
| V3 per-task and aggregate usage | `results/frontier-v3.json` |
| Per-turn `resident_prompt_proxy_tokens` | `results/frontier-native-usage.json` |
| Project corpus totals | `results/cost-audit.json` |
| Reasoning-floor bounds | `engine/prototype/OUTPUT_FRONTIER.json` |
| First-call fixed bound | `engine/call-budget/RESULT.json` |

`resident_prompt_proxy_tokens` is defined at `benchmarks/frozen-high/run_benchmark.py:58` as the
tiktoken `o200k_base` length of the caller-supplied prompt for a fresh `codex exec` invocation. It is
therefore a **lower bound on caller-controlled input** and an upper bound on nothing.

## Accounting conventions

- `uncached_input = input_tokens − cached_input_tokens`. The repository states cached input is a
  **subset** of input and must never be added twice. This ledger follows that convention.
- `reported_reasoning_output_tokens` is likewise a subset of output tokens.
- **No monetary claim is made.** Dollar figures are `CONDITIONAL` on a stated rate card. The models
  measured (`gpt-5.6-luna`, `gpt-5.6-sol`, `gpt-6-astra`) have **no published rate card**; the
  GPT-5.x public rates ($1.25 / $0.125 / $10.00 per M) are used only as a sensitivity reference, so
  that `k` (cache discount) and `p` (output:input price ratio) can be varied explicitly.

## Rate card used for the conditional dollar ledger

| Component | Rate per 1M tokens |
|---|---|
| Full-rate input | $1.25 |
| Cached input | $0.125 (90% discount ⇒ k = 0.10) |
| Output (incl. reported reasoning) | $10.00 (⇒ p = 8.0) |

Sensitivity is swept over `k ∈ {1.00, 0.25, 0.10}` and `p ∈ {4, 8, 16}`.

## Known limits

- The composition of `cached_input_tokens` is **UNKNOWN**. On single-invocation tasks (Q4) cached is
  83% of input, which is only possible if **intra-invocation** prefix re-reads are counted. If so,
  the "uncached ceiling" bounds in the dossier are conservative by an unquantified amount.
- Parent/coordinator conversation tokens are excluded from every repository receipt and remain
  **UNKNOWN**. Any whole-project break-even claim is therefore unsupported.
- Physical I/O, disk allocation, remote compute and electricity are unmeasured.
- `P_host` (the host prefix) is inferred as `input/turn − cached/turn` residual; it is not directly
  observable and is reported as `INFERRED`.
