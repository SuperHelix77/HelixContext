# Native cost sensitivity audit

These six diagnostic pairs cannot reach 80% model-token cost savings at any nonnegative per-token rates: even the best individual token category saves less than 80%. This arithmetic result applies only to these observed pairs. It is not a ceiling on future Helix designs.

Cached input is a subset of input. The model-only benefit is the dot product of the saved uncached-input, cached-input and output tokens with their respective rates. Subtract incremental preprocessing, retrieval, storage, coordination and recovery costs to obtain total benefit. Those costs remain incompletely metered; no net billing claim is established.

| Task | Model | Gross input saved | Output saved | Optimistic model-only cost ceiling |
|---|---|---:|---:|---:|
| terminal V2 | gpt-5.6-luna | -6.9% | -76.1% | -2.3% |
| terminal V2 | gpt-5.6-sol | 53.9% | 18.8% | 61.2% |
| terminal V2 | gpt-6-astra | 31.8% | 33.8% | 35.4% |
| renderer | gpt-5.6-luna | 26.5% | 27.9% | 27.9% |
| renderer | gpt-5.6-sol | -94.8% | -13.5% | -7.4% |
| renderer | gpt-6-astra | -89.2% | -26.3% | 27.9% |

The ceiling allows arbitrary nonnegative rates to favor whichever category improved most; actual prices need not resemble that extreme. Negative savings mean increased usage. These are single paired trials with bounded correctness checks, not general intelligence or workflow parity.

Luna terminal V2 and Sol renderer increase every priced token category. Positive token prices cannot make those observed model costs cheaper. Astra renderer reduces uncached input while increasing cached input and output, so its billing direction depends on rates and additional overhead.

Decision: retain ordinary scripting as the control and avoid enabling these mechanisms globally. Further deployment requires a measured positive full-task benefit and preserved capability. Spark owns the unresolved native hook delivery gate; this audit does not change hooks.

Reproduce: `python3 engine/accounting/audit.py`. Source hashes and exact cost coefficients are in `RATE_INDEPENDENT_AUDIT.json`.
