# V3 crosses the numeric gate: Sol research candidate frozen

**88.10% native input / 88.98% native output savings**, with exact artifact and
source-preservation checks passing. Freeze: `SOL_V1_80_80_CANDIDATE`. Sol
optimization stops; Astra High is next, then Luna High.

This is **one development task with an explicitly amended resource budget**,
not untouched preregistration, a holdout, general intelligence parity or
long-horizon workflow certification.

| Metric | Fresh app-server control | V3 candidate | Saved |
|---|---:|---:|---:|
| Native input including cached | 167,119 | 19,893 | 88.10% |
| Native output including reasoning | 2,659 | 293 | 88.98% |
| Cached input, subset | 127,360 | 6,016 | — |
| Uncached input | 39,759 | 13,877 | 65.10% |
| Reported reasoning output, subset | 1,074 | 256 | 76.16% |
| Model command calls | 5 | 0 | 100% |
| Native elapsed seconds | 112.926 | 12.927 | 88.55% |
| Exact artifact | 6,102 bytes, PASS | 6,102 bytes, PASS | — |

The pair consumed **187,012 reported input / 2,952 output tokens**. Cached input
is included rather than added twice. Uncached input fell 65.10%; the 88.10% total
input figure is not an 88.10% monetary saving. Physical I/O, SQLite traffic,
complete server billing and parent research remain unmeasured.

## What changed

V2's last model-side command read the skill. V3 attaches the exact local skill
through the supported native app-server `skill` input, with caller registration
before `turn/start`. The native runtime receives the full instructions; we did
not merely tell the model to skip a required read. See the
[design and official source](INTEGRATED_V3_DESIGN.md).

Both arms use the same app-server, Sol High, workspace-write sandbox, normal tools
and local registration boundary. Both have identical source fixtures and skill
files. Only the candidate receives native skill attachment, verified evidence,
Memory/Reducer presentation and caller completion. No CLI control was reused.
The candidate returned original IDs without commands, generated glue or a
registration narrative. Caller code performed exact copying and validation.

Raw app-server events independently match normalized HUD counters. Each arm has
one `turn/start`; cumulative usage is read once at its final total, not summed
across updates. The attached skill path/hash matches the registered actual native
thread ID. Neither stderr records a sampling retry or sandbox denial, and neither
raw stream includes an error notification. This is observed evidence, not proof
of unreported server internals or all future workflow behavior.

## Resource-budget amendment, preserved explicitly

The original runner stopped after control because **167,119 input exceeded its
150,000 post-call ceiling**. The candidate had not started. That original stopped
result remains unchanged and hash-bound.

The candidate prompt, task, semantic checker, code and reasoning settings were
already frozen before control. A separately recorded amendment authorized one
candidate continuation, capped at 80,000 input / 6,000 output and 250,000 input /
9,000 output combined. We did not rerun control, select among controls, edit the
candidate prompt, increase baseline work or lower checks. The candidate cleared
these amended limits and the unchanged 80/80 numerical threshold.

The public result retains the control's original `overrun: true`. The freeze is a
**budget-amended development candidate**, not a clean untouched preregistered
qualification. Transient preparation counters lost when the first driver stopped
are explicitly unknown; retained preparation and recovery counters are reported.

## Freeze and limits

The [frozen Sol profile](../profiles/sol-high-v1.json) binds component source hashes
and the [machine-readable adjudication](SOL_INTEGRATED_V3_RESULT.json). Activation
is restricted to explicit qualified-fixture/research use; unsupported work may
bypass Helix. Do not globally force this policy on novel tasks.

213 engineering tests passed before native launch; the HUD cumulative-reader
check subsequently raised the current suite to 214. Zero-inference preflight
confirmed the protocol, and native evidence confirmed actual attachment and
bounded task success. This does not replace the requested representative
three-task matrix, adversarial future-relevance trajectory or model failure and
recovery tests. Those gates remain open. No additional Sol tuning run follows.
