# Query-only witness reuse: short interface, failed scope gate

**Do not register or deploy this prototype.** Mechanical calibration passed;
the subsequent semantic-scope audit falsified the interface as described. No
native benchmark was launched and no live skill, kernel, profile or Engine route
changed. The 80/80 objective and capability-first release gates remain unachieved.

## Measured result

The previous Astra XHigh run generated a 2,456-byte tool payload containing a
2,265-byte Python witness. Reusing that exact program with five safely encoded
query literals reduces prospective arguments to 26 bytes. The native-tool schema
would add 553 bytes of input. Ordinary final answers remain model-written; this
proposal changes only an internal tool operation.

| Surface | Bytes | Local `o200k_base` proxy tokens |
|---|---:|---:|
| Observed native tool payload | 2,456 | 609 |
| Exact program within it | 2,265 | 509 |
| Prospective query arguments | 26 | 7 |
| Prospective tool schema | 553 | 110 |

These proxies are not hosted Astra counters. Input schema tokens and output
argument tokens are separate costs; subtracting their combined lengths from a
native task total would mix accounting boundaries. Tool framing, behavioral
response, repeated schema exposure and final-answer cost remain unmeasured.

Eighteen predeclared constructed cases matched their expected observations:
six query-specific defects, six valid candidates and six non-target queries.
They produced 54 expected defect observations, 162 total comparison rows and
162 passing whitespace controls. The original query reproduces the exact
model-written program and stdout bytes. Unicode, quotes and code-looking text
remain data; no query text executed. Ten boundary tests check stale authority,
duplicate/interrupted starts, literal structure, failure/malformed output and
timeout evidence retention. These are offline engineering checks, not model
capability replication.

Calibration took 1.6095 seconds; median case execution including binding/copy
work was 0.07965 seconds. Across cases the adapter copied 566,422 source bytes
and recorded 709,224 file bytes at its per-case accounting point. Exact programs,
requests, bindings, stdout/stderr and receipts are retained in a deduplicated
public evidence store. Full physical I/O, setup/research amortization and complete
model cost remain unknown. Coordinator research is additional usage, not free
because the number of native benchmark calls was zero.

## What the passing calibration missed

The original model-written witness used `unlisted_token` and an auxiliary record
containing `other evidence`. Its two corruption scenarios were described as
testing **nonmatching** auxiliary data. That claim was true for the original query.

Parameterizing the query preserves the program structure but can invalidate the
scenario's meaning. The [scope falsifier](SCOPE_AUDIT.json) uses the actual bound
reference implementation to establish:

| Query | Auxiliary matches legacy AND | Matches at least one literal-word query |
|---|---|---|
| `unlisted_token` | No | No |
| `other evidence` | Yes | Yes |
| `OTHÉR` | Yes | Yes |
| `unlisted other` | No | Yes |

The accent/case result also rules out a naive exact-word string guard. On the
last query, checking only legacy AND would miss the changed coverage under ANY.
The comparisons still execute and their reported equality counts are correct;
the **coverage label is overstated**. No model was exposed to this misleading
interface. We do not relabel this as an observed model intelligence regression.

A separate read-only source check establishes another blind spot: the program's
only `search` call passes `limit=1`. The known default-limit mutant differs from
the valid candidate only by changing the default from 10 to 9. That difference
cannot affect these explicitly limited calls. No additional model or probe run
was needed to discover this coverage gap.

**Conditional reuse rule:** fresh source hashes plus the same code structure do
not preserve a query-dependent coverage assumption. Reuse needs the relevant
preconditions checked for the actual parameter, or an accurately narrowed claim.
This is an observed counterexample to unguarded parameter substitution, not a
new general theorem about model cognition.

## Decision and next boundary

**REJECT as specified.** A future version must either verify and expose the
parameter-dependent matching conditions or rename/narrow the scenario claims.
It must state the explicit limit and corpus size, retain exact observations,
and leave other semantic probes available. Successful process execution must
never become a decision that the implementation is correct.

Even repairing scope would not admit an 80/80 benchmark by itself. In the prior
142,319-input / 2,343-output candidate, deleting the entire mixed probe segment
for free would remove only 25.34% of candidate input and 36.75% of candidate
output if all other counters stayed fixed. Actual reuse still needs query
selection, a tool call, receipt inspection and a normal final. This is optimistic
fixed-trajectory arithmetic, not an achievable saving or universal ceiling.

No unmatched historical control is substituted. The user goal requires complete
paired tasks and preserved capability/workflow; a 99% smaller argument string
cannot satisfy it. No further native call is authorized by this report. The next
admitted proposal must combine a valid responsibility boundary with a credible
whole-task cost case, rather than promote this attractive local reduction.

Evidence: [mechanical calibration](CALIBRATION.json), [scope audit](SCOPE_AUDIT.json),
[adjudicated result](RESULT.json), [boundary tests](TESTS.txt), and the retained
[artifact index](artifacts/INDEX.json). Earlier research sources and scope are in
[the preregistered design](DESIGN.md).
