# Astra kernel V1: mixed behavior, no economic release

OBSERVED: four fresh native Astra High streams completed, one original-base and
one kernel stream on each of two known prepared-review variants. Tools, task,
prepared evidence, skill, global AGENTS and reasoning effort were held constant
within each variant. Only the per-thread client base override differed.

| Variant | Input default → kernel | Input saving | Output default → kernel | Output saving | Uncached input saving |
|---|---:|---:|---:|---:|---:|
| Semantic defect | 90,226 → 56,827 | 37.02% | 946 → 917 | 3.07% | −6.96% |
| Valid implementation | 63,605 → 78,179 | −22.91% | 947 → 1,210 | −27.77% | −73.71% |

All costs include native reported reasoning output. The four calls consumed
288,837 input and 4,020 output tokens in total. Preparation, audit, recovery and
research costs are additional; these are not monetary or included-quota savings.
The two kernels were not installed globally. Sol's kernel remains untested.

## What actually changed

OBSERVED, defect: both bases rejected `pending[:16]`, executed 16/17/32-value
boundary probes, tested a stale-cursor case, and identified missing long-batch
checker coverage. Default regenerated hashes while reading snapshots; kernel did
not. Default used four segments/three commands, kernel three/two. This is evidence
for the intended mechanical-subtask removal on this bounded case. It does not
establish safe removal of whole Astra segments or an 80/80 policy.

OBSERVED, valid: default used three segments/two commands and accepted after source
and recorded-outcome inspection. Kernel used four/three and additionally exercised
four semantic cases: iteration-entry StopIteration, TypeError, ValueError, and
legacy-sequence failure after partial consumption, including stale-state/recovery.
All passed. Both returned ACCEPT with no unresolved obligations. Both justified
transactional buffering, exact-int validation, exception identity, list identity,
cursor synchronization, alias edits, and the contract's excluded concurrency and
resource-exhaustion domain. No claim of exhaustive capability parity follows.

INFERRED: the kernel can remove redundant mechanics without suppressing this known
semantic challenge, but can also increase semantic investigation. The new probes
must not simply be labeled waste and removed. Their adequacy contribution versus
their cost requires obligation-level analysis. Smaller base text did not ensure
fewer invocations or positive economics. No further prompt sampling is justified
by these two results alone.

## Integrity and limitations

Native terminal usage, every segment increment, thread/model/effort identity,
raw event hashes, identical prompt/skill attachment within pairs, prepared receipts
and bound input hashes were reconciled by `kernel_pair_audit.py`. Exact commands
and outputs were separately reviewed for the judgments above. No bound task files
changed. Inventory differences between arms consisted of caller-created skill
registry/snapshot files; neither visible command stream read prior thread state
from that database. Same-cwd/order/cache effects remain a limitation, not causal
equivalence proof. Hidden reasoning is not classified.

Important procedural failure: after the first successful defect rejection, the
harness rejected a structured assessment because its local check required a string.
The actual prompt did not require that type. Original STOPPED result and receipts
are preserved. A separately versioned amendment accepted a substantive object and
ran only the three previously unexecuted arms. No model call was retried. This
post-outcome harness amendment makes the experiment exploratory, not pristine
preregistered confirmation. Semantic outputs themselves were never repaired.

Local evidence: `research/native-astra-kernel-v1-20260909` under the Helix workspace.
`kernel-manifest.json`, `amendment.json`, original `kernel-results.json`, and
`amended-results.json` preserve the chronology. Public numerical/hash evidence is
in [BASE_KERNEL_PAIR_RESULT.json](BASE_KERNEL_PAIR_RESULT.json). Raw model requests
remain local. Hosted service-added instructions remain UNKNOWN; preflight verified
the client reads the configured file without an inference call.

## Decision

CONDITIONAL mechanical-delegation hypothesis survives; general Astra kernel
economic admission is **REJECTED for this V1 evidence**. No intelligence-loss claim
is warranted, and no intelligence-parity certification is warranted either.
80/80 remains unmet. Preserve the defect success and valid regression together.

Next user-directed work: audit Helix-native persistent memory and reducers against
Claude-Mem and RTK capabilities. Implement a gap only when it affects an observable
cost term and preserves exact recovery, semantic review and total-cost accounting.
Do not treat feature-count parity as usage savings or resume blind kernel tuning.
