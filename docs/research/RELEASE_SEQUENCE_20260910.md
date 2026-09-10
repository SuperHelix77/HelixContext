# User-directed release sequence

Latest instruction: releasable 75% input and 75% output profiles, capability and
agentic/workflow preservation first. Original 80/80 remains an aspiration; do not
mislabel 75/75 as 80/80. Keep actual paired counters and failures visible.

1. Luna: finish qualification and packaging. A fresh known coding pair now clears
   75/75 at 86.17% input / 79.06% output, with a portable kernel/contract candidate
   [frozen here](continuation-contract/LUNA_CODING_V1_75_FREEZE.json). W50 remains
   a bounded candidate. Two fresh closed-request retrieval pairs now avoid all
   model calls with exact answers, but this is a separate, grammar-limited
   Engine execution result with nonzero setup costs; see the
   [retrieval report](continuation-contract/LUNA_RESOLVED_RETRIEVAL_RESULT.md).
   General coding is not qualified. The corrected three-task continuation has
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
   A fresh W50 transfer now clears 98.27% input / 82.02% output, uncached 59.57%.
   This is an N=1 bounded candidate; the coding result below remains unchanged.
   The fresh three-contract coding transfer passed finite behavior but failed
   output qualification: median 88.02% input / 62.91% output, uncached21.50%.
   [Results](continuation-contract/SOL_VARIED_CODING_V1_RESULT.md) remain separate
   from the frozen assembly candidate. No unchanged retry is justified.
4. Astra: independently qualify its profile; preserve semantic review and probes.
   A fresh W50 transfer now clears 98.26% input / 90.72% output, uncached 76.51%.
   Both transfers use default bases and High effort; [audited report](continuation-contract/TRANSITION_TRANSFER_V1_RESULT.md).
   The fresh three-contract transfer now passes finite behavior but fails 75/75
   on all three pairs: median 83.07% input / 60.02% output, uncached 27.60%.
   Every candidate used one segment and zero commands. See the
   [audited result](continuation-contract/ASTRA_VARIED_CODING_V1_RESULT.md).
   The next coding attack must address work within that remaining call; another
   command reducer or unchanged retry has no demonstrated residual to remove.

All releases must remain integratable with the normal Codex app later. Keep Engine
independent of the research caller through a small versioned adapter interface for
bound ingress, lifecycle events, exact completion and semantic re-entry. Test each
interface's actual runtime behavior; do not assume CLI success equals desktop UI
success. A research-only launch path cannot be called completed app integration.

Current boundary evidence: pre-submit blocking avoids provider requests in installed
CLI; history insertion persists exact records without inference. Their composition
with visible completed ACKs and reliable restart is not yet verified. See
[runtime result](continuation-contract/PREINFERENCE_RUNTIME_RESULT.md).

Later offline evidence: an explicit user-command path creates durable Engine
execution items without a model call and retains success/failure across server
restart. Its unsandboxed authority boundary prevents treating it as an automatic
replacement for ordinary chat; [delivery qualification remains open](continuation-contract/NATIVE_ENGINE_DELIVERY_RESULT.md).

The new [display tracker](continuation-contract/DISPLAY_OUTBOX_RECOVERY_RESULT.md)
reconciles a retained native item after process restart and a lost local ACK without
resubmission. The initial shell-envelope mismatch remains a recorded failed trial;
offline recovery requires no second command. Automatic chat routing, native
idempotency, trusted outbox custody and desktop rendering are still unqualified.

HUD must distinguish benchmark qualification, packaging and Codex integration
status. Expose input/output/cached/uncached separately, failed attempts, Engine
overhead, integrity/recovery errors, active policy and native bypass. Unknown costs
and unsupported pricing stay unknown. Use timestamps and freshness indicators;
never fabricate successful zero-token work from answerless cancelled/blocked turns.
