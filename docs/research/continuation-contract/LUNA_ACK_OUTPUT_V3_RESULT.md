# Luna V3: explicit roles, exact-ID recovery, output savings64.43%

OBSERVED: one Luna High native turn, one model segment,22,829input/228output,
12,845uncached input. Reported188reasoningoutputtokens are included in228.
No hook events appear. Versus the reused original persistent control:
97.89%input,64.43%output,72.53%uncached savings.

The original frozen V3 **failed schema validation**: the model supplied exact
archive IDs `E01`, `E17`, `E31` rather than integer turn numbers. Its selected roles,
authorization and reason were correct. The caller stopped without rendering a
successful result. That failure is preserved in `failure.json` and the audit.

A subsequent deterministic adapter resolves exact event IDs against the same
bound archive. It rejects unknown, fuzzy, boolean and ambiguous references. It
changes no semantic choice and launches no model call. Rendering the resolved
roles gives violet, two required approvers and all exact historical strings;
the original semantic grader passes. Raw output and original history are untouched;
`recovered-final.json` and `recovery-results.json` record the correction separately.

**Classification: post-hoc development recovery PASS, not frozen-policy success,
independent replication, production admission or80/80.** The interface correction
is general exact identifier resolution, not a hard-coded answer or retroactive
source reordering.

## What changed and what remains

V2's ambiguous overwrite-order list became explicit base-policy and amendment
roles. The Engine applies supported amendment scope in chronological order;
unknown scope stops publication. A model-chosen semantic reason code replaces
model-written report prose. Engine templates copy exact policy values. Offline
checks reject reversed roles, stale/unknown references, unsupported scope and
contradictory decisions. A correctly rendered wrong authorization still fails the
separate semantic gate: mechanical validity never implies task correctness.

| Candidate | Native input | Native output | Qualification |
|---|---:|---:|---|
| ACK + preparation V1 |69,637|1,270|Known fixture PASS; output regression|
| Explicit ownership + ordered copy V2 |22,813|264|Wrong rendered group; FAIL|
| Roles + reason V3 |22,829|228|Schema FAIL; exact-ID recovery PASS|

The three-segment setup path is gone in V2/V3. V3's remaining output is188reported
reasoningtokens plus40otheroutputtokens. The80%outputbudget is128.2: even deleting
all40otheroutputtokens while retaining this observed reasoning count cannot
reach it. This is an arithmetic sensitivity of this trace, **not a proof of a
universal or irreducible Luna reasoning floor**. Another formatter alone has
insufficient removable output under the unchanged trajectory.

## Cost boundaries

All three candidate attempts together:115,279input/1,762output. Including the
native control:1,197,821input/2,403output. Failed attempts are retained. Adapter
recovery read18,118logicalbytes and took~0.000388seconds; native raw receipts use
173,139bytes. The frozen V3 driver failed before persisting its complete caller
metrics, so full preparation-path economics remain UNKNOWN. These partial
counters are not total effective-cost or monetary savings. Shared development,
audit and infrastructure costs are not amortized to zero.

No additional native call was made for adapter recovery. User-authorized V3
manifest SHA256:`6c037c7648a66b60eea973699c092b7370bc63bf44a27aade8cf1ab66931f435`.
See `LUNA_ACK_OUTPUT_V3_RESULT.json`, `native_luna_ack_output_v3.py`,
`luna_event_id_adapter.py`, `luna_ack_v3_audit.py`.
