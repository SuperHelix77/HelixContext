# User-directed release sequence

Latest instruction: releasable 75% input and 75% output profiles, capability and
agentic/workflow preservation first. Original 80/80 remains an aspiration; do not
mislabel 75/75 as 80/80. Keep actual paired counters and failures visible.

1. Luna: finish qualification and packaging. A fresh known coding pair now clears
   75/75 at 86.17% input / 79.06% output, with a portable kernel/contract candidate
   [frozen here](continuation-contract/LUNA_CODING_V1_75_FREEZE.json). W50 remains
   a separate bounded candidate; general
   coding is not qualified. The subsequent corrected three-task continuation has
   median 86.29% input / 64.04% output savings, all finite checks passing; one of
   three pairs meets 75/75. See the [qualification report](continuation-contract/LUNA_VARIED_CODING_REPORT_20260910.md).
   Unsupported cells retain ordinary model execution
   inside the active Engine; do not disable Engine for those tasks. A profile
   cannot inherit W50 savings on unrelated tasks. Native no-loss and full lifecycle
   evidence are still required before a release label.
2. Complete the live HUD after Luna: quick refresh, low monitoring overhead,
   authoritative event stream, reconciliation after reconnect/restart, accurate
   status and costs. Rendering and routine monitoring use no model calls. Measure
   update latency, source freshness and dropped/duplicated event handling rather
   than calling a dashboard “fast” from appearance alone.
3. Sol: qualify and package its own 75/75 profile with the same evidence rules.
4. Astra: independently qualify its profile; preserve semantic review and probes.

All releases must remain integratable with the normal Codex app later. Keep Engine
independent of the research caller through a small versioned adapter interface for
bound ingress, lifecycle events, exact completion and semantic re-entry. Test each
interface's actual runtime behavior; do not assume CLI success equals desktop UI
success. A research-only launch path cannot be called completed app integration.

Current boundary evidence: pre-submit blocking avoids provider requests in installed
CLI; history insertion persists exact records without inference. Their composition
with visible completed ACKs and reliable restart is not yet verified. See
[runtime result](continuation-contract/PREINFERENCE_RUNTIME_RESULT.md).

HUD must distinguish benchmark qualification, packaging and Codex integration
status. Expose input/output/cached/uncached separately, failed attempts, Engine
overhead, integrity/recovery errors, active policy and native bypass. Unknown costs
and unsupported pricing stay unknown. Use timestamps and freshness indicators;
never fabricate successful zero-token work from answerless cancelled/blocked turns.
