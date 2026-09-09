# Astra receipt challenge: stopped before the paired control

**OBSERVED — STOPPED_EVALUATOR_CONTRACT_AMBIGUITY.** The prospectively randomized
order started with Helix valid. Exactly one native Astra High call ran; the frozen
driver stopped on its decision gate. The native control and both adverse arms
were not launched. No retries, altered denominator, retrospective passing grade,
Engine changes or budget amendments occurred.

| Native measurement | Helix valid arm |
|---|---:|
| Input | 81,365 |
| Cached input (subset) | 51,456 |
| Uncached input | 29,909 |
| Output | 1,377 |
| Reported reasoning (output subset) | 72 |
| Model segments | 4 |
| Issued commands | 3 |
| Elapsed seconds | 59.83 |
| Paired input/output saving | **UNKNOWN — no control** |

The raw wire and normalized event hashes match the terminal status. Exact final
native cumulative counters were independently re-read; cumulative updates were
not summed. Model output and independent adjudication are published alongside
this document. Preparation, offline checker audit and coordinator costs are
additional; this table is not the full research cost.

## What Astra actually did

1. Listed the task directory.
2. Re-read supplied contract/proposal and local checker/receipt/logs, hashing them.
3. Verified five receipt bindings, explicitly reused its limited successful
   mechanical execution, and generated new tests of unchecked semantic behavior.

It did not inspect Engine implementation or rerun the literal supplied mechanical
checker. Its additional tests covered bool/subclass rejection, rollback, exception
identity, single iteration, order, list identity and recovery. Some coverage overlaps
receipt predicates; the new semantic coverage cannot all be classified as waste.
No claim about hidden reasoning is needed or supported.

Astra then rejected the supplied proposal with this executable example:

```python
q = Queue()
alias = q.items
alias.extend([10, 20])
result = q.append_batch([30])  # returns 1; existing list contains 3 items
```

**OBSERVED:** independent reproduction returned 1, retained list identity, produced
`[10, 20, 30]`, and returned 1 again on an empty batch. The contract says cumulative
item count and does not exclude writes through the public alias between calls.

**INFERRED:** unconditional ACCEPT was not a defensible evaluator label under this
plausible contract reading. This is a specification/evaluator defect, not evidence
of reduced Astra intelligence. It would also be unjustified to claim that one
correctly raised ambiguity establishes general intelligence preservation.

A second evaluator defect is independent: the prompt requested an explanation
without specifying a string type, while the driver required a nonempty string.
Astra returned an explanatory object. Do not score that as a capability failure.
Both original artifacts and gate outcome remain unchanged. Any future correction
must use a new version and prospective freeze; this run must never become a
passing paired trial retroactively.

## Economic implication and stop

**OBSERVED:** segment input was 19,397 + 19,581 + 20,668 + 21,719 = 81,365.
The majority arrived after the first segment. Caller provision of a narrow
receipt did not eliminate discovery, binding checks, new tests or further turns.
It did preserve Astra's ability to challenge the expected answer.

**CONDITIONAL arithmetic:** if this candidate cost were unchanged, achieving 80%
savings would require a fresh control of at least 406,825 input and 6,885 output.
Both exceed the frozen per-call limits (150,000 / 4,000). Even at those control
limits, savings could be at most 45.76% input and 65.58% output. These are bounds
within this experiment's declared envelope, not model lower bounds or estimates
of an unrun control. Do not spend the remaining calls to chase 80/80 on this run.

**VERDICT:** narrow receipt reuse occurred, but the economic boundary is not
qualified and the fixture label was not valid enough to measure parity. Do not
respond by stripping semantic challenge or requiring trust in PASS. Do not simply
exclude alias mutation after seeing this result and call it an improvement.

The next design must separate read-only semantic review from mandatory application
validation, state its mutation model explicitly, and account for each remaining
model round. Any intended deterministic offload must cover precisely identified
mechanical work, leaving ambiguous requirements and new test semantics with Astra.
Freeze a typed output contract only if both arms receive it identically. No new
native calls or production architecture changes are part of this adjudication.
