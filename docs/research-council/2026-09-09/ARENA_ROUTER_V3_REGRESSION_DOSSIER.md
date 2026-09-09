# Arena hostile audit — router validation and V3 regression

Status: **FROZEN INTAKE**

Source branch: `arena/01a086ad-helixcontext`

Pinned source commit: `a1f5750151f55e6d2c6186f144c0f0d98fe0b4a5`

Primary source dossier: `RESEARCH_DOSSIER_2026-09-09.md`, especially §23.

This intake preserves Arena's findings as an independent hostile-audit lane. They are not automatically Helix decisions.

## Core observed result

Arena extracted all **33 complete off/on pairs** across four cohorts (`V1V2`, `V2iter`, `FUP`, `V3`) and found a previously undocumented regression on short evidence tasks.

Input savings by cohort:

| Model | V1V2 Q | V2iter Q3 | FUP Q2 | V3 Q | V3 Q4 |
|---|---:|---:|---:|---:|---:|
| Luna | +88.8% | +35.0% | +51.0% | +50.6% | +31.6% |
| Sol | +77.4% | +67.2% | +84.2% | **-13.9%** | **-1.9%** |
| Astra | +48.7% | +49.7% | +50.6% | **-13.0%** | **-1.7%** |

Arena's mechanistic hypothesis is that Sol/Astra V3 receives compressed-but-not-resident evidence and then spends additional **uncached in-turn work** reconstructing or re-verifying it. The dossier points to the same surface signature in Astra W50 turn-50 and Luna memory-followup behavior. This is an inference from usage traces, not access to hidden reasoning.

## Router validation

Arena replayed a bypass router with leave-one-cohort-out validation.

Aggregate result:

- router: `$4.129`
- always ON: `$4.689`
- always OFF: `$5.188`
- router improves aggregate cost by **12.0% vs always ON** and **20.4% vs always OFF**

But on held-out V3:

- router: `$1.547`
- always ON: `$1.219`
- router is **27.0% worse** than always ON

Arena therefore withdraws its earlier task-router recommendation.

## T13 — policy-version dominance

Arena reports that policy-version effects dominate model/task effects in the current corpus. The strongest example is Luna long-horizon gain swinging from **-133.7%** to **-94.4%** to **+53.4%** on the same family across policy versions — a 187-point swing.

Arena's resulting recommendation:

> Do not ship a router keyed only on `(model, task family)`. Treat each Helix release/policy version as a new regime and use a **per-release measured gate**. Prior-release routing tables expire rather than serving as trusted priors.

This is supported by the leave-one-cohort-out failure on V3, but the exact variance claim should remain scoped to the observed corpus.

## Reliable sign-stable cells identified by Arena

| Rule | Support | Observed range |
|---|---:|---:|
| Luna + evidence tasks -> Helix ON | 5/5 | +6.1% to +73.5% |
| Sol + long-horizon -> Helix ON | 3/3 | +11.8% to +52.6% |
| Astra + long-horizon -> Helix ON | 3/3 | +6.2% to +43.4% |
| Sol/Astra + short evidence under V3 -> OFF | 2/2 within V3 | -1.4% to -15.1% |

Arena identifies Luna + evidence as the most sign-stable existing cell and warns that Sol caller-completion was still only n=1 in Arena's evidence cut.

## Zero-native-call priorities

Arena moved two actions to the top of the queue because they cost no new native calls:

1. Read Astra's retained W50 turn-50 trace.
2. Diff V3 evidence handling against V2iter/FUP for Sol and Astra to identify the regression source.

Arena estimates that recovering the previous +48% to +84% short-evidence behavior could be more valuable than adding a new mechanism.

## Consequences for council adjudication

- The earlier model/task router should be treated as **killed in its current form**.
- Routing/gating must be version-bound and re-measured after material policy changes.
- Aggregate model-level savings can hide task-family regressions.
- Per-family/per-policy telemetry should be mandatory in the HUD.
- The V3 Sol/Astra short-evidence regression must be reconciled before treating V3 as a generally superior policy.
- Arena's evidence cut predates later Sol Integrated V2/V3 developments; those later results must be evaluated separately rather than back-projected into this dossier.

## Provenance

Pinned Arena HEAD: `a1f5750151f55e6d2c6186f144c0f0d98fe0b4a5`

Arena branch is three commits ahead of main and contains:

- `RESEARCH_DOSSIER_2026-09-09.md`
- `research/cache-adjusted-ledger/LEDGER.md`
- `research/cache-adjusted-ledger/dollar.py`
- `research/cache-adjusted-ledger/ledger.py`

Do not silently update this frozen intake if the Arena branch later changes. A later Arena revision must be captured as a new intake artifact.