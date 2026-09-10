# Sol native-final V3: inspection work removed, release economics not qualified

OBSERVED, 2026-09-10. One fresh Sol High pair on the exposed maintenance task.
Frozen implementation `7ad70fd`; manifest
`d9d7b3531bd2f0e0507ff61f81c524e614dd9a15a26768ca461185f23f6ff415`.
Randomized order was Helix then control. No blind retries or reused controls.

**Do not admit this policy as a75/75 release.** It removes the targeted inspection
commands, but fails both token targets and the observed tariff comparison. Ordinary
Engine execution remains available; rejecting this optimization does not disable
the Engine. No Luna/Sol/Astra profile or population capability claim is frozen.

| Native counters, all attempts | Control | Helix V3 | Saving |
|---|---:|---:|---:|
| Total input |186,238|63,288|66.02%|
| Output, including reported reasoning |3,038|1,580|47.99%|
| Cached input |168,704|21,120|87.48%|
| Uncached input |17,534|42,168|**-140.49%**|
| Reported reasoning output |1,586|747|52.90%|
| Model segments |8|3|62.50%|
| Completed shell commands |6|0|100%|
| Internal Helix tool calls |0|2, one failed|Not comparable|
| Native elapsed seconds |122.60|68.26|44.32%|

Both arms used one task-level turn; internal tool continuations remain charged as
model segments. Setup1.116s and offline adjudication are additional costs. Eleven
native segments consumed249,526 input /4,618 output /189,824 cached input tokens
in this pair. Raw provider evidence totals350,254 bytes and remains local.

## What changed and what actually happened

V3 combines three versioned switches: indexed line edits, the complete editable
file as a numbered hot view, and actual initial/post Git scope receipts. Other
exact files remain cold and accessible. The model keeps semantic choices, ordinary
tools/probes and its normal final answer after execution. The original kernel,
skill and checked publication/recovery semantics remain.

The offline replay reduced the source view28,482→11,556 bytes and the derived edit
request2,061→534 bytes. Those replay edits NEVER entered the native prompt. Full
sources, tests and checks were unchanged. These are representation measurements,
not model savings. The real model chose a larger edit than that offline minimum.

The real Helix trajectory was:

1.19,699 input /588 output: model selected lines79–86 and authored new source, but
   omitted its final LF. Exact assembly joined the insertion to the following
   `with` statement. Staged Python collection failed. Nothing was published.
2.21,262 /370: the model corrected the missing LF. Same version0 source; all23
   regression tests and94 independent cases passed, then source was published.
3.22,327 /622: the model wrote its normal final answer from the actual receipt.
   No shell source/hash/scope inspection occurred.

The tool did not infer a newline, silently fix source, rerun the model, or hide the
failed attempt. Its final diff independently reconstructs the published bytes.
Its raw scope object binds actual Git HEAD/status, whitespace exit and source roots.
Those observations are not a semantic completeness or exclusive-custody certificate.

INFERRED: supplying scope and line-addressable source is consistent with eliminating
the V2 inspection detours. This composite N=1 pair cannot isolate which switch
caused the change. It does not show that semantic investigation should be suppressed.

CONDITIONAL: even deleting the entire repair segment from this recorded trajectory
would leave42,026 input /1,210 output:77.43% input and60.17% output savings against
this control. A newline-only interface fix therefore cannot meet75/75 under the
unchanged retained-segment costs. This is optimistic trace arithmetic, not an
attainable counterfactual, causal estimate or inherent model lower bound.

## Capability, output and control limitations

The two final artifacts differ in bytes but both pass23 regression tests and94
independent behavioral cases. All four semantic probe programs previously observed
in V1/V2 also pass on BOTH artifacts. V3 itself produced no additional standalone
semantic probe program in either arm. These are finite checks, not general
intelligence, long-horizon or workflow equivalence.

Both final answers are ordinary model-written prose after relevant tool results.
Their task/check/scope claims were explicitly checked against the receipts. Helix
truthfully reports its failed staged attempt and repair. However its local link
uses `file://…#L79`, violating its configured absolute Markdown path convention;
the control used the correct path format. The original answer remains unmodified.
Normal final authorship is established; full output-convention conformance is not.

