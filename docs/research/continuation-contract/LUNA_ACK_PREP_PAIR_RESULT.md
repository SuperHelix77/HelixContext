# Luna High: one-shot passive ACK dispatch + caller preparation

OBSERVED: fresh same-model paired known W50 development episode, frozen driver
`2fd871e`, candidate first, zero retries. Both arms pass 49 exact ACKs, full exact
history preservation and the final authoritative-policy/amendment decision.

| Native metric | Persistent control | Helix | Savings |
|---|---:|---:|---:|
| Input tokens | 1,082,542 | 69,637 | 93.57% |
| Output tokens | 641 | 1,270 | **−98.13%** |
| Uncached input | 46,766 | 15,109 | 67.69% |
| Reasoning output (included above) | 169 | 618 | −265.68% |
| Native user turns | 50 | 1 | 98% |
| Model segments | 50 | 3 | 94% |

**Verdict: input mechanism survives on this bounded fixture; combined80/80 fails.
No production promotion, no retry, no general intelligence/workflow parity claim.**

## What was tested

The caller may durably acknowledge an exact trusted receipt-only request envelope.
It never infers passivity from event data. Unknown/additional/action-bearing fields
or requests return native fallback; duplicate IDs are refused. The preflight
checked49ACKs, reopen recovery, duplicate refusal and final/unknown/action fallback.
This is a research dispatcher, not general event classification or a crash-safe
production transaction system. Partial writes/concurrency remain unqualified.

At the final semantic request, caller preparation supplies **all49 exact event/ACK
records**, not selected evidence or an answer. Luna must interpret the policy,
amendment and untrusted vendor note. The input packet matches the recovered archive
exactly. Both final answers retain exact nonce, decimal string, large integer
string, required approver count and amended group, rejecting unauthorized rollback.

The fresh control uses one persistent native thread, not50fresh process launches.
This explicitly changes the old W50 contract requiring50nativecalls in both arms.
It is not a replication of that old protocol, nor50dependent semantic decisions.

## Why the optimistic output projection failed

OBSERVED: control passive turns cost391outputtokens total; its final semantic turn
cost250. Helix's final turn cost1270output, over five times that native final turn.
Its three native segments cost597,297,376outputtokens. The runtime reports618
reasoning-outputtokens, without causal attribution of their contents.

Visible candidate commentary announces local verification, reports an unavailable
memory helper and says it is registering the skill, despite caller preparation
and registration. Native events record two pre-tool hook completions but no
commandExecution completion items. Therefore actual command execution details
are UNKNOWN; **zero recorded command items is not zero tool work**. This observation
also exposes an observability gap in command-only HUD counters.

INFERRED: integration/continuity work remains a plausible avoidable cost.
This single pair does not isolate skill attachment, trust wording, hooks, history
format or model variation. It does not prove a prompt edit would eliminate that cost.
The earlier93.52/81.40 sensitivity retained an older candidate final cost and older
control denominator; those assumptions did not transfer to this fresh pair.
Even retaining this control's250-token final and deleting all391passive output
would save only60.998% output. That is conditional arithmetic, not a universal bound.

## Hidden costs and limits

Caller candidate dispatcher/recovery preparation measured0.01245seconds,472012
logical bytes read and35398bytes written (control archive path:18069read/35388write).
The candidate repeatedly scans its growing ledger for duplicates: roughly26times
the18.1KB passive archive across the counted path. It is small here but not free or
an efficient scalable index. Continuity storage55067bytes; raw native receipts
221550bytes, versus473284control. Session elapsed29.78seconds versus118.12seconds.

These byte counters cover the instrumented archive path, not physical SSD I/O,
all Python parsing, native tools/hooks/registry activity or audit/development costs.
Setup/index/recovery costs are not converted to equivalent tokens or zero dollars.
The93.57% total-input figure is cache-sensitive; it is not93.57% monetary savings.
No total effective-cost claim is qualified without prices and complete accounting.

Artifacts: `LUNA_ACK_PREP_PAIR_RESULT.json`, frozen `native_luna_ack_pair.py`,
`luna_ack_pair_audit.py`. Raw receipts remain under
`research/native-luna-ack-pair-v1-20260909` in the local Helix workspace.
Manifest SHA256: `9c72f7f8ba7667ce0b9511ddede980a258af1aa79689d09ec3007e28223adeac`.
Audit reconciles all53native segments,51turns,98ACKs, event hashes, usage totals,
exact full histories, prompt recovery and both final grades. No further native
experiment is launched under the one-shot authorization.
