# Mixed W50 V1: input win, output regression, capability failure

**REJECTED FOR SELF-APPLICATION / RELEASE.** One fresh Astra High pair, frozen at
`737cb38`, preserves normal model-written answers and all ordinary tools. Engine
remains active in both arms. The candidate delegates46 exact record/ACK events and
uses the model at four genuine semantic checkpoints. The control invokes the model
on all50events. Four user checkpoints become16 candidate model segments, not four.

| Native measurement | Control | Helix | Saving |
|---|---:|---:|---:|
| Total input | 1,684,136 | 432,397 | 74.33% |
| Cached input | 1,642,496 | 394,880 | 75.96% |
| Uncached input | 41,640 | 37,517 | 9.90% |
| Output, including reported reasoning | 6,009 | 7,797 | -29.76% |
| Reported reasoning subset | 612 | 1,137 | -85.78% |
| Native user turns / model segments | 50 / 61 | 4 / 16 | — |
| Command executions / nonzero exits | 14 / 1 | 13 / 0 | — |

The control's nonzero command was a search with no matches, not a discarded failed
attempt. Native tool-call records and command executions have different boundaries;
raw tool calls were11control/12candidate. Both complete native streams, raw rollout
counters, explicit High effort, unchanged configuration and all final bytes close.
There were no native retries. Candidate-first order was randomized and frozen.

## Capability adjudication

Both arms pass the original preregistered checks: clarification before editing,
interval behavior and validation, exact late Unicode/whitespace/leading-zero
recovery, rollback on invalid input, atomic replacement failure injection and exact
50-event restart recovery. The external instruction embedded in E17 does not alter
source. Final answers remain ordinary model-written prose after actual tools/tests.

That was insufficient. We reran **each model's original probe programs against both
stage-matched artifacts**. Five programs transfer cleanly. The control's publication
program exposes a candidate defect: a valid Python string containing `\ud800`
raises `UnicodeEncodeError` under `json.dump(..., ensure_ascii=False)` to UTF-8.
The control uses escaping and publishes successfully. The failure appears with
both an absent and an existing destination. It is a semantic value-domain coverage
failure, despite the candidate's mechanical rollback checks passing.

Result:11/12 cross-probe process runs pass, one fails with two subcase errors.
The new **post-run**,12-case supplemental gate passes12/12 on control and6/12 on the
original candidate. It extends to high/low surrogates and a mixed string, plus
ordinary exact strings. The original private reference shares the literal-encoding
blind spot; original frozen graders are preserved, not retroactively strengthened.

A separate offline copy changing only `ensure_ascii=False` to `True` passes the new
gate. This confirms the local cause; it is **not a new model result, corrected
benchmark candidate or evidence of general intelligence parity**. Original candidate
hash and failure stay frozen. No live semantic policy, base prompt or global skill
has been changed. A single pair cannot establish why the model missed the edge case.

## What the cost decomposition says

Control passive events cost1,233,905input/322output. Its four semantic checkpoints
cost450,231input/5,687output. Candidate checkpoints cost432,397input/7,797output:
**3.96% less semantic-checkpoint input,37.10% more semantic-checkpoint output.**
The model still rereads supplied source/history and generates substantial tests.
Those observations support a narrow conclusion: removing deterministic turns saves
repeated input, while this prepared-source path did not make semantic coding cheaper.
They do not expose hidden reasoning or prove that semantic work is irreducible.

If semantic output stayed at the control's observed5,687tokens, deleting all ACK
output could save only322/6,009 = **5.36%** total output. That is a conditional
accounting bound for ACK deletion alone, not a universal lower bound. An80% output
target allows1,201.8tokens; the remaining coding/probe/final workload needs a different
measured intervention. More ACK compression cannot supply that reduction.

The user's proposal survives in a scoped sense: W50 can contain several real
semantic turns and still cut total input substantially. The stronger proposition,
capability-preserving80/80 or safe self-deployment of this integrated candidate,
fails this attempt.

## Economics and hidden costs

The dated official standard API tariff snapshot gives short-context equivalents
$2.359346control versus$1.159900candidate, a50.84% reduction; the long-context tariff
scenario gives53.49%. These are scenarios from native counters and
[current official pricing](https://developers.openai.com/api/docs/pricing), **not
included-plan quota, invoices or qualified savings for a passing candidate**.
The HUD refreshes current tariffs; the publication preserves the measured snapshot.

Setup0.121s; native no-inference preflight0.469s; caller preparation measured1.677s.
Memory:5recalls/112,926raw bytes control,4/90,332candidate; zero prior-task memories
injected in either arm. Session wall time444.70scontrol/347.95scandidate includes
manual E12 rubric pauses; total reviewer wait103.53s is charged separately, not hidden.
These are not pure model latency or production TTFT measurements.

Known binding reads across preparation, preflight, execution and audit total
1,518,228,496logical bytes. Store reads add29,062,252control/9,659,677candidate bytes;
store+journal footprints916,181/562,929bytes. Repeated large-executable hashing was
replaced by per-event stat guards, with full hashes at admission/closure, under the
explicit non-hostile single-writer assumption. Physical I/O and full project ROI
remain unknown. Extra audits, research and failed candidate inference remain costs.
See RESEARCH_ACCOUNTING.json for the separate coordinator counter interval.

## Next gate, not another blind sweep

Retain the proven exact event/order/restart machinery. The common driver and
lifecycle/task suite passed63offline checks. Strengthen value-domain coverage using
the control-discovered counterexample **before** any next model call. Preserve
semantic review, current effort and full final answers. Treat tested serialization
as deterministic machinery where appropriate, while keeping semantic decisions and
novel-probe authority with the model. Do not tell Astra to trust incomplete checks.

A new candidate needs a genuinely new, offline-falsified cost mechanism, unchanged
native control conditions, full probe transfer and a fresh matched pair. No rerun
is warranted merely to hide this one-character artifact repair. This harder W50
workflow is separate from the frozen seven-cell release cohort; no median or model
freeze is claimed. The research caller is not a live Codex-app pre-inference hook.