The control is **ordinary execution under shared installed instructions**, not
pristine Codex. Both captured input streams contain the user-owned global Helix
skill-activation rule. The control additionally chose an unrequested codexworkflow
skill, attempted registration through the global runtime, and encountered a
permission error before completing the task normally. That detour is retained in
the counters. There is no proof it was caused by one specific prompt clause.

This materially limits a claim of savings over vanilla Codex: part of the observed
control work is interacting with already-installed Helix continuity machinery.
Do not hide that cost, silently relabel the control, or change global settings.
The paired result remains valid evidence about these captured configurations.

## Hidden prices and accounting

The dated [official Standard API tariff](https://developers.openai.com/api/docs/pricing.md)
was fetched2026-09-10 06:38UTC, SHA
`8c9b760861c1c760cc82f6ccf3037bd9d3a49518a1303f56ba63a2eb0b4158ad`.
The HUD continues to refresh prices and expires stale values.

| API-equivalent scenario | Control | Helix | Saving |
|---|---:|---:|---:|
| Short context |$0.1983776|$0.2087200|**-5.21%**|
| Long context |$0.3663752|$0.4016400|**-9.63%**|

These scenarios are not bills, included-plan quota ratios, or complete effective
cost. Cache outcomes differed sharply: both first Helix segments reported zero
cached input. Cause, persistence and warm-deployment economics are UNKNOWN. Do not
assume all input is uncached, assign equal rates, or discard the observed misses.

Native Helix Store traffic:83,161 bytes read,46,737 written,129,898 hashed,10 object
reads. Prepared memory raw bytes36,056 /36,057 for Helix/control; preparation time
0.149 /0.199s. Scope observation runs three Git commands per snapshot. Staging,
SQLite, Python/checker and physical disk traffic are not fully metered. Zero-valued
uninstrumented Store staging fields do not establish zero whole-process I/O.
The extra failed checks, archival, caller preparation, final continuation and audits
are retained; total effective cost and actual Codex quota saving remain UNKNOWN.

## Decision and next gate

The inspection-removal hypothesis survives as bounded evidence. V3 does not qualify
as an economical policy, and no unchanged rerun or newline-only native retry is
justified. Keep the exact edit machinery as tested infrastructure, not proof of75/75.

Before another expensive cohort: establish an isolated, explicitly described
instruction/continuity boundary using offline request capture. Preserve the present
installed-configuration comparison separately. The control must not silently pay
Helix-specific setup while being advertised as vanilla. Do not change production
settings, omit ordinary semantic capabilities or manipulate cache outcomes to win.

The [zero-inference isolation probe](CONTROL_BOUNDARY_OFFLINE.json) now confirms
that two otherwise matched isolated CLI captures can retain the ordinary memory
instruction while excluding the user-owned Helix activation rule from one arm.
The AGENTS payload falls2,246→851 bytes; real global AGENTS/config are unchanged.
Both requests terminate at an intentional local400 response without credentials
or a model call. This is client serialization evidence only: authenticated
app-server effective config, skill/tool catalogs and production behavior still
need binding. It does not explain the whole initial input floor or validate a new
native baseline, capability level, cache result or token saving.

The seven-cell release cohort still has only1/7 recorded pairs. Its release medians
remain UNKNOWN. Historical selector/caller-rendered90/90 wins remain separate from
the current model-written-final contract. The normal Codex app pre-inference gate,
full capability parity and Astra High/XHigh qualification remain separate open gates.

Evidence: [native audit](SOL_HIGH_RESULT.json), [scope/diff and answer review](REVIEW_AUDIT.json),
[independent artifact/probe checks](PUBLIC_VERIFICATION.json),
[segment anatomy](artifacts/ANATOMY.json), [tariff scenarios](artifacts/COST.json),
[public hashes](artifacts/MANIFEST.json), [prospective protocol](PREREG.md).
Run `python3 docs/research/native-output-v3/verify_artifacts.py` to recheck the public
derivatives without inference or modification of the frozen receipts.
