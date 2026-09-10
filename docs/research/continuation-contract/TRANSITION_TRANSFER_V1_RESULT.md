# Astra and Sol W50 transfer: bounded 80/80 candidates

**OBSERVED — both fresh High pairs clear 80% total-input and output savings on the known W50 continuation fixture.** Freeze `ASTRA_W50_V1_80_80_CANDIDATE` and `SOL_W50_V1_80_80_CANDIDATE`. This is not coding qualification, a general release, or proof of intelligence/workflow parity.

The intervention replaces 49 explicitly resolved record-and-ACK model turns with the existing durable Engine transition. The same model then selects the governing policy and amendments in one semantic turn. Engine evaluates the supported rule schema and copies/renders the deterministic consequences. Both arms retain ordinary tools and use the same default client base and High effort. The coordinator's Extra High setting is outside the benchmark arms.

## Matched native receipts

| Model | Metric | Control | Helix | Saved |
|---|---|---:|---:|---:|
| Astra High | Total input | 1,156,877 | 20,145 | 98.26% |
| | Cached input | 1,121,792 | 11,904 | Separate counter |
| | Uncached input | 35,085 | 8,241 | 76.51% |
| | Output, including reported reasoning | 539 | 50 | 90.72% |
| | Reported reasoning subset | 47 | 30 | Separate counter |
| Sol High | Total input | 1,114,077 | 19,289 | 98.27% |
| | Cached input | 1,066,368 | 0 | Separate counter |
| | Uncached input | 47,709 | 19,289 | 59.57% |
| | Output, including reported reasoning | 545 | 98 | 82.02% |
| | Reported reasoning subset | 70 | 78 | Separate counter |

Both controls used 50 native turns/segments; each candidate used one. All four arms issued zero commands. Each completed 49 exact ACKs and passed the unchanged final finite grader. Candidate history, exact event recovery and delivery identities reconcile with the controls. Neither candidate loaded Engine source through tools.

**OBSERVED — no native retries or failed arms.** All four attempts total 2,310,388 input, 1,232 output, 2,200,064 cached input, 110,324 uncached input and 225 reported reasoning tokens. These include the purchased controls; they are not deployment costs amortized to zero.

## What actually disappeared

Each control emitted 343 output tokens across its 49 ACKs. Its final semantic segment used 196 output tokens for Astra and 202 for Sol. Candidate semantic output was 50 and 98 respectively: final-segment-only output reductions of 74.49% and 51.49%.

Control final input was 26,309 for Astra and 25,453 for Sol. Removing prior ACK invocations dominates the whole-workflow input saving; this is not a 98% compression of the final semantic call. Sol's reported reasoning subset increased from 70 to 78 even while total workflow output fell 82.02%. Counters do not expose private reasoning or establish an irreducible floor.

Both models emitted `{"policy":"E01","amendments":["E17"]}`. This excludes the untrusted vendor event from authority. The Engine-derived answers preserve the nonce, exact numerical strings, amended group and two-approver requirement, and reject the one-approver request. Final prose and evidence lists differ from control; byte-identical final-answer parity is not claimed. The grader checks required evidence turns and a nonempty explanation, not exhaustive semantic equivalence.

## Economics and costs retained

**CONDITIONAL — frozen API Standard tariff scenarios**, verified against [official pricing](https://developers.openai.com/api/docs/pricing.md) on 2026-09-10. The [snapshot](transition-transfer-artifacts/tariff-snapshot.json) binds rates, timestamp and source hash. The live HUD refreshes prices; this historical snapshot remains frozen.

| Model | Short tariff control → Helix | Scenario saving | Long tariff control → Helix |
|---|---:|---:|---:|
| Astra | $1.499592 → $0.096814 | 93.54% | $2.985709 → $0.192378 |
| Sol | $0.628283 → $0.079116 | 87.41% | $1.251116 → $0.157252 |

These are tariff-weighted native counters, not observed Codex billing, included-plan quota, full systems cost or total project ROI. Cache was observed, not controlled. Parent research usage remains separately metered in the HUD.

| Observed local cost | Astra control | Astra Helix | Sol control | Sol Helix |
|---|---:|---:|---:|---:|
| Arm elapsed seconds | 170.106 | 4.763 | 130.169 | 6.174 |
| Preparation seconds within arm | 0.220 | 0.304 | 0.168 | 0.274 |
| Memory preflight seconds, both consultations | 0.444 | 0.323 | 0.392 | 0.297 |
| Raw memory response bytes | 44,114 | 44,110 | 44,110 | 44,106 |
| Engine object bytes read | 1,198,072 | 1,182,208 | 1,198,072 | 1,182,208 |
| Engine object bytes written | 60,089 | 60,089 | 60,089 | 60,089 |

Root registration/preparation adds 1.375 seconds and zero model turns. Preparation and memory times overlap arm elapsed: do not sum them as independent components. Caller final realization took less than 0.001 seconds per arm. Separate post-run cold recovery read and hashed 43,740 object bytes per arm. Object accounting excludes SQLite, metadata, full history-view writes, physical SSD traffic and energy. The ledger's full-prefix validation still has quadratic cumulative work; this experiment does not solve that scaling cost.

## Freeze, provenance and limits

The [preregistration](TRANSITION_TRANSFER_V1_PREREG.md), runner, dependencies, default bases and effective configuration were frozen at commit `faae491`, before any arm. Manifest SHA256: `5feb2f64a9f3095d8b3cb0b965de6df74eb1de3d53c673a7d25584d144ecabb0`. Frozen order was Astra control, Astra Helix, Sol Helix, Sol control. No control was reused. Full local audit verifies native/raw hashes, per-segment counters, High effort, default-base identity, configuration bindings, memory receipts, exact cold recovery and final realization.

The [audited report](TRANSITION_TRANSFER_V1_RESULT.json) and [public derivatives](transition-transfer-artifacts/manifest.json) retain the numerical evidence. Run `python3 docs/research/continuation-contract/transition-transfer-artifacts/verify.py` for offline counter reconciliation, source binding, exact-history recovery input, realization and original-grader checks. Public extracted usage events are not complete raw streams or provider-signed receipts; private prompts, configuration and memory responses remain local.

**CONDITIONAL — N=1 per model on an exposed development family.** The per-family median is this one observation. Do not mix it into the three-task coding medians to manufacture a qualified model median. Luna's earlier adaptive selector result remains separately labeled with its reused control.

**UNKNOWN — normal Codex app interception and broad release safety.** This research caller owns the trusted ledger head, not an atomic app event boundary. Automatic UI delivery, hostile writers and crash-safe final authority publication are not demonstrated here. The historical fixture required 50 model turns in each arm; caller-owned ACK delivery is the explicitly authorized intervention, not replication of that historical protocol.

**Next gate:** varied unseen authority/positive-authorization cases, ambiguous and unknown rules, late relevance and production lifecycle integrity. Use offline state/recovery falsifiers before new native pairs. Do not retune these successful W50 arms, delete coding failures, weaken semantic escalation, or claim a general 80/80 release.
