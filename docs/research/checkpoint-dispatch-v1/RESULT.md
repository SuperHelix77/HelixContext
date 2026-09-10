# Durable checkpoint dispatch: offline closure

OBSERVED: the caller now freezes workflow/event, pre-state/head, exact native
request and RPC identity before transport. An exclusive fsynced dispatch marker
blocks automatic resend after either a successful send or an uncertain failure.
Native completion is associated with that original ticket, and the full native
final is retained unchanged. Incomplete captures remain unresolved.

Hostile tests exposed an original-parent crash replay defect in the preceding
`af04cfe` completion adapter: retrying the first event against EMPTY after later
commits could index an empty prefix. The correction recovers the current committed
head and keeps the historical checkpoint state separately. Earlier artifacts remain
bound to their original commit; this is a subsequent correction, not a rewrite.

Two prior real Astra cold-task request streams were replayed through the existing
RPC.call method and the new instance-local dispatch hook. Outgoing wire bytes and
original finals were unchanged. Restart replay preserved each final, and duplicate
send was blocked. Read-only app-server methods recovered the already-completed
candidate thread and exact final without thread/start, thread/resume or turn/start.

Readback took 0.04350 s and returned 8,780 native wire bytes. The entire calibration
took 0.07099 s. Replay journals used 5,634 / 8,280 bytes; logical store reads were
401,228 / 276,328 bytes. These are offline/recovery measurements with constant
binding callbacks, not live model economics. Complete result is RESULT.json.

The combined lifecycle, task/grader and new common-driver suite passes 63 checks.
The task suite includes independent interval oracles, exact late evidence,
publication fault injection, staged visibility and scripted full 50-event replay.
There were zero new model invocations for this engineering closure.

Limits: trusted local caller and retained external ticket/head; not hostile-host
rollback protection, hosted exactly-once execution, automatic ambiguous-request
reconciliation, general capability parity or Codex-app pre-inference interception.
