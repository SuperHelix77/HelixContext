# Bound retrieval and Luna release status

**OBSERVED:** Two fully specified retrieval requests execute without inference,
preserving the original native-input bytes. **CONDITIONAL:** This is a strict
request-language implementation, not general natural-language or model parity.
No new hosted benchmark call was used. Coordinator/research usage is outside
these run receipts; no whole-project return-on-cost claim is made. Engine stays
active on semantic paths too.

| Task | Original bytes | Answer bytes | Local wrapper time | Model calls | Finite grader |
|---|---:|---:|---:|---:|---|
| Selection | 74,982 | 215 | 2.98 ms | 0 | PASS |
| Cold note recovery | 27,224 | 148 | 1.48 ms | 0 | PASS |

[The receipt](BOUND_RETRIEVAL_REPLAY_RESULT.json) pins source, answer, task state,
adapter, gate and runner. Times include ingestion, state preparation, store reopen,
dispatch, grading and receipt preparation, not a latency guarantee. Each source
is read by the wrapper and again by the store. Object counters exclude some
parsing/state-file/physical I/O/research costs. No monetary or quota claim follows
from zero model calls. Cold recovery uses a history snapshot, not forty new turns.

The retained native tasks used 57,216 input / 668 output and 83,946 input / 809
output. These are not new paired model runs. Engine JSON bytes are not native tokens.

## Authority correction

The low-level adapter recognized wording without representing inherited
constraints. Recognition alone was insufficient. The new
[bound gate](../../../engine/prototype/bound_retrieval.py) requires a caller-pinned
root binding task, source, adapter version and complete active constraints.

- Valid closed request with no inherited constraints: return deterministic answer.
- Prior constraints, unknown wording, extra requirements or unsupported schema:
  ordinary semantic execution inside Engine.
- Missing/stale authority, corrupt source or state changes during retrieval: hold
  for recovery and withhold the answer.

The caller must supply all applicable authority; hashes cannot prove completeness.
Source data supplies neither instructions nor executable callbacks. This is a
read-only operation; delivery still needs caller compare-and-swap on the returned
root. Normal Codex-app pre-inference integration remains unimplemented. Use the
bound gate, not the low-level research dispatcher, for future integrations.

21 tests pass, including inherited constraints, stale/mutated state, changed
task/source/version, duplicates, unknown requirements, malformed schemas, restart,
deleted originals, cold tamper, oversized integer parameters and exact Unicode /
whitespace / leading zeros. Included checks compare 100 varied selections with
SQLite and recover all 96 original packing tags. This is finite software evidence.

## Evidence lineage

[V1](RESOLVED_RETRIEVAL_REPLAY_RESULT.json) reserialized inputs: decoded strings
survived, but original file bytes were not archived. Do not call its smaller byte
counts original-source retention. [V2](RESOLVED_RETRIEVAL_ORIGINAL_SOURCE_RESULT.json)
uses original manifest-verified bytes. [Bound V1](BOUND_RETRIEVAL_REPLAY_RESULT.json)
adds authority checks. Older receipts remain unchanged. Only two parameterized
request grammars are supported; broader inference savings are unproven.

## Luna qualification

| Scope | Input saved | Output saved | Uncached saved | Evidence |
|---|---:|---:|---:|---|
| W50 selector | 98.28% | 88.73% | 81.59% | One adaptive candidate, retained control |
| Fresh coding V3 | 89.44% | 64.58% | 49.02% | One known pair; finite checks pass; 75/75 fails |
| Policy safety median | 49.64% | 54.41% | 10.41% | Three fresh development pairs |
| Original general suite median | 9.15% | −62.30% | 14.36% | Superseded policy; regressions retained |

**Broad Luna 75/75 remains open.** The favorable adaptive coding result did not
replicate. Identical candidate instructions produced different reported output.
Fresh coding's 1,152 reasoning tokens alone exceed the 967.75-token allowance for
75% saving against 3,871 control output tokens. Deleting all 219 remaining output
tokens yields at most 70.24% saving if reasoning stays fixed. This is a conditional
trace bound, not a universal floor or an account of hidden reasoning.

An unchanged retry measures variability, not a new mechanism. Do not disable
Engine, lower effort, suppress semantic checks or prewrite a fixture algorithm
to manufacture qualification. Compiled retrieval is excluded from model medians.

## HUD and accounting

Six explicit cohorts show N, input/output/uncached medians, ratio-of-totals, current short/long tariff-scenario medians, finite
checks and scope. Engine-only replay is separate. Finite checks require a pinned
audit and exact native-stream hash; unbound checks stay unknown.

Fixed omitted pricing for `CLOSED` sessions: metered failed attempts are also
charged. Fixed duplicate-control totals: the registered snapshot has 61 unique
verified threads and excludes 10 aliases. Parent chat and absent receipts remain
outside the boundary. Current tariff refresh/expiry stays active; tariff scenarios
are not included-plan quota estimates.

Caching unchanged native-trace parsing reduced local median warm scan time from
78.04 to 28.01 ms over ten scans, with zero extra logical file reads. Cold scan:
111.27 ms. Polling stays every two seconds, no inference. See
[measurement](HUD_SCOPED_REPORTING_MEASUREMENT.json). 24 HUD/pricing/statistics
tests pass; browser checks verified tables, filtering and no console errors.

## Next gate

Freeze W50 as a scoped candidate. Next justified inference: prospective paired
qualification of the frozen interface on varied continuations, changed authority
and recovery, charging every attempt. Coding/re-entry remain separately
unqualified. Sol and Astra may reuse deterministic infrastructure but cannot
inherit Luna's native results. No general release is declared.
