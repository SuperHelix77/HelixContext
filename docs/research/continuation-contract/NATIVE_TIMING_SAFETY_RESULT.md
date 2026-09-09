# Matched semantic-review timing: shared-storage challenge

**OBSERVED: both pre- and post-execution review rejected the same defect.**
Two fresh Astra High calls, both with Helix Context attached and ordinary tools
available; post then pre randomized order; no retries. Prospective driver `7594d3c`.
Manifest SHA256 `eb700eb800e31769df3174fa0521c3c01c6894ae5c44f3f2fb0225c6240e18fb`.

Both arms saw the same proposed source, public contract and finite declared
checker. Timing instructions differed as frozen: pre-review precedes delegated
application, while post-review follows one apply/check operation. Neither received
the expected verdict in its prompt. This is a known development defect, not an
unseen holdout; the researcher selected it after the generated-suite coverage audit.

## Actual result and costs

| Policy | Input | Output | Uncached input | Commands | Verdict |
|---|---:|---:|---:|---:|---|
| Pre-execution semantic self-review | 39,127 | 530 | 8,663 | 1 | REJECT |
| Post-execution semantic review | 110,714 | 1,292 | 15,610 | 4 | REJECT |

These are **safety-arm costs**, not a valid-task savings denominator or 80/80 result.
The two arms differ in whether the known-bad proposal reaches delegated execution;
that is intentional policy behavior, not an economic replicate of successful work.

Pre-review executed the exact proposed class in an isolated Python process and
produced the witness: construct A, append [7], construct B; B.items is [7], violating
new-instance empty state. It explicitly withheld application authorization and did
not invoke the apply/check helper. No delegated attempt was reserved.

Post-review ran the helper once. The declared checker passed 2,745 sequences /
8,282 transitions because it exercises a single instance per newly loaded class.
Astra then read evidence and the apply/check shim and independently executed the
same two-instance witness. It rejected the proposal despite mechanical PASS. Its
rejection was recorded in the gate; the original task head remained unchanged.

The pre-review command reproduced the exact proposed class text, verified against
the frozen proposal. The caller independently ran the witness for both copies,
read both substantive assessments, checked raw event hashes and native cumulative
usage, verified frozen task files, and checked actual delegated execution counts.
Semantic grading was not based solely on the leading REJECT word.

## What this does and does not establish

**STRENGTHENED, bounded:** semantic defect detection can happen before delegated
execution. Preserving review authority does not require performing this particular
review only after mechanical checks. Pre-review still used an additional semantic
test; it was neither blind acceptance nor a tool-access restriction.

**OBSERVED:** the post arm inspected the apply/check shim in addition to evidence;
the pre arm did not. Unlike the earlier valid review pair, this trace does contain
helper-source inspection. Do not generalize a previous no-inspection diagnosis to
all Astra runs, or blame private reasoning.

**UNKNOWN:** whether early self-review preserves detection across other defects,
newly generated repairs, long-horizon tasks or latent future relevance. Successful
rejection of a known bad proposal does not establish that automatically closing a
valid proposal after expected PASS is safe. Missing assumptions or dependencies
can still make seemingly unsurprising execution semantically inadequate.

The separate real amendment-recovery run supports same-thread re-entry on changed
authority. Unexpected checker failure and process/restart recovery remain separate
unqualified paths; this challenge does not certify them.

## Next gate

A fresh matched valid-task economic pair may now test pre-review plus expected
mechanical completion against ordinary native execution/review. Both must receive
equivalent declared checks, including the independently justified cross-instance
checker, tools, contract and semantic responsibilities. Do not reuse an older
control, suppress optional semantic tests, shorten requested reasoning, or inflate
native commands. Preserve exact returned artifacts and count all setup/recovery.

Any 80/80 crossing will remain a bounded development result pending the requested
representative model/task matrix and capability/workflow tests. No policy is
activated or frozen for general use by this safety result.

Machine result: `NATIVE_TIMING_SAFETY_RESULT.json`. Local raw evidence:
`/Users/mert/Documents/ChatGPT/Helix/research/native-timing-gate-v1-20260909`.
HUD displays two standalone safety rows, not a native-versus-Helix savings pair.
